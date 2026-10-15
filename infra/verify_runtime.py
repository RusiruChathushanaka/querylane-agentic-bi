"""Run fixed checks with the attached backend identity; remove the check job afterward."""

import base64
import json
import tempfile
import time
from pathlib import Path

from provision import PROJECT, REGION, gcloud


def main():
    job = "agentic-bi-demo-check"
    service = json.loads(
        gcloud(
            "run", "services", "describe", "agentic-bi-backend", "--region", REGION, "--format=json"
        ).stdout
    )
    container = service["spec"]["template"]["spec"]["containers"][0]
    image = container["image"]
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="agentic-bi-runtime-env-", suffix=".json", delete=False
    ) as config:
        json.dump({item["name"]: item["value"] for item in container["env"] if "value" in item}, config)
    encoded = base64.b64encode(Path(__file__).with_name("runtime_check.py").read_bytes()).decode()
    code = f"exec(__import__('base64').b64decode('{encoded}'))"
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        gcloud(
            "run",
            "jobs",
            "deploy",
            job,
            "--region",
            REGION,
            "--image",
            image,
            "--service-account",
            f"agentic-bi-backend@{PROJECT}.iam.gserviceaccount.com",
            "--command",
            "python",
            f"--args=^~^-c~{code}",
            "--env-vars-file",
            config.name,
            "--set-secrets",
            "POSTGRES_PASSWORD=agentic-bi-postgres-reader:latest",
            "--memory",
            "2Gi",
            "--cpu",
            "1",
            "--max-retries",
            "0",
            "--task-timeout",
            "300s",
        )
        execution = gcloud("run", "jobs", "execute", job, "--region", REGION, "--wait", check=False)
        print(execution.stdout)
        result, logs = None, []
        for _ in range(6):
            logs = json.loads(
                gcloud(
                    "logging",
                    "read",
                    f'resource.type="cloud_run_job" AND resource.labels.job_name="{job}" AND timestamp>="{started}"',
                    "--limit",
                    "60",
                    "--format=json",
                ).stdout
            )
            result = next(
                (
                    json.loads(item["textPayload"].split("AGENTIC_BI_RUNTIME_CHECK ", 1)[1])
                    for item in logs
                    if item.get("textPayload", "").startswith("AGENTIC_BI_RUNTIME_CHECK ")
                ),
                None,
            )
            if result is not None:
                break
            time.sleep(5)
        if result is None:
            print(execution.stderr)
            print(json.dumps([item.get("textPayload", "") for item in logs], indent=2))
            raise RuntimeError("Runtime check produced no completion report.")
        Path("docs/evaluation/cloud-runtime.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if execution.returncode or not result["passed"]:
            raise RuntimeError("Runtime checks failed; inspect the report.")
    finally:
        gcloud("run", "jobs", "delete", job, "--region", REGION, check=False)
        Path(config.name).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
