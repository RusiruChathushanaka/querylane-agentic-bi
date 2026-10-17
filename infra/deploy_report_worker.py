"""Prepare or deploy ONLY the private report worker. Foundation/IAM are separate operator actions.

Default prints a reviewable plan and performs no cloud reads or writes. --apply is a release operation.
"""

import argparse
import json
import tempfile
from pathlib import Path

from provision import PROJECT, REGION, gcloud
from runtime_settings import preserve_analysis_settings


def configuration(profile, frontend_url, existing=None):
    return preserve_analysis_settings({
        "ENVIRONMENT": "production",
        "STORAGE_BACKEND": "firestore",
        "DATA_BACKEND": "cloud",
        "AI_BACKEND": "gemini",
        "DATA_PROFILE": profile,
        "SOURCE_ROW_LIMIT": "30000" if profile == "timeseries" else "10000",
        "GOOGLE_CLOUD_PROJECT": PROJECT,
        "FIRESTORE_DATABASE": "agentic-bi-demo",
        "BIGQUERY_DATASET": "agentic_bi_demo",
        "BIGQUERY_LOCATION": REGION,
        "CLOUD_SQL_INSTANCE": f"{PROJECT}:{REGION}:agentic-bi-demo-pg",
        "ALLOWED_ORIGINS": frontend_url,
        "TEXT_MODEL": "gemini-3.8-flash",
        "TEXT_MODEL_LOCATION": "global",
        "APP_MODULE": "app.report_worker:app",
        "REPORTS_ENABLED": "false",
        "REPORT_DISPATCH": "cloud_tasks",
        "REPORT_REGION": REGION,
        "REPORT_QUEUE": "agentic-bi-reports",
        "REPORT_BUCKET": f"{PROJECT}-agentic-bi-reports",
        "REPORT_DISPATCH_SERVICE_ACCOUNT": f"agentic-bi-report-dispatch@{PROJECT}.iam.gserviceaccount.com",
        "REPORT_RESEARCH_ENABLED": "false",
    }, existing or {})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        required=True,
        help="Verified backend image built by the existing Cloud Build helper",
    )
    parser.add_argument("--frontend-url", required=True)
    parser.add_argument(
        "--data-profile", choices=["legacy", "timeseries"], required=True
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    env = configuration(args.data_profile, args.frontend_url)
    if not args.apply:
        print(
            json.dumps(
                {
                    "service": "agentic-bi-report-worker",
                    "image": args.image,
                    "region": REGION,
                    "private": True,
                    "runtime_identity": f"agentic-bi-report-worker@{PROJECT}.iam.gserviceaccount.com",
                    "environment": env,
                    "timeout_seconds": 660,
                    "concurrency": 1,
                    "max_instances": 2,
                    "requirements": [
                        "Dedicated worker/dispatch identities and scoped IAM",
                        "Private export bucket",
                        "Cloud Tasks queue",
                        "Private OIDC scheduler reconciliation",
                        "Enable public API dispatch only after worker verification",
                    ],
                    "note": "No deployment, IAM, seeding, or cloud data writes performed.",
                },
                indent=2,
            )
        )
        return
    if not args.image.startswith(
        f"{REGION}-docker.pkg.dev/{PROJECT}/agentic-bi-demo/backend:"
    ) and not args.image.startswith(
        f"{REGION}-docker.pkg.dev/{PROJECT}/agentic-bi-demo/backend@sha256:"
    ):
        parser.error("Use a verified backend image from the dedicated demo repository.")
    current = gcloud("run", "services", "describe", "agentic-bi-report-worker",
                     "--region", REGION, "--format", "json", check=False)
    if current.returncode == 0:
        existing = {entry["name"]: entry["value"] for entry in
                    json.loads(current.stdout)["spec"]["template"]["spec"]["containers"][0].get("env", [])
                    if "value" in entry}
        env = configuration(args.data_profile, args.frontend_url, existing)
    elif "NOT_FOUND" not in current.stderr.upper():
        parser.error("Cannot inspect worker configuration. Resolve the read error before deployment.")
    # Bootstrap privately with reports disabled, discover its real URL, then enable dispatch.
    with tempfile.TemporaryDirectory(prefix="querylane-report-release-") as directory:
        config = Path(directory) / "worker.json"
        config.write_text(json.dumps(env))
        gcloud(
            "run",
            "deploy",
            "agentic-bi-report-worker",
            "--image",
            args.image,
            "--region",
            REGION,
            "--service-account",
            f"agentic-bi-report-worker@{PROJECT}.iam.gserviceaccount.com",
            "--no-allow-unauthenticated",
            "--port",
            "8080",
            "--timeout",
            "660",
            "--concurrency",
            "1",
            "--max-instances",
            "2",
            "--min-instances",
            "0",
            "--cpu",
            "2",
            "--memory",
            "2Gi",
            "--env-vars-file",
            str(config),
            "--set-secrets",
            "GUEST_SIGNING_KEY=agentic-bi-guest-signing:latest,POSTGRES_PASSWORD=agentic-bi-postgres-reader:latest",
        )
    url = gcloud(
        "run",
        "services",
        "describe",
        "agentic-bi-report-worker",
        "--region",
        REGION,
        "--format",
        "value(status.url)",
    ).stdout.strip()
    gcloud(
        "run",
        "services",
        "update",
        "agentic-bi-report-worker",
        "--region",
        REGION,
        "--update-env-vars",
        f"REPORTS_ENABLED=true,REPORT_WORKER_URL={url}",
    )
    print(
        json.dumps(
            {
                "worker_url": url,
                "image": args.image,
                "data_profile": args.data_profile,
                "next": "Verify private task dispatch, then configure the public API using infra/deploy.py report options.",
            }
        )
    )


if __name__ == "__main__":
    main()
