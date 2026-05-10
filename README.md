# 🛒 电商智能客服系统

基于 **LangGraph** 的多 Agent 电商智能客服系统，涵盖意图分类、RAG 知识库检索、Function Calling 工具调用、工单升级等完整客服流程。

**可插拔数据源** — 内置演示数据，接入真实电商数据库只需实现一个接口，无需修改任何业务代码。

---

## 🚀 三分钟快速上手

### 第一步：获取 API Key

前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 免费注册 → 创建 API Key → 复制。

> 也可以使用 OpenAI、通义千问、硅基流动等任何兼容 OpenAI 接口的服务商。

### 第二步：配置

```bash
# 克隆项目
git clone https://github.com/RTY798/ai-customer-service-agent.git
cd ai-customer-service-agent

# 配置 API Key
cd backend
cp .env.example .env
```

打开 `.env`，填入你的 API Key：

```ini
LLM_API_KEY=sk-你的key粘贴到这里
```

> 其他配置保持默认即可。

### 第三步：启动（任选一种方式）

#### 🐳 方式一：Docker 一键启动（推荐，最简单）

```bash
set LLM_API_KEY=sk-你的key粘贴到这里
docker-compose up --build
```

等待构建完成，浏览器打开 **http://localhost:3000**。

#### 💻 方式二：本地手动启动

**后端：**

```bash
cd backend
pip install -r requirements.txt
pip install langgraph langchain-community
python seed_data.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**新开一个终端，启动前端：**

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 **http://localhost:3000**。

#### ⌨️ 方式三：纯命令行模式（不需要前端）

```bash
cd backend
pip install -r requirements.txt
pip install langgraph langchain-community
python seed_data.py
python -m app.cli
```

### 第四步：开始对话

在聊天框输入以下问题试试：

| 你想做什么 | 输入这句话 |
|-----------|-----------|
| 查看产品 | `你们有什么产品？` |
| 查订单 | `查询订单 ORD-001` |
| 追踪物流 | `ORD-001 到哪里了？` |
| 了解退货 | `怎么退货？` |
| 投诉 | `我要投诉` |
| 打个招呼 | `你好` |

你会看到 AI 的思考过程实时展示：**"分流 → 知识库 → 汇总"** 或 **"分流 → 工具 → 汇总"**，点开可以查看每个 Agent 的处理细节。

---

## 📚 详细使用说明

### Web UI 界面

```
┌─────────────────────────────────────────────┐
│  🅰 电商智能客服系统            ● 在线       │  ← 顶栏
├─────────────────────────────────────────────┤
│                                             │
│  你好！我是电商智能客服系统...             │  ← 欢迎消息
│                                             │
│  ┌─────────────────────────────────┐        │
│  │ 你们有什么产品？                │        │  ← 你的问题
│  └─────────────────────────────────┘        │
│                                             │
│  AI 电商智能客服                            │
│  ┌─────────────────────────────────┐        │
│  │ 我们主要销售以下产品...         │        │  ← AI 回复
│  └─────────────────────────────────┘        │
│  ┌─ Agent 处理过程 ───────────────┐         │
│  │ ● ● ●                   展开   │        │  ← 思考链（可展开）
│  └─────────────────────────────────┘        │
│                                             │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────┐  [➤]          │  ← 输入框
│  │ 输入你的问题...         │               │
│  └─────────────────────────┘               │
│  Enter 发送  Shift+Enter 换行              │
└─────────────────────────────────────────────┘
```

- **Enter** 发送消息，**Shift+Enter** 换行
- 点击 **"Agent 处理过程"** 展开查看 AI 的完整思考路径
- 投诉场景会自动生成 **工单**，显示编号和摘要

### CLI 模式操作

启动后看到：

```
╔══════════════════════════════════════════╗
║       电商智能客服系统  v1.0              ║
║   LangGraph 多 Agent 智能客服             ║
║                                          ║
║   输入 /help 查看命令                     ║
║   输入 /quit 退出                         ║
╚══════════════════════════════════════════╝

  You: 你们有什么产品？
```

CLI 模式会显示处理路径和每个 Agent 的输出摘要，适合开发调试。

### API 调用

```bash
# 普通请求
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "查询订单 ORD-001"}'

# 流式请求（SSE，实时推送思考过程）
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

---

## 🧠 系统架构

```
用户 → [Web UI / CLI / API] → LangGraph Agent Workflow
                                  │
        ┌─────────────────────────┼──────────────────────┐
        ▼                         ▼                      ▼
   Router Agent           Knowledge Agent           Tool Agent
  (意图分类: 4类)        (RAG 知识库检索)        (Function Calling)
        │                         │                      │
        └─────────────────────────┼──────────────────────┘
                                  ▼
                           Summary Agent
                        (整合 + 自然语言回复)
                                  │
                                  ▼
                          响应 → 用户
```

