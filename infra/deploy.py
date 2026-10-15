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
    args = parser.parse_args()
    service = f"agentic-bi-{args.service}"
    folder = "Frontend" if args.service == "frontend" else "Backend"
    image = f"{REGION}-docker.pkg.dev/{PROJECT}/agentic-bi-demo/{args.service}:{int(time.time())}"
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
    subprocess.run(command, check=True)
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
        "run", "services", "describe", service, "--region", REGION, "--format", "value(status.url)"
    ).stdout.strip()
    print(json.dumps({"service": service, "url": url, "image": image}))


if __name__ == "__main__":
    main()
