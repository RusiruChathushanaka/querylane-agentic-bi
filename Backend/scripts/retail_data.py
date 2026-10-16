"""Generate, reconcile, and upload the expanded synthetic retail history."""

import argparse
import asyncio
import json
import os
from datetime import date
from pathlib import Path

from app.retail_generator import GeneratorConfig, generate, read_manifest
from app.retail_validation import validate_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("generate", help="Offline: stream a new deterministic Parquet bundle")
    create.add_argument("--output", type=Path, required=True)
    create.add_argument("--start", type=date.fromisoformat, default=date(2023, 1, 1))
    create.add_argument("--end", type=date.fromisoformat, default=date(2026, 9, 30))
    for name, default in (
        ("orders-per-day", 300),
        ("customers", 25000),
        ("products", 200),
        ("stores", 24),
        ("seed", 42),
    ):
        create.add_argument(f"--{name}", type=int, default=default)
    extend = commands.add_parser(
        "extend",
        help="Regenerate the same history through a later as-of end; uploads insert only new records",
    )
    extend.add_argument("--from-bundle", type=Path, required=True)
    extend.add_argument("--end", type=date.fromisoformat, required=True)
    extend.add_argument("--output", type=Path, required=True)
    for name in ("validate", "upload"):
        command = commands.add_parser(name)
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--report", type=Path)
        if name == "upload":
            command.add_argument(
                "--apply",
                action="store_true",
                help="Without this flag only a local plan is produced; no credentials or database access",
            )
            command.add_argument("--target", choices=("cloud", "postgres-local"), default="cloud")
    args = parser.parse_args()
    try:
        if args.command in ("generate", "extend"):
            if args.command == "extend":
                old = read_manifest(args.from_bundle)
                values = old["parameters"] | {"end": str(args.end)}
                if args.end < date.fromisoformat(old["parameters"]["end"]):
                    raise ValueError("An extension cannot move the as-of end backward.")
                config = GeneratorConfig(
                    **{k: date.fromisoformat(v) if k in ("start", "end") else v for k, v in values.items()}
                )
            else:
                config = GeneratorConfig(
                    **{k: getattr(args, k) for k in GeneratorConfig.__dataclass_fields__}
                )
            result = generate(config, args.output, progress=lambda s: print(s, flush=True))
            print(
                json.dumps(
                    {
                        "bundle": str(args.output),
                        "version": result["version"],
                        "tables": {n: f["rows"] for n, f in result["files"].items()},
                    },
                    indent=2,
                )
            )
            return
        if args.command == "validate":
            result = validate_bundle(args.bundle)
        else:
            from app.retail_upload import postgres_connection, upload_cloud, upload_plan, upload_postgres

            result = upload_plan(args.bundle)
            if args.apply:
                if args.target == "cloud":
                    result = asyncio.run(upload_cloud(args.bundle, progress=lambda s: print(s, flush=True)))
                else:
                    dsn = os.environ.get("RETAIL_POSTGRES_ADMIN_DSN")
                    if not dsn:
                        raise ValueError(
                            "Set RETAIL_POSTGRES_ADMIN_DSN for the local PostgreSQL target; credentials are never CLI arguments."
                        )
                    validation = validate_bundle(args.bundle)
                    if not validation["passed"]:
                        raise ValueError("Bundle validation failed; no upload attempted.")

                    async def local():
                        async with postgres_connection(None, local_dsn=dsn) as connection:
                            return await upload_postgres(
                                connection, args.bundle, read_manifest(args.bundle, False), grant_reader=False
                            )

                    result = {"postgres": asyncio.run(local()), "status": "ready", "target": "postgres-local"}
            else:
                result["dry_run"] = True
                result["requested_target"] = args.target
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, indent=2, default=str) + "\n")
        print(json.dumps(result, indent=2, default=str))
        if result.get("passed") is False:
            raise SystemExit(1)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
