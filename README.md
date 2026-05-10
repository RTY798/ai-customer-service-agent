# 电商智能客服系统

基于 **LangGraph** 的多 Agent 电商智能客服系统，涵盖意图分类、RAG 知识库检索、Function Calling 工具调用、工单升级等完整客服流程。

**可插拔数据源** — 内置演示数据，接入真实电商数据库只需实现一个接口。

## 交互方式

本系统支持 **3 种交互方式**：

| 方式 | 适用场景 | 启动命令 |
|------|----------|----------|
| 🌐 **Web UI** | 浏览器聊天界面 | 见下方"快速开始" |
| 💻 **CLI 终端** | 开发测试、无头环境 | `python -m app.cli` |
| 🔌 **REST API** | 集成到其他系统 | `POST /api/chat` (含 SSE 流式) |

## 系统架构

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

## Agent 设计

| Agent | 职责 | 技术实现 |
|-------|------|----------|
| **Router** | 意图分类（order_query / product_inquiry / complaint / general） | LLM structured output → 条件路由 |
| **Knowledge** | 产品 FAQ、退换货政策、配送说明等知识检索 | 关键词匹配（Jaccard 相似度）+ LLM 合成 |
| **Tool** | 订单查询、物流追踪、退换货政策查询、产品详情 | Function Calling（4 个工具函数） |
| **Escalation** | 升级处理，生成结构化工单 | LLM 生成工单摘要 → 转人工 |
| **Summary** | 整合所有 Agent 输出，生成友好回复 | LLM 自然语言合成 |

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent 框架 | LangGraph（StateGraph + 条件边编排） |
| LLM | OpenAI 兼容 API（DeepSeek Chat） |
| 后端 | FastAPI + SSE 流式推送 |
| 前端 | Next.js 16 + Tailwind CSS v4 |
| 部署 | Docker Compose |

## 快速开始

### 前置要求

- Python 3.13+
- Node.js 22+
- 一个 OpenAI 兼容的 LLM API Key（[DeepSeek](https://platform.deepseek.com/) 免费注册）

### 1. 配置

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY
```

### 2. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt
pip install langgraph langchain-community
python seed_data.py

# 前端
cd frontend
npm install
```

### 3. 启动

**方式 A: Web UI**

```bash
# 终端 1 - 后端
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2 - 前端
cd frontend && npm run dev

# 浏览器打开 http://localhost:3000
```

**方式 B: CLI 终端**

```bash
cd backend && python -m app.cli
```

**方式 C: Docker 一键部署**

```bash
set LLM_API_KEY=sk-your-key-here
docker-compose up --build
```

## 接入真实数据

系统默认使用内置演示数据。要接入你自己的电商数据库：

1. 实现 `ECommerceDataProvider` 接口（详见 [docs/DATA_PROVIDER.md](docs/DATA_PROVIDER.md)）
2. 在 `.env` 中配置：
   ```ini
   DATA_PROVIDER=myapp.providers:MyCustomProvider
   ```
3. 重启系统即可

## 测试用例

| 问题 | 期望路径 | 验证内容 |
|------|----------|----------|
| "你们有什么产品？" | Router → Knowledge → Summary | 知识库检索 |
| "查询订单 ORD-001" | Router → Tool → Summary | Function Calling |
| "我要投诉" | Router → Escalation → Summary | 工单生成 |
| "你好" | Router → Knowledge → Summary | 兜底回复 |

## 项目结构

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
│   ├── DATA_PROVIDER.md          # 数据 Provider 接入教程
│   └── 面试问答.md                # 面试准备
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── CONTRIBUTING.md
└── 启动项目.bat
```

## 简历价值

| 面试高频问题 | 本项目回答 |
|-------------|-----------|
| "用过什么 Agent 框架？" | LangGraph 多 Agent 编排（StateGraph + 条件路由） |
| "RAG 怎么实现的？" | 文档分块 + 语义检索 + LLM 合成 |
| "Function Calling 用过吗？" | 4 个工具函数：订单查询、物流追踪、政策查询、产品详情 |
| "Agent 之间怎么通信？" | LangGraph StateGraph 共享状态 + 条件边路由 |
| "怎么处理 Agent 错误？" | 降级策略 + 转人工兜底 |
| "部署经验？" | Docker Compose 全容器化 |

## License

MIT
