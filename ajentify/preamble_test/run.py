"""Drive a fixed waste-classification scenario through each preamble-test agent
and print the generated message stream so we can compare tool-preamble behaviour
across models.

Usage:
    python ajentify/preamble_test/run.py                     # all agents, all scenarios
    python ajentify/preamble_test/run.py --agent gpt_5_2     # one agent only
    python ajentify/preamble_test/run.py --scenario multi    # one scenario only

Contexts are created with ``ttl_days=1`` so they auto-expire — no cleanup needed.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


AJENTIFY_BASE_URL = "https://api.ajentify.com"
STAGE = "preamble-test"

AGENTS = ["gpt_5_2", "gpt_5_2_codex", "claude_sonnet_4_6", "claude_opus_4_6"]

SCENARIOS: dict[str, list[str]] = {
    "single": [
        "Hi, I have a plastic water bottle — which bin does it go in?",
    ],
    "multi": [
        "Hi, I've just finished a box of cereal — which bin does it go in?",
        "Yep, the soft-plastic liner is still inside the box.",
        "Thanks! What about the cereal box itself, where does that go?",
    ],
    "no_bin": [
        "Hi, I've got a tree branch — which bin does it go in?",
    ],
}


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _load_api_key() -> str:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        env = parent / ".env"
        if env.is_file():
            for line in env.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == "AJENTIFY_API_KEY":
                    v = v.strip()
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                        v = v[1:-1]
                    return v
    sys.exit("AJENTIFY_API_KEY not found in .env or environment.")


def _post(path: str, *, api_key: str, body: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        AJENTIFY_BASE_URL + path,
        data=json.dumps(body).encode("utf-8"),
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
        sys.exit(f"HTTP {exc.code} from {path}:\n{detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Network error calling {path}: {exc.reason}")


def _format_messages(messages: list[dict[str, Any]]) -> list[str]:
    lines = []
    for m in messages:
        if "type" in m and m["type"] == "tool_call":
            args = json.dumps(m.get("tool_input") or {}, ensure_ascii=False)
            lines.append(f"  [TOOL CALL ] {m.get('tool_name')}({args})")
        elif "type" in m and m["type"] == "tool_response":
            out = m.get("tool_output") or ""
            if len(out) > 200:
                out = out[:200] + "…"
            lines.append(f"  [TOOL RESP ] {out}")
        else:
            sender = m.get("sender", "?")
            text = (m.get("message") or "").strip()
            tag = "AI" if sender == "ai" else sender.upper()
            if text:
                lines.append(f"  [{tag}] {text}")
            else:
                lines.append(f"  [{tag}] <empty>")
    return lines


def _count_preamble_instances(messages: list[dict[str, Any]]) -> dict[str, int]:
    """Count how often an AI text message is immediately followed by a tool call
    (a "preamble + tool" pair) vs how often a tool call appears without a
    preceding AI text (a "naked tool"). Sequential tool calls inside a single
    assistant batch count as naked-after-the-first.
    """
    preambles = 0
    naked = 0
    last_ai_text_then_no_other = False
    for m in messages:
        if "type" in m and m["type"] == "tool_call":
            if last_ai_text_then_no_other:
                preambles += 1
            else:
                naked += 1
            last_ai_text_then_no_other = False
        elif "type" in m and m["type"] == "tool_response":
            last_ai_text_then_no_other = False
        else:
            sender = m.get("sender")
            text = (m.get("message") or "").strip()
            if sender == "ai" and text:
                last_ai_text_then_no_other = True
            else:
                last_ai_text_then_no_other = False
    total_tool_calls = preambles + naked
    return {
        "preamble_pairs": preambles,
        "naked_tool_calls": naked,
        "total_tool_calls": total_tool_calls,
    }


def run_scenario(*, api_key: str, agent: str, scenario_name: str, user_messages: list[str]) -> dict[str, Any]:
    print(f"\n{'═' * 80}")
    print(f"AGENT: {agent}    SCENARIO: {scenario_name}")
    print("═" * 80)

    ctx_resp = _post(
        "/context",
        api_key=api_key,
        body={
            "stage": STAGE,
            "agent": agent,
            "invoke_agent_message": False,
            "ttl_days": 1,
        },
    )
    context_id = ctx_resp["context_id"]
    initial = ctx_resp.get("messages") or []
    print(f"context_id: {context_id}    model_id: {ctx_resp.get('model_id')}")

    all_generated: list[dict[str, Any]] = list(initial)
    for i, user_msg in enumerate(user_messages, start=1):
        print()
        print(f"--- turn {i}: user → agent ---")
        print(f"  [HUMAN] {user_msg}")
        chat_resp = _post(
            "/chat",
            api_key=api_key,
            body={"context_id": context_id, "message": user_msg},
        )
        gen = chat_resp.get("generated_messages") or []
        all_generated.append({"sender": "human", "message": user_msg})
        all_generated.extend(gen)
        for line in _format_messages(gen):
            print(line)

    summary = _count_preamble_instances(all_generated)
    print()
    print("--- preamble metrics ---")
    print(f"  preamble pairs (AI-text → tool_call): {summary['preamble_pairs']}")
    print(f"  naked tool calls (no preceding AI text): {summary['naked_tool_calls']}")
    print(f"  total tool calls: {summary['total_tool_calls']}")
    return {
        "agent": agent,
        "scenario": scenario_name,
        "context_id": context_id,
        "model_id": ctx_resp.get("model_id"),
        **summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=AGENTS, action="append",
                        help="Restrict to a single agent (repeatable). Default: all four.")
    parser.add_argument("--scenario", choices=list(SCENARIOS), action="append",
                        help="Restrict to a single scenario (repeatable). Default: all.")
    args = parser.parse_args(argv)

    api_key = _load_api_key()
    agents = args.agent or AGENTS
    scenarios = args.scenario or list(SCENARIOS)

    results: list[dict[str, Any]] = []
    for agent in agents:
        for scenario_name in scenarios:
            results.append(run_scenario(
                api_key=api_key,
                agent=agent,
                scenario_name=scenario_name,
                user_messages=SCENARIOS[scenario_name],
            ))

    print("\n" + "═" * 80)
    print("SUMMARY")
    print("═" * 80)
    print(f"{'agent':<22}{'scenario':<10}{'preamble':>10}{'naked':>8}{'total':>8}")
    print("-" * 58)
    for r in results:
        print(
            f"{r['agent']:<22}{r['scenario']:<10}"
            f"{r['preamble_pairs']:>10}{r['naked_tool_calls']:>8}{r['total_tool_calls']:>8}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
