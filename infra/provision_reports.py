"""Scoped report foundation. Default is a local-only plan; --apply changes demo resources.

Run using Backend/.venv/bin/python. Stages separate foundation, private invocation,
and scheduling so OIDC dispatch can be verified before reconciliation is scheduled.
"""

import argparse
import json
import sys
from pathlib import Path

from provision import PROJECT, REGION, gcloud

WORKER = f"agentic-bi-report-worker@{PROJECT}.iam.gserviceaccount.com"
BACKEND = f"agentic-bi-backend@{PROJECT}.iam.gserviceaccount.com"
DISPATCH = f"agentic-bi-report-dispatch@{PROJECT}.iam.gserviceaccount.com"
BUCKET = f"gs://{PROJECT}-agentic-bi-reports"


def missing(*args):
    result = gcloud(*args, "--format=json", check=False)
    if result.returncode == 0:
        return False
    if any(marker in result.stderr.lower() for marker in ("not_found", "not found", "does not exist")):
        return True
    raise RuntimeError(result.stderr[:1000])


def binding(prefix, member, role):
    gcloud(*prefix, "--member", f"serviceAccount:{member}", "--role", role)


def foundation():
    for name in ("agentic-bi-report-worker", "agentic-bi-report-dispatch"):
        email = f"{name}@{PROJECT}.iam.gserviceaccount.com"
        if missing("iam", "service-accounts", "describe", email):
            gcloud("iam", "service-accounts", "create", name, "--display-name", name)
    role = json.loads(gcloud("iam", "roles", "describe", "agenticBiModelInvoker", "--format=json").stdout)
    if set(role["includedPermissions"]) != {"aiplatform.endpoints.predict", "serviceusage.services.use"}:
        raise RuntimeError("Prediction role permissions changed; review before granting it.")
    for role_name, condition in (
        (f"projects/{PROJECT}/roles/agenticBiModelInvoker", "None"),
        ("roles/bigquery.jobUser", "None"),
        (
            "roles/datastore.user",
            f'expression=resource.name=="projects/{PROJECT}/databases/agentic-bi-demo",title=agentic-bi-demo-firestore',
        ),
        (
            "roles/cloudsql.client",
            f'expression=resource.name=="projects/{PROJECT}/instances/agentic-bi-demo-pg"&&resource.service=="sqladmin.googleapis.com",title=agentic-bi-demo-sql',
        ),
    ):
        binding(("projects", "add-iam-policy-binding", PROJECT, "--condition", condition), WORKER, role_name)
    for secret in ("agentic-bi-guest-signing", "agentic-bi-postgres-reader"):
        binding(("secrets", "add-iam-policy-binding", secret), WORKER, "roles/secretmanager.secretAccessor")
    if missing("storage", "buckets", "describe", BUCKET):
        gcloud(
            "storage",
            "buckets",
            "create",
            BUCKET,
            "--location",
            REGION,
            "--uniform-bucket-level-access",
            "--public-access-prevention",
        )
    else:
        metadata = json.loads(gcloud("storage", "buckets", "describe", BUCKET, "--format=json").stdout)
        if metadata.get("public_access_prevention") != "enforced" or not metadata.get(
            "uniform_bucket_level_access"
        ):
            raise RuntimeError("Existing report bucket must enforce uniform/private access.")
    for member, role_name in (
        (WORKER, "roles/storage.objectCreator"),
        (WORKER, "roles/storage.objectViewer"),
        (BACKEND, "roles/storage.objectViewer"),
    ):
        binding(("storage", "buckets", "add-iam-policy-binding", BUCKET), member, role_name)
    queue_args = (
        "--location",
        REGION,
        "--max-concurrent-dispatches",
        "2",
        "--max-dispatches-per-second",
        "2",
        "--max-attempts",
        "3",
        "--min-backoff",
        "30s",
        "--max-backoff",
        "60s",
    )
    command = (
        "create"
        if missing("tasks", "queues", "describe", "agentic-bi-reports", "--location", REGION)
        else "update"
    )
    gcloud("tasks", "queues", command, "agentic-bi-reports", *queue_args)
    for member in (BACKEND, WORKER):
        binding(
            ("tasks", "queues", "add-iam-policy-binding", "agentic-bi-reports", "--location", REGION),
            member,
            "roles/cloudtasks.enqueuer",
        )
        binding(
            ("iam", "service-accounts", "add-iam-policy-binding", DISPATCH),
            member,
            "roles/iam.serviceAccountUser",
        )
    # Append only this reader; update_dataset uses the fetched etag to reject races.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Backend"))
    from google.cloud import bigquery

    from app.admin import operator_credentials

    with bigquery.Client(project=PROJECT, credentials=operator_credentials()) as client:
        dataset = client.get_dataset(f"{PROJECT}.agentic_bi_demo")
        reader = bigquery.AccessEntry("READER", "userByEmail", WORKER)
        if reader not in dataset.access_entries:
            dataset.access_entries = list(dataset.access_entries) + [reader]
            client.update_dataset(dataset, ["access_entries"])
    print("Dedicated report foundation ready; no source data or existing grants removed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["foundation", "invoker", "scheduler"], default="foundation")
    parser.add_argument("--worker-url")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.stage != "foundation" and (
        not args.worker_url or not args.worker_url.startswith("https://agentic-bi-report-worker-")
    ):
        parser.error("Supply the actual dedicated worker HTTPS URL.")
    if not args.apply:
        print(
            json.dumps(
                {
                    "project": PROJECT,
                    "region": REGION,
                    "stage": args.stage,
                    "identities": [WORKER, DISPATCH],
                    "worker": "agentic-bi-report-worker",
                    "bucket": BUCKET,
                    "queue": "agentic-bi-reports",
                    "worker_permissions": [
                        "existing prediction-only role",
                        "BigQuery jobUser plus demo-dataset READER",
                        "conditional named-demo Firestore/Cloud SQL access",
                        "two reader/runtime secrets",
                        "export objectCreator/objectViewer",
                        "queue enqueuer",
                        "actAs dispatch identity only",
                    ],
                    "backend_permissions": [
                        "export objectViewer",
                        "queue enqueuer",
                        "actAs dispatch identity only",
                    ],
                    "dispatch_permissions": ["invoker only on private worker"],
                    "scheduler": "private OIDC POST every minute; applied separately after OIDC verification",
                    "preserves": [
                        "existing IAM bindings/ACLs",
                        "larger timeseries dataset",
                        "all shared history and skills",
                    ],
                    "worker_url": args.worker_url,
                    "applied": False,
                },
                indent=2,
            )
        )
        return
    if args.stage == "foundation":
        foundation()
    elif args.stage == "invoker":
        binding(
            ("run", "services", "add-iam-policy-binding", "agentic-bi-report-worker", "--region", REGION),
            DISPATCH,
            "roles/run.invoker",
        )
    else:
        command = (
            "create"
            if missing("scheduler", "jobs", "describe", "agentic-bi-report-reconcile", "--location", REGION)
            else "update"
        )
        gcloud(
            "scheduler",
            "jobs",
            command,
            "http",
            "agentic-bi-report-reconcile",
            "--location",
            REGION,
            "--schedule",
            "* * * * *",
            "--time-zone",
            "Etc/UTC",
            "--http-method",
            "POST",
            "--uri",
            args.worker_url.rstrip("/") + "/internal/reports/reconcile",
            "--oidc-service-account-email",
            DISPATCH,
            "--oidc-token-audience",
            args.worker_url.rstrip("/"),
            "--headers",
            "Content-Type=application/json",
            "--message-body",
            "{}",
            "--attempt-deadline",
            "60s",
        )
        print("Private reconciliation schedule ready.")


if __name__ == "__main__":
    main()
