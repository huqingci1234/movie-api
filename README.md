# Movie API

一个面向 TVBox、影视仓及兼容客户端的影视元数据与播放源聚合 API，优先识别并标注 2160P/4K 资源。

> 本项目只提供接口框架。请仅接入你拥有版权、获得授权或其服务条款明确允许调用的内容源；不内置盗版资源站、破解接口或绕过 DRM 的功能。

## 功能规划

- FastAPI 后端，提供健康检查与统一 JSON API
- 影视分类、搜索、详情和播放源数据模型
- 清晰度识别：2160P/4K、1080P、720P、SD
- 资源站适配器机制，便于添加/停用合规数据源
- TVBox 风格配置输出（具体客户端字段兼容性需实测）
- Docker 部署

## 本地运行

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/docs` 查看 API 文档。

## API

- `GET /health`：健康检查
- `GET /api/v1/catalog`：分类列表
- `GET /api/v1/search?q=...`：搜索（接入数据源前返回空结果）
- `GET /api/v1/detail/{vod_id}`：影片详情
- `GET /api/v1/play/{vod_id}`：播放线路（只返回已授权源配置的播放地址）
- `GET /tvbox/config.json`：客户端配置模板

## 4K 标记规则

按来源元数据中的分辨率/标签识别；2160P、3840x2160、UHD、4K 可标记为 `4K`。不能仅凭文件名保证实际画质，后续可增加媒体探测和来源可信度字段。

## 数据源接入

在 `app/sources/` 中实现适配器，并在配置中启用。每个适配器应遵守上游 API 的授权、频率限制、缓存和署名要求。不要将账号密码、Cookie 或密钥提交到 Git；使用环境变量。
