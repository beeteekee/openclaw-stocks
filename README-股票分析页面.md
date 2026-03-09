# 股票分析页面使用说明

## 为什么需要独立页面？

OpenClaw 的 Control UI 要求必须在 **HTTPS** 或 **localhost** 环境下才能运行，这是浏览器安全策略的要求。

**解决方案**：创建了一个独立的 HTML 页面，可以直接打开使用，无需 HTTPS。

---

## 使用方法

### 方法 1：直接打开（推荐）

在 Finder 中找到文件并双击打开：
```
/Users/likan/.openclaw/workspace/stock-analysis.html
```

### 方法 2：通过命令行打开

```bash
open /Users/likan/.openclaw/workspace/stock-analysis.html
```

### 方法 3：通过本地服务器访问（可选）

如果需要在不同设备访问，可以启动一个简单的 HTTP 服务器：

```bash
# Python 3
python3 -m http.server 8000

# 然后访问
# http://localhost:8000/stock-analysis.html
```

---

## 页面功能

### 📊 核心功能
- **股票输入**：支持股票名称（如"比亚迪"）或代码（如"002594"）
- **智能分析**：基于养家心法10条核心原则
- **实时结果**：WebSocket 实时接收分析结果

### 🎯 分析维度
1. **行业成长系数** - 高成长/中成长/低成长/无成长
2. **财务质量评分** - ROE、ROA、负债率等指标
3. **技术面分析** - 250日均线 + 缠论买卖点
4. **题材热度** - 近10个交易日涨停统计
5. **综合得分** - 长期/中期/短期评分

### ⚡ 便捷功能
- **快速示例**：点击预设股票标签快速选择
- **自动重连**：连接断开后3秒自动重连
- **回车快捷键**：按 Enter 键快速提交
- **连接状态**：实时显示连接状态

---

## 连接配置

页面会自动尝试以下 WebSocket 地址（按优先级）：

1. `wss://stockbot.nat100.top/ws` （推荐，如果支持 WSS）
2. `ws://stockbot.nat100.top:18789/ws`
3. `wss://stockbot.nat100.top:18789/ws`

如果都无法连接，会显示错误信息。

---

## 故障排查

### 问题 1：连接失败
**原因**：Gateway 服务未运行或端口未开放

**解决方法**：
```bash
# 检查 Gateway 进程
ps aux | grep openclaw

# 检查端口监听
lsof -i :18789

# 重启 Gateway
openclaw gateway restart
```

### 问题 2：分析无响应
**原因**：Agent 未绑定到 webchat 通道

**解决方法**：检查配置中是否包含正确的 binding：
```json
{
  "bindings": [
    {
      "agentId": "stock-analysis",
      "match": {
        "channel": "webchat"
      }
    }
  ]
}
```

### 问题 3：需要认证
**原因**：Gateway 配置了 Token 认证

**解决方法**：如果需要 Token，可以在页面中修改 JavaScript 代码，在认证消息中添加 Token。

---

## 示例输入

### 输入股票名称
```
分析股票：比亚迪
分析股票：贵州茅台
分析股票：宁德时代
```

### 输入股票代码
```
分析股票：002594
分析股票：300750
分析股票：600519
```

### 混合查询
```
分析股票：比亚迪 002594
```

---

## 技术说明

### WebSocket 消息格式

**发送（客户端 → 服务器）：**
```json
{
  "type": "message",
  "message": "分析股票：比亚迪"
}
```

**接收（服务器 → 客户端）：**
```json
{
  "type": "message",
  "message": "📊 比亚迪(002594)诊断结果..."
}
```

### 浏览器兼容性
- ✅ Chrome (推荐)
- ✅ Safari
- ✅ Firefox
- ✅ Edge
- ✅ 所有现代浏览器

---

## 更新日志

### 2026-02-14
- ✅ 创建独立股票分析页面
- ✅ 支持多种 WebSocket 地址自动尝试
- ✅ 添加快速示例标签
- ✅ 实现自动重连机制
- ✅ 优化界面设计和用户体验

---

## 反馈与支持

如遇问题，请检查：
1. Gateway 服务是否正常运行
2. 端口 18789 是否监听正常
3. 网络连接是否稳定

**页面位置**：`/Users/likan/.openclaw/workspace/stock-analysis.html`
