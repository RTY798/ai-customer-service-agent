# 电商智能客服系统 — 用户使用手册

## 目录

- [系统概述](#系统概述)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [三种使用方式](#三种使用方式)
- [测试用例](#测试用例)
- [自定义数据源](#自定义数据源)
- [常见问题](#常见问题)

---

## 系统概述

本系统是一个基于 **LangGraph** 的多 Agent 电商智能客服。用户提问后，系统自动判断意图，路由到对应的 Agent 处理，最终生成回复。整个流程类似真人客服的思考过程：

1. **理解意图** — 用户想查订单？问产品？还是投诉？
2. **查找信息** — 去知识库搜索，或用工具查询订单/物流
3. **组织回复** — 整合所有信息，生成友好回答

### Agent 处理路径

| 用户意图 | 处理路径 | 示例 |
|---------|---------|------|
| 产品咨询 | Router → Knowledge → Summary | "你们有什么产品？" |
| 订单查询 | Router → Tool → Summary | "查一下 ORD-001" |
| 投诉升级 | Router → Escalation → Summary | "我要投诉" |
| 一般问候 | Router → Knowledge → Summary | "你好" |

---

## 快速开始

### 前置要求

- Python 3.13+
- Node.js 22+
- 一个 OpenAI 兼容的 LLM API Key（推荐 [DeepSeek](https://platform.deepseek.com/) 免费注册）

### 安装与启动

#### 方式一：本地启动（推荐开发调试）

```bash
# 1. 配置 API Key
cd backend
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY

# 2. 安装后端依赖
pip install -r requirements.txt
pip install langgraph langchain-community

# 3. 初始化知识库
python seed_data.py

# 4. 安装前端依赖
cd ../frontend
npm install

# 5. 启动（需要两个终端）
# 终端 1 - 后端 API
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2 - 前端界面
cd frontend && npm run dev

# 6. 浏览器打开 http://localhost:3000
```

#### 方式二：Docker 一键部署

```bash
# 设置你的 API Key
set LLM_API_KEY=sk-your-key-here

# 一键启动
docker-compose up --build
```

#### 方式三：CLI 终端模式（无需前端）

```bash
cd backend
python -m app.cli
```

---

## 配置说明

### 核心配置（.env 文件）

```ini
# ── LLM API 配置 ──
LLM_API_KEY=sk-your-api-key-here    # 你的 API Key（必填）
LLM_BASE_URL=https://api.deepseek.com  # API 地址
LLM_MODEL=deepseek-chat                # 模型名称

# ── 数据源配置 ──
DATA_PROVIDER=demo                      # "demo" 用内置演示数据
                                        # 或 "mymodule:MyProvider" 用自定义数据源

# ── 服务配置 ──
HOST=0.0.0.0
PORT=8000
```

### 支持的 LLM 供应商

| 供应商 | API 地址 | 推荐模型 |
|--------|---------|---------|
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| 硅基流动 | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-7B-Instruct` |

> 只要兼容 OpenAI API 格式都可以使用，修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

---

## 三种使用方式

### 1. Web UI（浏览器）

启动后访问 `http://localhost:3000`，界面包含：

- **消息区域**：显示对话历史
- **输入框**：底部输入问题，Enter 发送，Shift+Enter 换行
- **Agent 处理过程**：每条回复上方有"Agent 处理过程"按钮，点击展开可看到每个 Agent 的处理步骤和中间结果

![界面布局说明](https://via.placeholder.com/800x500?text=Chat+UI+Screenshot)

### 2. CLI 终端

适合开发调试或无图形界面的服务器环境。

```bash
cd backend
python -m app.cli
```

CLI 模式会显示：
- Agent 的**处理路径**（如 `knowledge → summary`）
- 每个 Agent 的**输出摘要**
- 生成的**工单信息**（投诉场景）

可用命令：
- `/help` — 显示帮助
- `/quit` — 退出

### 3. REST API

适合集成到其他系统。

**普通请求（JSON）：**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "查询订单 ORD-001"}'
```

返回格式：

```json
{
  "reply": "您的订单 ORD-001 已于 2026-05-01 发货...",
  "intent": "order_query",
  "thought_chain": [
    {"agent": "router", "status": "completed", ...},
    {"agent": "tool", "status": "completed", ...},
    {"agent": "summary", "status": "completed", ...}
  ],
  "escalation_ticket": null
}
```

**流式请求（SSE，实时推送 Agent 思考过程）：**

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

SSE 事件流格式：

```
data: {"event": "thought", "data": {"agent": "router", "status": "running", "detail": "正在分析您的意图..."}}

data: {"event": "thought", "data": {"agent": "router", "status": "completed", ...}}

data: {"event": "thought", "data": {"agent": "knowledge", "status": "completed", ...}}

data: {"event": "message", "data": {"content": "您好！很高兴为您服务！请问有什么可以帮您的吗？"}}

data: {"event": "done", "data": {}}
```

| 事件类型 | 说明 |
|---------|------|
| `thought` | Agent 思考过程（包含 agent 名称、状态、输入输出等） |
| `message` | 最终回复内容 |
| `ticket` | 工单信息（仅投诉场景） |
| `done` | 处理完成 |

---

## 测试用例

启动后可以尝试以下问题，观察不同的 Agent 处理路径：

### 产品咨询 → Knowledge Agent

> "你们有什么产品？"
> "蓝牙耳机多少钱？"
> "键盘有什么功能？"

**预期**：系统检索知识库，返回产品介绍。

### 订单查询 → Tool Agent

> "查询订单 ORD-001"
> "查一下 ORD-002 的物流"
> "我的订单到哪里了？"

**预期**：系统调用订单查询工具，返回订单状态和物流信息。

### 投诉升级 → Escalation Agent

> "我要投诉"
> "我要退货，质量太差了"
> "找你们经理来"

**预期**：系统生成工单，显示工单编号和摘要。

### 一般问答 → Knowledge Agent

> "你好"
> "退货政策是怎样的？"
> "你们发什么快递？"
> "怎么开发票？"

**预期**：系统从知识库检索相关文档并回答。

---

## 自定义数据源

系统默认使用内置演示数据。要接入自己的电商数据库，只需实现一个接口。

### 实现步骤

1. 创建一个类，继承 `ECommerceDataProvider`
2. 实现所有抽象方法（订单/物流/商品/政策/知识库）
3. 配置环境变量指向你的类

详细教程见 [docs/DATA_PROVIDER.md](docs/DATA_PROVIDER.md)。

### 简单示例

```python
# myprovider.py
from app.data.base import ECommerceDataProvider, Order, Product

class MyProvider(ECommerceDataProvider):
    def get_order(self, order_id):
        # 从你的数据库查询
        row = your_db.query("SELECT * FROM orders WHERE id=?", order_id)
        if row:
            return Order(order_id=row.id, status=row.status, ...)
        return None
    
    # ... 实现其他方法
    
    def get_all_knowledge_docs(self):
        # 返回你的知识库文档列表
        return [...]
```

配置 `.env`：

```ini
DATA_PROVIDER=myprovider:MyProvider
```

---

## 常见问题

### Q: 启动后前端显示白屏或加载中？

检查后端是否已启动：`curl http://localhost:8000/api/health`。如果返回 `{"status":"ok"}` 表示后端正常，刷新前端页面即可。

### Q: 后端报 "LLM API 调用失败"？

检查 `.env` 中的 `LLM_API_KEY` 是否正确配置，以及 `LLM_BASE_URL` 是否能正常访问。

### Q: Docker 启动后连不上后端？

Docker 环境中前端容器通过 `http://backend:8000` 访问后端（Docker 内部 DNS），不是 `localhost:8000`。如果修改了后端端口，需要同步修改 `frontend/lib/api.ts` 中的地址。

### Q: CLI 模式中文显示乱码？

Windows 终端可能不支持 UTF-8 显示。在启动 CLI 前执行：

```bash
chcp 65001  # 切换到 UTF-8 代码页
python -m app.cli
```

### Q: 如何清空对话历史？

刷新前端页面（Web UI）或重新启动 CLI 程序即可。系统目前不持久化对话历史。

### Q: 支持哪些语言？

系统支持中文和英文输入。LLM 会根据用户输入的语言自动用相应语言回复。
