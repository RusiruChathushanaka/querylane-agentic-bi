"""Exercise actual card handlers under all source preferences without real API/model calls."""

import argparse
import json
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

p = argparse.ArgumentParser(
    description="Local browser regression for sample-card source selection; all API traffic is intercepted."
)
p.add_argument("--frontend", default="http://localhost:3013")
p.add_argument(
    "--output", type=Path, default=Path("/tmp/querylane-workspace-samples.json")
)
args = p.parse_args()
assert urlparse(args.frontend).hostname in {"localhost", "127.0.0.1"}, (
    "Use a local frontend only."
)
S = "querylane-sample-source-regression"
F = args.frontend.rstrip("/")
B = F + "/sample-probe"


def ab(*args):
    p = subprocess.run(
        ["agent-browser", "--session", S, "--json", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(p.stdout)["data"]


def ev(js):
    return ab("eval", js)["result"]


ab("open", "about:blank")
ab("set", "viewport", "1600", "1200")
chat = {
    "id": "a" * 32,
    "source": "postgres",
    "title": "Local sample test",
    "skill_ids": [],
    "active_run": None,
}
fixtures = {
    "**/api/config": {"backend_url": B},
    "**/sample-probe/api/v1/connections": {
        "mode": "cloud",
        "period": "DAILY · MULTI-YEAR",
        "connections": [],
    },
    "**/sample-probe/api/v1/conversations": {"conversations": [], **chat},
    "**/sample-probe/api/v1/conversations/" + "a" * 32: {
        "conversation": chat,
        "messages": [],
    },
    "**/sample-probe/api/v1/guest-sessions": {
        "token": "local-browser-test-only",
        "expires_in": 3600,
    },
    "**/sample-probe/api/v1/reports/config": {"enabled": True},
    "**/sample-probe/api/v1/reports?conversation_id=*": {"reports": []},
    "**/sample-probe/api/v1/skills": {"skills": []},
    "**/sample-probe/api/v1/conversations/" + "a" * 32 + "/turns": {"run_id": "test"},
}
for path, body in fixtures.items():
    ab("network", "route", path, "--body", json.dumps(body))
ab(
    "network",
    "route",
    "**/sample-probe/api/v1/runs/test/events*",
    "--body",
    "event: complete\ndata: {}\n\n",
)
ab("open", F + "/app")
ev(
    "localStorage.setItem('querylane-preferences-v1',JSON.stringify({defaultSource:'postgres'}))"
)
results = []
for default in ["postgres", "bigquery", "all"]:
    ev(
        "localStorage.setItem('querylane-preferences-v1',JSON.stringify({defaultSource:"
        + json.dumps(default)
        + "}))"
    )
    for index, (name, expected) in enumerate(
        [
            ("See the bigger picture", "bigquery"),
            ("Actuals meet ambition", "all"),
            ("Know your customers", "all"),
            ("Find what sells", "bigquery"),
            ("Manual question", default),
        ]
    ):
        ab("open", F + "/app")
        ab("wait", ".suggestion-card:not(:disabled)")
        ev(
            "window.__sampleStarts=[];const original=window.fetch;window.fetch=(u,o)=>{if(o?.method==='POST'&&String(u).endsWith('/api/v1/conversations'))window.__sampleStarts.push(JSON.parse(o.body));return original(u,o)}"
        )
        if index < 4:
            ab("click", f".suggestion-card:nth-child({index + 1})")
        else:
            ab("fill", "#question", "Local regression question")
            ab("click", 'button[aria-label="Send question"]')
        for _ in range(20):
            starts = ev("window.__sampleStarts")
            if starts:
                break
            time.sleep(0.1)
        unchanged = (
            ev(
                "JSON.parse(localStorage.getItem('querylane-preferences-v1')).defaultSource"
            )
            == default
        )
        result = {
            "default": default,
            "card": name,
            "expected": expected,
            "actual": starts[0]["source"] if starts else None,
            "saved_preference_preserved": unchanged,
        }
        result["passed"] = result["actual"] == expected and unchanged
        results.append(result)
ab("open", F + "/app")
ab("wait", ".suggestion-card:not(:disabled)")
for width in [320, 390, 768, 1280]:
    ab("set", "viewport", str(width), "960")
    layout = ev(
        "({width:innerWidth,cards:document.querySelectorAll('.suggestion-card').length,"
        "overflow:document.documentElement.scrollWidth>innerWidth+1})"
    )
    results.append(
        {"layout": layout, "passed": layout["cards"] == 4 and not layout["overflow"]}
    )
# Wait for the welcome reveal before settled contrast assertions.
ab("wait", "700")
accessibility = ab("a11y", "--selector", ".suggestion-grid")
results.append(
    {
        "accessibility": accessibility["counts"],
        "violations": accessibility["violations"],
        "passed": accessibility["counts"]["violations"] == 0,
    }
)
print(json.dumps(results, indent=2))
args.output.write_text(json.dumps(results, indent=2) + "\n")
ab("close")
raise SystemExit(0 if all(r["passed"] for r in results) else 1)
