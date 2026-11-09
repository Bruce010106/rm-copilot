# ADR 0001：整体架构与技术选型

- 状态：已采纳
- 日期：2026-11-09

## 背景

项目目标是展示两类能力：AI 应用 / Agent 工程（工具调用、证据、评测、人工审批）和全栈工程（产品化前端、可部署后端）。

## 决策

1. **前后端分离**：Next.js 15（TypeScript）做界面和 BFF；Python FastAPI 做数据和 Agent 服务。Python 的 LLM 与数据生态最完整，前端保持 TypeScript。
2. **一个数据库**：Postgres + pgvector 同时存业务数据和向量，不引入独立向量库，部署简单，也便于在 SQL 里做混合检索。
3. **LLM Provider 抽象**：业务代码只依赖 `LLMProvider` 接口；提供 mock、Anthropic、OpenAI 兼容三种实现，方便测试与跨模型对比成本和效果。
4. **Agent 循环自写**：先手写 tool-calling 循环，理解并掌控每一步；后续再用 LangGraph 做对照实现。
5. **合成数据 + 标准答案**：生成器在服务记录里埋入客户信号，并单独输出 `truth.json`，让 KYC 抽取从第一天起就可量化评测。
6. **测试不依赖外部服务**：API 测试用内存 SQLite，模型类型只用跨库通用类型；pgvector 列在需要时再单独加。

## 影响

- 需要维护两种语言；接口契约以 FastAPI 的 OpenAPI 为准，后续可生成 TS 类型。
- 暂不引入迁移工具（`app.seed` 直接重建表），出现需保留的数据后再加 Alembic。
