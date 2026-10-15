"""Idempotent, explicitly named demo foundation. Never touches existing datasets."""

import argparse
import json
import secrets
import subprocess

PROJECT = "project-e8b1593d-009a-4822-abf"
REGION = "asia-southeast1"


def run(*args, input_text=None, check=True):
    result = subprocess.run(args, input=input_text, capture_output=True, text=True)
    if check and result.returncode:
        # Secret values are passed on stdin, never echoed or placed in shell commands.
        raise RuntimeError(f"{args[0]} {args[1]} failed: {result.stderr[:1500]}")
    return result


def gcloud(*args, **kwargs):
    return run("gcloud", *args, "--project", PROJECT, "--quiet", **kwargs)


def ensure_service_account(name):
    email = f"{name}@{PROJECT}.iam.gserviceaccount.com"
    if gcloud("iam", "service-accounts", "describe", email, check=False).returncode:
        gcloud("iam", "service-accounts", "create", name, "--display-name", name)
    return email


def grant(email, role, condition=None):
    gcloud(
        "projects",
        "add-iam-policy-binding",
        PROJECT,
        "--member",
        f"serviceAccount:{email}",
        "--role",
        role,
        "--condition",
        condition or "None",
    )


def ensure_secret(name):
    if gcloud("secrets", "describe", name, check=False).returncode:
        gcloud(
            "secrets",
            "create",
            name,
            "--replication-policy",
            "automatic",
            "--data-file",
            "-",
            input_text=secrets.token_urlsafe(48),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--foundation", action="store_true")
    args = parser.parse_args()
    if not args.foundation:
        parser.error("Specify --foundation to provision the approved named resources.")
    backend = ensure_service_account("agentic-bi-backend")
    frontend = ensure_service_account("agentic-bi-frontend")
    builder = ensure_service_account("agentic-bi-builder")
    print("Dedicated service accounts ready.")
    # No roles/run.builder or roles/aiplatform.user on this shared project.
    # The custom role permits prediction and API quota attribution only.
    role_id = "agenticBiModelInvoker"
    if gcloud("iam", "roles", "describe", role_id, check=False).returncode:
        gcloud(
            "iam",
            "roles",
            "create",
            role_id,
            "--title",
            "Agentic BI model invocation only",
            "--permissions",
            "aiplatform.endpoints.predict,serviceusage.services.use",
            "--stage",
            "GA",
        )
    grant(backend, f"projects/{PROJECT}/roles/{role_id}")
    # Job submission does not grant access to any dataset. The demo dataset's
    # reader ACL is assigned separately by the seed command.
    grant(backend, "roles/bigquery.jobUser")
    grant(
        backend,
        "roles/cloudsql.client",
        f'expression=resource.name=="projects/{PROJECT}/instances/agentic-bi-demo-pg"&&resource.service=="sqladmin.googleapis.com",title=agentic-bi-demo-sql',
    )
    condition = f'expression=resource.name=="projects/{PROJECT}/databases/agentic-bi-demo",title=agentic-bi-demo-firestore'
    grant(backend, "roles/datastore.user", condition)
    print("Scoped runtime and build permissions ready.")
    if gcloud(
        "artifacts", "repositories", "describe", "agentic-bi-demo", "--location", REGION, check=False
    ).returncode:
        gcloud(
            "artifacts",
            "repositories",
            "create",
            "agentic-bi-demo",
            "--repository-format",
            "docker",
            "--location",
            REGION,
        )
    gcloud(
        "artifacts",
        "repositories",
        "add-iam-policy-binding",
        "agentic-bi-demo",
        "--location",
        REGION,
        "--member",
        f"serviceAccount:{builder}",
        "--role",
        "roles/artifactregistry.writer",
    )
    bucket = f"gs://{PROJECT}-agentic-bi-build"
    if gcloud("storage", "buckets", "describe", bucket, check=False).returncode:
        gcloud("storage", "buckets", "create", bucket, "--location", REGION, "--uniform-bucket-level-access")
    gcloud(
        "storage",
        "buckets",
        "add-iam-policy-binding",
        bucket,
        "--member",
        f"serviceAccount:{builder}",
        "--role",
        "roles/storage.objectUser",
    )
    # Cloud Build validates staging/log bucket metadata before reading objects.
    # objectUser alone does not include storage.buckets.get.
    gcloud(
        "storage",
        "buckets",
        "add-iam-policy-binding",
        bucket,
        "--member",
        f"serviceAccount:{builder}",
        "--role",
        "roles/storage.legacyBucketReader",
    )
    if run("bq", "--project_id", PROJECT, "show", f"{PROJECT}:agentic_bi_demo", check=False).returncode:
        run(
            "bq",
            "--project_id",
            PROJECT,
            "--location",
            REGION,
            "mk",
            "--dataset",
            "--description",
            "Synthetic Agentic BI retail demo only",
            f"{PROJECT}:agentic_bi_demo",
        )
    for name in ["agentic-bi-guest-signing", "agentic-bi-postgres-reader", "agentic-bi-postgres-admin"]:
        ensure_secret(name)
        if name != "agentic-bi-postgres-admin":
            gcloud(
                "secrets",
                "add-iam-policy-binding",
                name,
                "--member",
                f"serviceAccount:{backend}",
                "--role",
                "roles/secretmanager.secretAccessor",
            )
    print(
        json.dumps(
            {
                "backend_service_account": backend,
                "frontend_service_account": frontend,
                "builder_service_account": builder,
                "dataset": "agentic_bi_demo",
                "region": REGION,
            }
        )
    )


if __name__ == "__main__":
    main()
