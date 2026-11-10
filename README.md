# RM Copilot

[![CI](https://github.com/Bruce010106/rm-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/Bruce010106/rm-copilot/actions/workflows/ci.yml)

客户经理（Relationship Manager）的 AI 工作台：让 Agent **安全地**参与客户经营——回答有证据、写操作要审批、指标口径统一、效果可评测。

> 全部数据为合成数据（`data/seed`），不含任何真实客户或公司信息。

## 架构

```
apps/web (Next.js 15)  ──HTTP──▶  services/agent (FastAPI)  ──▶  Postgres + pgvector
       ▲                                │                         Redis（任务队列）
       │                                ├─ LLM Provider 抽象（Claude / OpenAI 兼容 / mock）
Claude Desktop ──MCP──▶ packages/mcp-server ─┘
```

| 目录 | 内容 |
|---|---|
| `apps/web` | 前端 + BFF（Server Components 直连 agent 服务） |
| `services/agent` | 数据 API、Agent 循环、工具、问数 |
| `packages/mcp-server` | 对外暴露的 MCP 工具（W8） |
| `data/seed` | 合成数据生成器；`truth.json` 是 KYC 评测的标准答案 |
| `evals` | 评测集与跑分脚本 |
| `docs/adr` | 架构决策记录 |

## 本地启动

```bash
cp .env.example .env
docker compose up -d                      # Postgres(pgvector) + Redis

# Agent 服务
cd services/agent
python -m venv .venv && .venv/Scripts/activate     # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev,llm]"
python ../../data/seed/generate.py --customers 300
python -m app.seed                        # 建表并导入合成数据
uvicorn app.main:app --reload             # http://localhost:8000/docs

# 前端（另开终端）
cd apps/web
pnpm install
pnpm dev                                  # http://localhost:3000
```

测试：`cd services/agent && pytest`（用内存 SQLite，不依赖 docker）。

## 开发约定

- **接口类型**：前端类型由后端 OpenAPI 自动生成，不手写。改了后端接口后：
  ```bash
  cd services/agent && python scripts/export_openapi.py   # 更新 apps/web/openapi.json
  cd apps/web && pnpm gen:api                              # 更新 lib/api-types.ts
  ```
  CI 会检查这两个文件是否最新。
- **代码规范**：Python 用 `ruff check` + `ruff format`；前端用 `pnpm typecheck`。
- **UI 组件**：shadcn/ui（`components/ui`），用 `pnpm dlx shadcn@latest add <组件>` 添加。
- **流程**：每个功能对应一个 Issue，开分支、提 PR，CI 通过后合并。

## 路线图

- [x] W1–2 数据模型、合成数据、客户列表 / 客户 360
- [ ] W3 LLM 抽象层接入，客户 AI 摘要（带证据引用）
- [ ] W4–5 问数 Agent：语义层 + NL2SQL + SQL 安全校验 + 评测集
- [ ] W6 今日工作台：规则召回 + LLM 排序 + 采纳反馈
- [ ] W7 触达助手：个性化文案 + 合规检查 + 人工审批
- [ ] W8 MCP Server，写操作 human-in-the-loop
- [ ] W9 KYC 标签抽取（证据链）+ 准确率/召回率评测
- [ ] W10 角色权限、可观测、成本统计
- [ ] W11–12 部署、演示视频、技术博客
