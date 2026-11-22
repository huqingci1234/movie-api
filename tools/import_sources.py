#!/usr/bin/env python3
"""Fetch public TVBox JSON configs and merge their sites into dist/tvbox.json."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "config" / "sources.json"
OUTPUT_FILE = ROOT / "dist" / "tvbox.json"
MAX_BYTES = 12 * 1024 * 1024
TIMEOUT = 25

def fetch_json(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
        raise ValueError(f"仅允许 HTTPS raw.githubusercontent.com 地址：{url}")
    request = Request(url, headers={"User-Agent": "movie-api-public-config-importer/0.2"})
    with urlopen(request, timeout=TIMEOUT) as response:
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError(f"配置超过 {MAX_BYTES} 字节：{url}")
    value = json.loads(body.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 根节点必须是对象：{url}")
    return value

def main() -> int:
    manifest = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    merged: dict = {}
    seen: set[str] = set()
    report: list[dict] = []
    for source in manifest.get("sources", []):
        url = source.get("url")
        if not url:
            continue
        try:
            data = fetch_json(url)
            added = 0
            for site in data.get("sites", []):
                if not isinstance(site, dict):
                    continue
                key = str(site.get("key") or site.get("api") or site.get("name") or "")
                if key and key not in seen:
                    seen.add(key)
                    merged.setdefault("sites", []).append(site)
                    added += 1
            for field in ("spider", "wallpaper", "logo", "parses", "lives", "homepage",
                          "warning", "rules", "ads", "doh", "headers"):
                if field not in merged and field in data:
                    merged[field] = data[field]
            report.append({"name": source.get("name", url), "status": "ok",
                           "sites_added": added, "source_sites": len(data.get("sites", []))})
        except (ValueError, HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            report.append({"name": source.get("name", url), "status": "failed", "error": str(exc)})
    merged["name"] = manifest.get("name", "Movie API")
    merged["notice"] = "交流群 QQ：956979768"
    merged["qq_group"] = "956979768"
    merged["import_report"] = report
    if not merged.get("sites"):
        print("没有成功导入任何站点；保留原文件不覆盖。", file=sys.stderr)
        return 1
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_FILE), "sites": len(merged["sites"]),
                      "report": report}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
