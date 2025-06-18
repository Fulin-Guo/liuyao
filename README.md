# 专业六爻排盘与API服务

本项目是一个专业的六爻排盘工具，它不仅提供了一个基于Web的用户界面（WebUI）来进行六爻排盘，还暴露了一个API接口，允许开发者通过编程方式获取排盘结果。

## 项目特点

- **Web用户界面 (WebUI)**: 使用 Streamlit 构建，提供一个直观易用的界面，用户可以选择特定时间或使用当前时间进行六爻排盘。卦象展示精美，清晰显示本卦、变卦、动爻、纳甲六亲及世应等信息。
- **API 服务**: 基于 FastAPI 构建，提供一个 `/divination` 接口，可以通过POST请求（可选 `target_time`参数）获取六爻排盘结果。API使用API Key进行认证。
- **核心排盘逻辑**: 包含精确的农历转换、天干地支计算、以及基于时间起卦的六爻算法。
- **模块化设计**: 项目结构清晰，核心服务（如时间转换、卦象计算）与API接口、WebUI分离，易于维护和扩展。

## 技术栈

- **后端与API**: Python, FastAPI
- **Web用户界面**: Python, Streamlit
- **数据与时间处理**: Python内置 `datetime` 模块，自定义农历转换逻辑
- **数据库**: SQLite (用于存储API Key等)

## 如何运行

### 1. 环境准备

确保你已经安装了 Python (推荐 3.8+)。然后安装项目依赖：

```bash
pip install -r requirement.txt
```

### 2. 生成API Key (可选，如果需要使用API)

运行 `create_api_key.py` 脚本来生成一个API Key，并将其记录下来。API Key会存储在 `liuyao_api.db` 数据库中。

```bash
python create_api_key.py
```

### 3. 运行API服务

使用 uvicorn 启动 FastAPI 应用：

```bash
uvicorn app.main:app --reload
```

API服务默认运行在 `http://127.0.0.1:8000`。你可以访问 `http://127.0.0.1:8000/docs` 查看API文档和进行交互式测试。

**API使用示例**:

向 `/divination` 端点发送POST请求。在请求头中包含 `X-API-Key` 并填入你生成的API Key。

请求体 (可选 `target_time`，ISO 8601格式):

```json
{
  "target_time": "2025-06-18T10:30:00"
}
```

如果省略 `target_time`，则使用服务器当前时间。

### 4. 运行Web用户界面

在新的终端中，使用 streamlit 启动 WebUI：

```bash
streamlit run webui.py
```

WebUI通常会自动在浏览器中打开，地址一般为 `http://localhost:8501`。

## 项目结构

```
liuyao/
├── README.md               # 本文档
├── app/                    # FastAPI 应用目录
│   ├── __init__.py
│   ├── crud.py             # 数据库操作
│   ├── database.py         # 数据库配置和引擎
│   ├── dependencies.py     # API依赖项 (如API Key验证)
│   ├── main.py             # FastAPI应用主入口
│   ├── models.py           # SQLAlchemy数据模型
│   ├── schemas.py          # Pydantic数据模型 (请求/响应)
│   └── services/           # 核心服务逻辑
│       ├── calculator.py   # (已整合到divination_service.py)
│       ├── constants.py    # 卦象、天干地支等常量
│       ├── divination_service.py # 六爻排盘核心服务
│       ├── formatter.py    # (可能用于格式化输出，具体看内容)
│       └── time_converter.py # 公历农历及干支转换
├── create_api_key.py       # 生成API Key的脚本
├── liuyao_api.db           # SQLite数据库文件
├── requirement.txt         # 项目依赖
├── tests/                  # 测试目录 (当前为空)
└── webui.py                # Streamlit Web用户界面
```

## 未来展望

- 增加更详细的卦辞、爻辞解释。
- 支持更多的起卦方式。
- 完善单元测试和集成测试。
- 优化UI/UX体验。
