# Movie API

面向 TVBox、影视仓及兼容客户端的公开配置整理工具与 API。项目会从公开 GitHub 配置仓库拉取 JSON，合并去重后生成 dist/tvbox.json。

> 公开可访问不等于获得内容版权或接口使用授权。导入结果来自第三方维护，使用前请核验来源许可、所在地法律及目标客户端兼容性。本项目不托管视频、不破解付费服务、不绕过 DRM。

## 当前公开上游

- TVboxorg/TVBox：https://github.com/TVboxorg/TVBox
- 上游 JSON：https://raw.githubusercontent.com/TVboxorg/TVBox/main/dist/official.json

该上游是多源合并配置。本项目保留 spider、parses、lives 等依赖字段。上游源会变动、失效或调整协议；导入成功只代表 JSON 可读取，不代表每个站点都能播放，也不代表每项内容已获授权。

## 快速导入

需要 Python 3.10+：

```bash
pip install -r requirements.txt
python tools/import_sources.py
```

生成 dist/tvbox.json，可供支持 TVBox 标准配置的客户端导入。config/sources.json 是上游仓库清单，可添加你有权使用的 raw GitHub JSON 地址。

导入器仅接受 HTTPS 的 raw.githubusercontent.com 地址，限制响应体大小和超时；会按站点 key 去重，保留 spider、parses、lives、headers 等顶层字段。若本轮没有成功导入任何站点，不会覆盖现有输出。

## API

启动：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- GET /health：健康检查
- GET /tvbox/config.json：生成的客户端配置
- GET /api/v1/announcement：交流群公告（QQ：956979768）
- GET /api/v1/catalog、/api/v1/search、/api/v1/detail/{vod_id}、/api/v1/play/{vod_id}：媒体 API 框架，尚未接入自有授权媒体库

## 4K 与交流群

app/quality.py 可识别 2160P、3840×2160、UHD 等标签并将 4K 排前。源名称含 4K 不代表实际播放流一定达到 4K。

交流群：956979768。API 公告接口已提供该信息。不同 TVBox / 影视仓 客户端对自定义公告字段支持不同，因此不能保证每个 APP 首页都会显示，需按具体客户端适配。
