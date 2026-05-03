"""Deploy the Pod Ajentify manifest to a stage.

Usage:
    python ajentify/deploy.py <stage> [--plan] [--manifest PATH] [--org-id ID]

Examples:
    python ajentify/deploy.py staging --plan      # dry-run via /deploy/plan
    python ajentify/deploy.py staging             # apply
    python ajentify/deploy.py production          # promote same manifest

The script loads the manifest at ``--manifest`` (default
``ajentify/ajentify.json``), inlines any ``prompt_file`` references on agents
and ``code_file`` references on tools (resolved relative to the manifest's
directory), strips those reference fields, and POSTs the resolved manifest to
the Ajentify deploy endpoint. ``AJENTIFY_API_KEY`` is read from the nearest
``.env`` (walking up from the manifest), or from the process environment.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


AJENTIFY_BASE_URL = "https://api.ajentify.com"


def _ssl_context() -> ssl.SSLContext:
    """Build an SSL context that works on macOS Python by preferring certifi
    when available. macOS framework Python does not ship with a usable system
    cert bundle, which causes ``CERTIFICATE_VERIFY_FAILED`` for HTTPS calls.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def find_dotenv(start: Path) -> Path | None:
    """Walk up from ``start`` looking for a ``.env`` file."""
    for directory in [start, *start.parents]:
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_dotenv(path: Path) -> dict[str, str]:
    """Minimal .env parser: ``KEY=VALUE`` lines, ``#`` comments, optional quotes."""
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        values[key] = val
    return values


def get_api_key(manifest_path: Path) -> str:
    key = os.environ.get("AJENTIFY_API_KEY")
    if key:
        return key
    dotenv_path = find_dotenv(manifest_path.parent)
    if dotenv_path is not None:
        env = load_dotenv(dotenv_path)
        key = env.get("AJENTIFY_API_KEY")
        if key:
            return key
    sys.exit(
        "AJENTIFY_API_KEY is not set. Add it to .env or export it before running."
    )


def inline_file_references(manifest: dict[str, Any], manifest_dir: Path) -> dict[str, Any]:
    """Resolve ``prompt_file`` (agents) and ``code_file`` (tools) into the
    server-recognised ``prompt`` / ``code`` fields, and strip the references.
    """

    def _read(rel_path: str, kind: str, owner: str) -> str:
        path = (manifest_dir / rel_path).resolve()
        if not path.is_file():
            sys.exit(
                f"{kind} for {owner!r} points to {rel_path!r} but {path} does not exist"
            )
        return path.read_text()

    for agent_name, agent in (manifest.get("agents") or {}).items():
        if "prompt_file" in agent:
            if agent.get("prompt"):
                sys.exit(
                    f"agent {agent_name!r} has both 'prompt' and 'prompt_file'; pick one"
                )
            agent["prompt"] = _read(agent["prompt_file"], "prompt_file", agent_name)
            del agent["prompt_file"]

    for tool_name, tool in (manifest.get("tools") or {}).items():
        if "code_file" in tool:
            if tool.get("code"):
                sys.exit(
                    f"tool {tool_name!r} has both 'code' and 'code_file'; pick one"
                )
            code = _read(tool["code_file"], "code_file", tool_name)
            # .py files conventionally end with a single newline; strip it so
            # the on-disk POSIX-friendly format matches the canonical tool
            # code (no trailing newline) the server stores. Keeps re-deploys
            # as noops when nothing meaningful has changed.
            if code.endswith("\n"):
                code = code[:-1]
            tool["code"] = code
            del tool["code_file"]

    return manifest


def post_deploy(
    *,
    api_key: str,
    stage: str,
    manifest: dict[str, Any],
    plan_only: bool,
    org_id: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"stage": stage, "manifest": manifest}
    if org_id:
        body["org_id"] = org_id

    endpoint = "/deploy/plan" if plan_only else "/deploy"
    url = AJENTIFY_BASE_URL + endpoint
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, context=_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        sys.exit(f"HTTP {exc.code} from {endpoint}:\n{detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Network error calling {url}: {exc.reason}")


def print_response(response: dict[str, Any], *, plan_only: bool) -> None:
    label = "PLAN" if plan_only else "DEPLOY"
    stage = response.get("stage_name")
    created = response.get("stage_created")
    summary = response.get("summary") or {}
    operations = response.get("operations") or []

    print(f"--- {label} ---")
    print(f"stage:         {stage}{' (newly created)' if created else ''}")
    print(
        "summary:       "
        + ", ".join(f"{k}={v}" for k, v in summary.items())
        if summary
        else "summary:       (none)"
    )
    print("operations:")
    if not operations:
        print("  (none)")
    else:
        for op in operations:
            kind = op.get("kind", "?")
            name = op.get("logical_name", "?")
            action = op.get("op", "?")
            rid = op.get("resource_id")
            suffix = f"  [{rid}]" if rid else ""
            print(f"  {action:<6} {kind:<6} {name}{suffix}")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    default_manifest = here / "ajentify.json"

    parser = argparse.ArgumentParser(description="Deploy the Pod Ajentify manifest.")
    parser.add_argument("stage", help="Target stage, e.g. 'staging' or 'production'.")
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Dry-run via POST /deploy/plan. No changes are applied.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
        help=f"Path to the manifest JSON (default: {default_manifest}).",
    )
    parser.add_argument(
        "--org-id",
        dest="org_id",
        default=None,
        help="Optional org_id; defaults to the API key's first org.",
    )
    args = parser.parse_args(argv)

    manifest_path: Path = args.manifest.resolve()
    if not manifest_path.is_file():
        sys.exit(f"Manifest not found: {manifest_path}")

    api_key = get_api_key(manifest_path)

    with manifest_path.open() as f:
        manifest = json.load(f)

    manifest = inline_file_references(manifest, manifest_path.parent)

    response = post_deploy(
        api_key=api_key,
        stage=args.stage,
        manifest=manifest,
        plan_only=args.plan,
        org_id=args.org_id,
    )
    print_response(response, plan_only=args.plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
