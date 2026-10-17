"""Verify managed TimesFM with the worker identity, without impersonation or IAM changes."""

import argparse
import base64
import json
import time
import uuid
from pathlib import Path

from provision import PROJECT, REGION, gcloud


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        required=True,
        help="Verified backend image digest containing the adapter.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    prefix = f"{REGION}-docker.pkg.dev/{PROJECT}/agentic-bi-demo/backend@sha256:"
    if not args.image.startswith(prefix) or len(args.image.removeprefix(prefix)) != 64:
        parser.error(
            "Use a verified digest from the dedicated backend image repository."
        )
    if not args.apply:
        print(
            json.dumps(
                {
                    "plan": "One temporary Cloud Run job; four bounded synthetic TimesFM queries; no analytical writes or IAM changes.",
                    "image": args.image,
                }
            )
        )
        return
    service = json.loads(
        gcloud(
            "run",
            "services",
            "describe",
            "agentic-bi-report-worker",
            "--region",
            REGION,
            "--format=json",
        ).stdout
    )
    identity = service["spec"]["template"]["spec"]["serviceAccountName"]
    expected = f"agentic-bi-report-worker@{PROJECT}.iam.gserviceaccount.com"
    if identity != expected:
        raise RuntimeError(
            "Worker identity differs from the dedicated runtime account; inspect before continuing."
        )
    job = "agentic-bi-timesfm-check-" + uuid.uuid4().hex[:8]
    source = base64.b64encode(
        Path("Backend/scripts/smoke_timesfm.py").read_bytes()
    ).decode()
    code = (
        "import asyncio,base64,json; from pathlib import Path; from types import SimpleNamespace; "
        f"scope={{'__name__':'timesfm_runtime_probe'}}; exec(base64.b64decode('{source}'),scope); "
        f"asyncio.run(scope['run'](SimpleNamespace(live=True,gcloud_credentials=False,impersonate='',project='{PROJECT}',location='{REGION}',output='/tmp/timesfm.json'))); "
        "result=json.loads(Path('/tmp/timesfm.json').read_text()); "
        f"result.update(identity='{identity}',credential_source='Cloud Run workload ADC',temporary_job='{job}',image='{args.image}'); "
        "print('AGENTIC_BI_TIMESFM_CHECK '+json.dumps(result),flush=True); "
        "raise SystemExit(0 if result['passed'] else 1)"
    )
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        gcloud(
            "run",
            "jobs",
            "create",
            job,
            "--region",
            REGION,
            "--image",
            args.image,
            "--service-account",
            identity,
            "--command",
            "python",
            f"--args=^~^-c~{code}",
            "--memory",
            "2Gi",
            "--cpu",
            "1",
            "--tasks",
            "1",
            "--max-retries",
            "0",
            "--task-timeout",
            "300s",
        )
        execution = gcloud(
            "run", "jobs", "execute", job, "--region", REGION, "--wait", check=False
        )
        result = None
        for _ in range(8):
            entries = json.loads(
                gcloud(
                    "logging",
                    "read",
                    f'resource.type="cloud_run_job" AND resource.labels.job_name="{job}" AND timestamp>="{started}"',
                    "--limit",
                    "80",
                    "--format=json",
                ).stdout
            )
            for entry in entries:
                line = entry.get("textPayload", "")
                if line.startswith("AGENTIC_BI_TIMESFM_CHECK "):
                    result = json.loads(line.split(" ", 1)[1])
                    break
            if result is not None:
                break
            time.sleep(5)
        if result is None:
            raise RuntimeError(
                "Runtime check produced no structured outcome. Inspect the temporary job's logs."
            )
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if execution.returncode or not result["passed"]:
            raise RuntimeError(
                "Worker TimesFM compatibility failed; keep feature flags disabled."
            )
    finally:
        gcloud("run", "jobs", "delete", job, "--region", REGION, check=False)


if __name__ == "__main__":
    main()
