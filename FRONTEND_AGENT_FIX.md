# 前端Agent问题分析报告

## 问题描述
`frontend-coder` agent在当前环境下无法使用。

## 错误信息
```
{"status": "forbidden", "error": "agentId is not allowed for sessions_spawn (allowed: none)"}
```

## 根本原因

### 1. Subagent权限控制机制
OpenClaw的subagent系统使用权限控制，确保安全性：
- 当前session（stock-analysis）的 `allowAny: false`
- 这意味着stock-analysis只能使用明确允许的subagent列表
- 当前列表为空：`allowed: none`

### 2. 配置检查
在 `openclaw.json` 中：
- `agents.defaults.subagents.maxConcurrent: 4` - subagents功能已启用
- `stock-analysis` agent没有配置 `subagents.allowlist`
- `frontend-coder` agent已定义但未被允许访问

### 3. 权限验证
```json
{
  "requester": "stock-analysis",
  "allowAny": false,
  "agents": [
    {
      "id": "stock-analysis",
      "configured": true
    }
  ]
}
```
- 只有 `stock-analysis` 自己在允许列表中
- `frontend-coder` 不在允许列表中

## 解决方案

### 方案1：配置Subagent Allowlist（推荐）✅

在 `stock-analysis` agent配置中添加 `subagents.allowlist`：

```json
{
  "id": "stock-analysis",
  "default": true,
  "name": "股票分析",
  "workspace": "/Users/likan/.openclaw/workspace",
  "identity": {
    "name": "OpenClaw",
    "theme": "专业的股票分析助手",
    "emoji": "📈"
  },
  "sandbox": {
    "mode": "off",
    "workspaceAccess": "rw"
  },
  "subagents": {
    "allowlist": [
      "backend-coder",
      "frontend-coder"
    ]
  }
}
```

**优点：**
- 精确控制哪些agent可以被调用
- 安全性高
- 符合最小权限原则

**缺点：**
- 需要手动配置每个需要调用的agent

### 方案2：启用 allowAny（不推荐）⚠️

在 `stock-analysis` agent配置中设置 `allowAny: true`：

```json
{
  "id": "stock-analysis",
  "default": true,
  "name": "股票分析",
  "subagents": {
    "allowAny": true
  }
}
```

**优点：**
- 配置简单
- 可以调用任何agent

**缺点：**
- 安全性较低
- 可能调用未预期的agent

### 方案3：人工处理前端任务（临时）🔧

直接修改HTML/CSS文件，不使用subagent。

**优点：**
- 无需修改配置
- 立即解决问题

**缺点：**
- 无法利用subagent的功能
- 需要人工介入

## 推荐执行步骤

### 步骤1：备份配置
```bash
cp /Users/likan/.openclaw/openclaw.json /Users/likan/.openclaw/openclaw.json.backup
```

### 步骤2：修改配置
编辑 `/Users/likan/.openclaw/openclaw.json`，在 `stock-analysis` agent配置中添加：

```json
"subagents": {
  "allowlist": [
    "backend-coder",
    "frontend-coder"
  ]
}
```

### 步骤3：重启Gateway
```bash
openclaw gateway restart
```

### 步骤4：验证
```bash
# 检查agents_list
openclaw agents list

# 应该显示backend-coder和frontend-coder
```

## 技术细节

### Subagent权限模型
```
┌─────────────────────────────────────┐
│  stock-analysis (当前session)       │
│  - allowAny: false                │
│  - subagents.allowlist:           │
│    - backend-coder               │
│    - frontend-coder              │
└─────────────────────────────────────┘
              │
              ├── sessions_spawn(agentId="backend-coder") ✅
              ├── sessions_spawn(agentId="frontend-coder") ✅
              └── sessions_spawn(agentId="other-agent") ❌
```

### 配置优先级
1. Agent级别的 `subagents.allowlist`（优先级最高）
2. Agent级别的 `subagents.allowAny`
3. Global defaults

## 备注
- 这个问题不是bug，而是安全特性
- 默认情况下，agent之间不允许互相调用
- 需要明确配置才能允许跨agent调用

---

**报告生成时间**：2026-03-12 09:50
**报告人**：项目经理（stock-analysis）
**状态**：问题分析完成，等待执行修复方案
