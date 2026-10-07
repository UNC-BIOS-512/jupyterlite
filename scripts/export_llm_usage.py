#!/usr/bin/env python3
"""Export anonymous class LLM usage to data/llm_usage.csv.

Reads per-request spend logs from the class LiteLLM gateway and writes one
row per request. Students are replaced by a stable ID derived from a secret
salt (HMAC), so the ID can't be traced back to a GitHub username without the
salt, even by someone who has the class list. Times are cut to the hour.
No prompts, responses, keys, or request IDs are written.

Environment variables:
  LITELLM_URL         gateway base URL
  LITELLM_USAGE_KEY   view-only LiteLLM key (proxy_admin_viewer role)
  USAGE_ID_SALT       secret salt for student IDs; changing it renumbers everyone
  USAGE_EXCLUDE       optional comma-separated key aliases to leave out
"""

import argparse
import csv
import hashlib
import hmac
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "llm_usage.csv"
TZ = ZoneInfo("America/New_York")

# Test and service keys, never students.
ALWAYS_EXCLUDE_PREFIXES = ("zz-", "usage-export")

COLUMNS = [
    "student",
    "date",
    "hour",
    "weekday",
    "prompt_tokens",
    "cached_tokens",
    "completion_tokens",
    "cost_usd",
    "latency_s",
    "success",
]


def fetch_spend_logs(url, key):
    req = urllib.request.Request(
        f"{url.rstrip('/')}/spend/logs",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "bios512-usage-export"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def student_id(alias, salt):
    digest = hmac.new(salt.encode(), alias.lower().encode(), hashlib.sha256).hexdigest()
    return "s" + digest[:6]


def to_row(log, salt):
    meta = log.get("metadata") or {}
    usage = meta.get("usage_object") or {}
    details = usage.get("prompt_tokens_details") or {}
    start = parse_time(log["startTime"])
    end = parse_time(log["endTime"])
    local = start.astimezone(TZ)
    return {
        "student": student_id(meta["user_api_key_alias"], salt),
        "date": local.date().isoformat(),
        "hour": local.hour,
        "weekday": local.strftime("%a"),
        "prompt_tokens": log.get("prompt_tokens") or 0,
        "cached_tokens": details.get("cached_tokens") or 0,
        "completion_tokens": log.get("completion_tokens") or 0,
        "cost_usd": round(log.get("spend") or 0, 6),
        "latency_s": round((end - start).total_seconds(), 1),
        "success": (log.get("status") or "success") != "failure",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    salt = os.environ["USAGE_ID_SALT"]
    exclude = {a.strip().lower() for a in os.environ.get("USAGE_EXCLUDE", "").split(",") if a.strip()}

    rows = []
    for log in fetch_spend_logs(os.environ["LITELLM_URL"], os.environ["LITELLM_USAGE_KEY"]):
        alias = ((log.get("metadata") or {}).get("user_api_key_alias") or "").lower()
        if not alias or alias in exclude or alias.startswith(ALWAYS_EXCLUDE_PREFIXES):
            continue
        rows.append(to_row(log, salt))
    rows.sort(key=lambda r: (r["date"], r["hour"], r["student"]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows for {len({r['student'] for r in rows})} students to {args.out}")


if __name__ == "__main__":
    main()
