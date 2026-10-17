"""Build with a resource-scoped builder, then deploy as the current operator."""

import argparse
import json
import subprocess
import time
from pathlib import Path

from provision import PROJECT, REGION, gcloud


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=["frontend", "backend"], required=True)
    parser.add_argument("--backend-url")
    parser.add_argument("--frontend-url")
    parser.add_argument("--data-profile", choices=["legacy", "timeseries"], default=None)
    parser.add_argument("--reports-worker-url")
    parser.add_argument("--reports-bucket")
    parser.add_argument("--reports-dispatch-service-account")
    parser.add_argument("--image", help="Reuse an already built, verified image from this demo repository.")
    parser.add_argument("--build-only", action="store_true", help="Build without changing Cloud Run traffic/configuration.")
    args = parser.parse_args()
    if args.service == "backend" and not args.frontend_url:
        parser.error("--frontend-url is required for backend deployment.")
    if args.service == "frontend" and not args.backend_url:
        parser.error("--backend-url is required for frontend deployment.")
    existing_env = {}
    if args.service == "backend":
        flags = [
            args.reports_worker_url,
            args.reports_bucket,
            args.reports_dispatch_service_account,
        ]
        if any(flags) and not all(flags):
            parser.error("Supply all three --reports-* options together.")
        current = gcloud(
            "run",
            "services",
            "describe",
            "agentic-bi-backend",
            "--region",
            REGION,
            "--format",
            "json",
            check=False,
        )
        if current.returncode == 0:
            existing_env = {
                entry["name"]: entry["value"]
                for entry in json.loads(current.stdout)["spec"]["template"]["spec"]["containers"][0].get(
                    "env", []
                )
                if "value" in entry
            }
        elif "NOT_FOUND" not in current.stderr.upper():
            parser.error("Cannot inspect existing backend configuration; resolve the cloud read error first.")
        elif args.data_profile is None:
            parser.error("Cannot inspect the active profile. Supply --data-profile explicitly.")
        args.data_profile = args.data_profile or existing_env.get("DATA_PROFILE", "legacy")
    service = f"agentic-bi-{args.service}"
    folder = "Frontend" if args.service == "frontend" else "Backend"
    image_prefix = f"{REGION}-docker.pkg.dev/{PROJECT}/agentic-bi-demo/{args.service}"
    if args.image and not args.image.startswith((image_prefix + ":", image_prefix + "@sha256:")):
        parser.error("--image must reference this service in the dedicated demo image repository.")
    image = args.image or f"{image_prefix}:{int(time.time())}"
    builder = f"projects/{PROJECT}/serviceAccounts/agentic-bi-builder@{PROJECT}.iam.gserviceaccount.com"
    # The builder has no project-wide build/deploy role; only the dedicated
    # image repository and source/log bucket are writable by it.
    command = [
        "gcloud",
        "builds",
        "submit",
        ".",
        "--project",
        PROJECT,
        "--region",
        REGION,
        "--config",
        "infra/cloudbuild.yaml",
        "--service-account",
        builder,
        "--gcs-source-staging-dir",
        f"gs://{PROJECT}-agentic-bi-build/source",
        "--substitutions",
        f"_IMAGE={image},_DIRECTORY={folder}",
        "--quiet",
    ]
    if not args.image:
        subprocess.run(command, check=True)
    if args.build_only:
        print(json.dumps({"service": service, "image": image, "deployed": False}))
        return
    deploy = [
        "run",
        "deploy",
        service,
        "--image",
        image,
        "--region",
        REGION,
        "--service-account",
        f"{service}@{PROJECT}.iam.gserviceaccount.com",
        "--allow-unauthenticated",
        "--port",
        "8080",
        "--max-instances",
        "2",
        "--min-instances",
        "0",
    ]
    if args.service == "backend":
        if not args.frontend_url:
            parser.error(
                "--frontend-url must be the approved frontend origin (use localhost for first bootstrap)."
            )
        values = {
            "ENVIRONMENT": "production",
            "STORAGE_BACKEND": "firestore",
            "DATA_BACKEND": "cloud",
            "DATA_PROFILE": args.data_profile,
            "SOURCE_ROW_LIMIT": "30000" if args.data_profile == "timeseries" else "10000",
            "AI_BACKEND": "gemini",
            "GOOGLE_CLOUD_PROJECT": PROJECT,
            "FIRESTORE_DATABASE": "agentic-bi-demo",
            "BIGQUERY_DATASET": "agentic_bi_demo",
            "BIGQUERY_LOCATION": REGION,
            "CLOUD_SQL_INSTANCE": f"{PROJECT}:{REGION}:agentic-bi-demo-pg",
            "ALLOWED_ORIGINS": args.frontend_url,
            "TEXT_MODEL": "gemini-3.8-flash",
            "TEXT_MODEL_LOCATION": "global",
            "LIVE_MODEL": "gemini-live-2.5-flash-native-audio",
            "LIVE_MODEL_LOCATION": "us-central1",
        }
        # Preserve enabled report dispatch across later routine releases. New foundation is opt-in.
        values.update(
            {k: v for k, v in existing_env.items() if k.startswith("REPORT_") or k == "REPORTS_ENABLED"}
        )
        values.setdefault("REPORTS_ENABLED", "false")
        if args.reports_worker_url:
            values.update(
                REPORTS_ENABLED="true",
                REPORT_DISPATCH="cloud_tasks",
                REPORT_WORKER_URL=args.reports_worker_url,
                REPORT_BUCKET=args.reports_bucket,
                REPORT_DISPATCH_SERVICE_ACCOUNT=args.reports_dispatch_service_account,
                REPORT_REGION=REGION,
                REPORT_QUEUE="agentic-bi-reports",
            )
        # JSON is valid YAML. Configuration contains no secret values.
        config = Path("/tmp/agentic-bi-backend-env.json")
        config.write_text(json.dumps(values))
        deploy += [
            "--env-vars-file",
            str(config),
            "--set-secrets",
            "GUEST_SIGNING_KEY=agentic-bi-guest-signing:latest,POSTGRES_PASSWORD=agentic-bi-postgres-reader:latest",
            "--timeout",
            "3600",
            "--concurrency",
            "8",
            "--cpu",
            "1",
            "--memory",
            "2Gi",
            "--no-cpu-throttling",
        ]
    else:
        if not args.backend_url:
            parser.error("--backend-url is required for frontend deployment.")
        deploy += [
            "--set-env-vars",
            f"BACKEND_URL={args.backend_url}",
            "--memory",
            "512Mi",
            "--concurrency",
            "40",
        ]
    print(gcloud(*deploy).stdout)
    url = gcloud(
        "run",
        "services",
        "describe",
        service,
        "--region",
        REGION,
        "--format",
        "value(status.url)",
    ).stdout.strip()
    print(json.dumps({"service": service, "url": url, "image": image}))


if __name__ == "__main__":
    main()
