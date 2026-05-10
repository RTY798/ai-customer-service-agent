# 贡献指南

## 开发环境

- Python 3.13+
- Node.js 22+
- 一个 OpenAI 兼容的 LLM API Key（DeepSeek / OpenAI 等）

## 快速开始

```bash
# 后端
cd backend
cp .env.example .env  # 填入你的 API Key
pip install -r requirements.txt
pip install langgraph langchain-community
python seed_data.py

# 前端
cd frontend
npm install
```

## 项目结构

```
backend/app/
├── agents/         # LangGraph Agent 节点
│   ├── graph.py           # 工作流编排
│   ├── router_agent.py    # 意图分类
│   ├── knowledge_agent.py # RAG 知识库
│   ├── tool_agent.py      # 工具调用
│   ├── escalation_agent.py# 工单升级
│   └── summary_agent.py   # 汇总回复
├── data/           # 数据抽象层 ★
│   ├── base.py            # 数据模型 + 接口
│   ├── demo_provider.py   # 演示数据
│   └── config.py          # Provider 选择
├── knowledge_base/ # 知识库检索
└── main.py         # FastAPI 入口
```

## 代码风格

- Python: PEP 8，使用 `black` + `isort` + `ruff`
- TypeScript: 使用项目 ESLint 配置
- 提交前运行 `ruff check` 和 `tsc --noEmit`

## 如何添加自定义数据 Provider

参考 [docs/DATA_PROVIDER.md](docs/DATA_PROVIDER.md)

1. 实现 `ECommerceDataProvider` 抽象基类
2. 设置环境变量 `DATA_PROVIDER=myapp.providers:MyCustomProvider`
3. 启动系统即可使用你的数据源

## PR 流程

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feat/my-feature`
3. 提交更改: `git commit -m "feat: my feature"`
4. 推送到分支: `git push origin feat/my-feature`
5. 创建 Pull Request

### Commit 规范

- `feat:` 新功能
- `fix:` Bug 修复
- `refactor:` 重构
- `docs:` 文档
- `chore:` 构建/工具

## 报告 Issue

请包含：
- 系统环境（Python 版本、OS）
- 复现步骤
- 期望行为与实际行为
- 完整的错误日志
