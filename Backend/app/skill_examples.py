"""Stable seed IDs let operators add examples without replacing public edits."""

from app.skills import SkillContent, Skills

EXAMPLES = [
    (
        "monthly-revenue-review",
        {
            "name": "Monthly revenue review",
            "description": "Explain monthly revenue trends with explicit reporting assumptions.",
            "when_to_use": "Monthly revenue, sales trends, or comparisons across reporting months.",
            "source": "bigquery",
            "tags": ["revenue", "trends"],
            "instructions": "## Purpose\nReview revenue trends.\n\n## Workflow\nUse completed-order gross revenue before refunds unless the visitor explicitly requests another supported definition. Aggregate at order grain, preserve follow-up filters, label months chronologically, and state the date range and USD units.\n\n## Business definitions\nGross revenue is before refunds. A month is a calendar month.\n\n## Examples\nShow monthly revenue as a line chart. Explain the largest observed monthly change without inventing causes.",
        },
    ),
    (
        "regional-target-review",
        {
            "name": "Regional target review",
            "description": "Compare regional actual revenue and targets at compatible grains.",
            "when_to_use": "Regional targets, attainment, revenue gaps, or actual-versus-target questions.",
            "source": "all",
            "tags": ["targets", "cross-source"],
            "instructions": "## Purpose\nCompare actual revenue with regional targets.\n\n## Workflow\nUse the same reporting window in both sources. Join on month and region when month is retained, or aggregate both sides to region first. Explain unmatched keys and inferred relationships.\n\n## Business definitions\nAttainment percent is 100 times actual revenue divided by target revenue; handle zero targets explicitly.\n\n## Examples\nCompare regional revenue with targets, showing actuals and targets side by side.",
        },
    ),
]


async def seed_examples(repo, settings):
    skills = Skills(repo, settings)
    for skill_id, value in EXAMPLES:
        await skills.mutate("administrator", skill_id=skill_id, content=SkillContent(**value), seed=True)
    return len(EXAMPLES)
