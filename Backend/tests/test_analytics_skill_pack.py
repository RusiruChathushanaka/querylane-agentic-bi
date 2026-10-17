"""The curated pack stays importable and cannot overwrite shared visitor revisions."""

from app.config import Settings
from app.repository import Repository
from app.skill_examples import analytics_examples, seed_analytics
from app.skills import Skills, export_skill, import_skill
from app.storage import MemoryStore


def test_analytics_pack_import_export_and_prediction_boundaries():
    examples = dict(analytics_examples())
    assert len(examples) == 12
    for skill_id, content in examples.items():
        assert skill_id.startswith(("analytics-", "prediction-"))
        assert import_skill(export_skill(content.model_dump())) == content
        assert len(content.instructions.encode("utf-8")) <= 16384
    forecasts = {key: value for key, value in examples.items() if key.startswith("prediction-")}
    assert len(forecasts) == 4
    for content in forecasts.values():
        assert "Advanced Analysis" in content.instructions
        assert "baseline" in content.instructions.lower()
    scenario = forecasts["prediction-driver-scenarios"].instructions
    assert "visitor-supplied" in scenario and "every forecast period" in scenario
    assert "not guaranteed lift" in scenario
    assert "unweighted mean" in examples["analytics-kpi-definitions"].instructions


async def test_reseeding_pack_preserves_edits_disabled_deleted_and_immutable_history():
    settings = Settings(environment="test")
    store = MemoryStore()
    repo = Repository(store, settings)
    skills = Skills(repo, settings)
    assert await seed_analytics(repo, settings) == 12
    original = await skills.get("prediction-sales-forecast", 1)
    await skills.mutate(
        "visitor",
        skill_id="prediction-sales-forecast",
        action="update",
        patch={"expected_revision": 1, "name": "Visitor forecast", "enabled": False},
    )
    await skills.mutate(
        "visitor",
        skill_id="analytics-seasonality",
        action="delete",
        patch={"expected_revision": 1},
    )
    before = await store.list("skills")
    assert await seed_analytics(repo, settings) == 12
    assert await store.list("skills") == before
    assert await skills.get("prediction-sales-forecast", 1) == original
    assert (await skills.get("prediction-sales-forecast"))["name"] == "Visitor forecast"
    assert not (await skills.get("prediction-sales-forecast"))["enabled"]
    assert (await skills.get("analytics-seasonality"))["deleted"]
    assert len(await skills.list()) == 11
