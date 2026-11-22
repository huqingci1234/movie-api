from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Movie API", description="公开 TVBox 配置整理与授权媒体元数据接口", version="0.2.0")
ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "dist" / "tvbox.json"
QQ_GROUP = "956979768"

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Movie API"}

@app.get("/api/v1/announcement")
def announcement() -> dict[str, str]:
    return {"title": "官方交流群", "content": f"交流群 QQ：{QQ_GROUP}", "qq_group": QQ_GROUP}

@app.get("/api/v1/catalog")
def catalog() -> dict[str, Any]:
    return {"code": 0, "list": []}

@app.get("/api/v1/search")
def search(q: str = Query(..., min_length=1, max_length=100)) -> dict[str, Any]:
    return {"code": 0, "query": q, "list": []}

@app.get("/api/v1/detail/{vod_id}")
def detail(vod_id: str) -> dict[str, Any]:
    raise HTTPException(status_code=404, detail="影片不存在或尚未配置元数据源")

@app.get("/api/v1/play/{vod_id}")
def play(vod_id: str) -> dict[str, Any]:
    raise HTTPException(status_code=404, detail="暂无可用播放线路")

@app.get("/tvbox/config.json")
def tvbox_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise HTTPException(status_code=503, detail="配置尚未生成，请先运行 python tools/import_sources.py")
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