### 5 个 Agent 分工

| Agent | 职责 | 技术实现 |
|-------|------|----------|
| **Router** | 意图分类（order_query / product_inquiry / complaint / general） | LLM structured output → 条件路由 |
| **Knowledge** | 产品 FAQ、退换货政策、配送说明等知识检索 | 关键词匹配（Jaccard 相似度）+ LLM 合成 |
| **Tool** | 订单查询、物流追踪、退换货政策查询、产品详情 | Function Calling（4 个工具函数） |
| **Escalation** | 升级处理，生成结构化工单 | LLM 生成工单摘要 → 转人工 |
| **Summary** | 整合所有 Agent 输出，生成友好回复 | LLM 自然语言合成 |

---

## 🔌 接入自己的数据

系统默认使用内置演示数据（3 个订单、3 个产品、9 篇知识库文档）。接入自己的电商数据库只需三步：

### 1. 创建一个 Provider 类

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
    
    def get_all_knowledge_docs(self):
        # 返回你的知识库文档
        return [...]

    # ... 还需实现其他 8 个方法
```

### 2. 配置 .env

```ini
DATA_PROVIDER=myprovider:MyProvider
```

### 3. 重启系统

> 不需要修改任何业务代码。详细教程见 [docs/DATA_PROVIDER.md](docs/DATA_PROVIDER.md)。

---

## ⚙️ 技术栈

| 组件 | 技术 |
|------|------|
| Agent 框架 | LangGraph（StateGraph + 条件边编排） |
| LLM | OpenAI 兼容 API（DeepSeek Chat） |
| 后端 | FastAPI + SSE 流式推送 |
| 前端 | Next.js 16 + Tailwind CSS v4 |
| 部署 | Docker Compose |

---

## 🧪 测试用例

| 问题 | 期望路径 | 验证内容 |
|------|----------|----------|
| "你们有什么产品？" | Router → Knowledge → Summary | 知识库检索 |
| "查询订单 ORD-001" | Router → Tool → Summary | Function Calling |
| "ORD-001 到哪里了？" | Router → Tool → Summary | 物流追踪 |
| "怎么退货？" | Router → Knowledge → Summary | 政策查询 |
| "我要投诉" | Router → Escalation → Summary | 工单生成 |
| "你好" | Router → Knowledge → Summary | 兜底回复 |

---

## ❓ 常见问题

**Q: 启动报错 "ModuleNotFoundError: No module named 'pydantic_settings'"**

确保你用的是 Python 3.13+，并已安装所有依赖：
```bash
pip install -r requirements.txt
pip install langgraph langchain-community
```

**Q: 前端连不上后端**

确认后端已启动（`curl http://localhost:8000/api/health` 返回 `{"status":"ok"}`）。前端默认连接 `http://localhost:8000`。

**Q: Docker 启动后前端白屏**

Docker 环境中前端通过 `http://backend:8000` 访问后端（Docker 内部 DNS）。确认没有修改默认端口。

**Q: CLI 中文显示乱码**

Windows 终端请先执行 `chcp 65001` 切换到 UTF-8 代码页。

**Q: 怎么清空对话历史？**

刷新页面（Web UI）或重启 CLI 程序即可。系统不持久化对话历史。

---

## 📂 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI + SSE 端点
│   │   ├── config.py             # pydantic-settings
│   │   ├── cli.py                # CLI 终端交互
│   │   ├── data/                 # ★ 数据抽象层
│   │   │   ├── base.py           # 数据模型 + Provider 接口
│   │   │   ├── demo_provider.py  # 演示数据（默认）
│   │   │   └── config.py         # Provider 选择逻辑
│   │   ├── models/schemas.py     # 数据模型
│   │   ├── agents/
│   │   │   ├── graph.py          # LangGraph 工作流编排
│   │   │   ├── router_agent.py   # 意图分类
│   │   │   ├── knowledge_agent.py # RAG 知识库
│   │   │   ├── tool_agent.py     # 工具调用
│   │   │   ├── escalation_agent.py # 工单升级
│   │   │   └── summary_agent.py  # 汇总回复
│   │   └── knowledge_base/
│   │       └── vector_store.py   # 关键词检索
│   ├── seed_data.py
│   └── requirements.txt
├── frontend/                     # Next.js 16
├── docs/
│   ├── USER_GUIDE.md             # 完整使用手册
│   ├── DATA_PROVIDER.md          # 数据 Provider 接入教程
│   └── 面试问答.md                # 面试准备
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── CONTRIBUTING.md
└── 启动项目.bat
```

---

## 📄 License

MIT
