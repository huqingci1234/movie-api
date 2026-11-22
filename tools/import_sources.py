#!/usr/bin/env python3
"""Import public TVBox JSON configs and build one deduplicated subscription.

Only fetches explicitly configured HTTPS JSON URLs from raw.githubusercontent.com.
Review source repositories and licensing before adding them to config/sources.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "config" / "sources.json"
OUTPUT_FILE = ROOT / "dist" / "tvbox.json"
MAX_BYTES = 5 * 1024 * 1024
TIMEOUT = 15
USER_AGENT = "movie-api-config-builder/0.1"


def fetch_json(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
        raise ValueError(f"仅允许 HTTPS raw.githubusercontent.com 地址：{url}")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=TIMEOUT) as response:
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError(f"配置文件超过 {MAX_BYTES} 字节：{url}")
    data = json.loads(body.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON 根节点必须是对象：{url}")
    return data


def merge_config(url: str, sites: list, seen: set, report: list, depth: int = 0) -> None:
    if depth > 2:
        report.append({"url": url, "status": "skipped", "reason": "嵌套层级过深"})
        return
    try:
        data = fetch_json(url)
    except (ValueError, HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        report.append({"url": url, "status": "failed", "reason": str(exc)})
        return

    count_before = len(sites)
    for site in data.get("sites", []):
        if not isinstance(site, dict):
            continue
        api = site.get("api") or site.get("url")
        key = (str(site.get("key") or ""), str(api or ""))
        if api and key not in seen:
            seen.add(key)
            sites.append(site)

    # Multi-repository subscriptions commonly contain {urls:[{name,url}, ...]}.
    for child in data.get("urls", []):
        if isinstance(child, dict) and isinstance(child.get("url"), str):
            merge_config(child["url"], sites, seen, report, depth + 1)

    report.append({
        "url": url,
        "status": "ok",
        "sites_added": len(sites) - count_before,
    })


def main() -> int:
    if not SOURCE_FILE.exists():
        print(f"缺少配置文件：{SOURCE_FILE}", file=sys.stderr)
        return 2
    config = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    sources = config.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("config/sources.json 的 sources 必须是数组")

    sites: list = []
    seen: set = set()
    report: list = []
    for item in sources:
        if not isinstance(item, dict) or not item.get("url"):
            continue
        merge_config(str(item["url"]), sites, seen, report)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "name": config.get("name", "Movie API · 4K优先"),
        "sites": sites,
        "parses": config.get("parses", []),
        "flags": config.get("flags", []),
        "lives": config.get("lives", []),
        "ads": [],
    }
    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(OUTPUT_FILE.relative_to(ROOT)),
        "source_count": len(sources),
        "site_count": len(sites),
        "report": report,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
