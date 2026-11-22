from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Movie API",
    description="面向兼容影视客户端的授权影视元数据与播放源聚合接口",
    version="0.1.0",
)

APP_NAME = os.getenv("APP_NAME", "Movie API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.get("/api/v1/catalog")
def catalog() -> dict[str, Any]:
    # TODO: 从已启用且获授权的数据源汇总分类
    return {"code": 0, "list": []}


@app.get("/api/v1/search")
def search(q: str = Query(..., min_length=1, max_length=100)) -> dict[str, Any]:
    # TODO: 调用已启用的数据源适配器并统一结果格式
    return {"code": 0, "query": q, "list": []}


@app.get("/api/v1/detail/{vod_id}")
def detail(vod_id: str) -> dict[str, Any]:
    # TODO: 根据 vod_id 查询授权数据源
    raise HTTPException(status_code=404, detail="影片不存在或尚未配置数据源")


@app.get("/api/v1/play/{vod_id}")
def play(vod_id: str) -> dict[str, Any]:
    # TODO: 仅返回已授权播放源；不解析或绕过 DRM
    raise HTTPException(status_code=404, detail="暂无可用播放线路")


@app.get("/tvbox/config.json")
def tvbox_config() -> dict[str, Any]:
    # 通用配置模板；不同客户端字段可能存在差异，需在目标软件中验证
    base = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    return {
        "name": "Movie API",
        "api": f"{base}/api/v1",
        "version": "0.1.0",
        "description": "请先配置经授权的数据源",
    }
