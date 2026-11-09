# MCP Server（W8）

把 RM Copilot 的能力以 MCP 工具暴露给 Claude Desktop、Cursor 等客户端。

计划中的工具：

| 工具 | 类型 | 说明 |
|---|---|---|
| `search_customers` | 只读 | 按条件查客户 |
| `get_customer_360` | 只读 | 客户画像、持仓、服务记录 |
| `ask_data` | 只读 | 自然语言问数（走语义层） |
| `draft_outreach` | 草稿 | 生成触达文案，不发送 |
| `submit_outreach` | 写操作 | 提交审批，必须经人工确认后才发送 |
