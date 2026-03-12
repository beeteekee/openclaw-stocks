# 公网访问配置说明

## 🌐 当前问题

### 现象
- 本地访问：✅ 正常（http://localhost/ - HTTP 200）
- 公网访问：❌ 失败（http://stockbot.nat100.top/ - HTTP 404）
- 服务器类型：natapp.cc（内网穿透服务）

### 原因分析
```
stockbot.nat100.top:80
         ↓
   natapp.cc转发
         ↓
   本地Python后端（端口5000）← 这里返回404
```

natapp的80端口配置为转发到本地的5000端口（Python后端），而不是80端口（前端服务器）。

---

## 🔧 解决方案

### 方案1：配置natapp端口转发（推荐）

#### 步骤
1. 登录natapp.cc网站
2. 找到stockbot.nat100.top对应的隧道
3. 修改端口转发配置：
   - 前置端口：80（公网）
   - 目标地址：127.0.0.1
   - 目标端口：80（前端服务器）

#### 优点
- 保留现有的5000端口隧道
- 可以同时访问前端和后端
- 配置简单

#### 缺点
- 需要natapp账号权限
- 免费版可能有限制

### 方案2：前端服务器完整代理

前端服务器已经配置了API代理，可以转发所有API请求到Python后端。

#### 当前配置
```javascript
// 股票分析API
app.get('/api/analyze', (req, res) => {
    // 转发到 http://localhost:5000/api/analyze
});

// TOP3精选API
app.get('/api/top3', (req, res) => {
    // 转发到 http://localhost:5000/api/top3
});

// 统计API
app.post('/api/stats/record', (req, res) => {
    // 本地处理
});

app.get('/api/stats/previous', (req, res) => {
    // 本地处理
});
```

#### 优点
- 无需修改natapp配置
- 所有请求通过80端口
- 前端服务器统一管理

#### 缺点
- 需要确保前端服务器持续运行

### 方案3：使用多个natapp隧道

为前端和后端分别创建不同的natapp隧道。

#### 配置示例
```
前端隧道：
- 公网：stockbot.nat100.top:80
- 本地：127.0.0.1:80（前端服务器）

后端隧道：
- 公网：stockbot-api.natapp.cc:80
- 本地：127.0.0.1:5000（Python后端）
```

#### 优点
- 前后端完全隔离
- 可以独立重启

#### 缺点
- 需要多个natapp隧道
- 需要不同的域名

---

## 🚀 快速修复（方案2实施方案）

### 前端已完成的功能
✅ 静态页面服务
✅ 统计API（本地存储）
✅ API代理到后端
✅ TOP3精选展示

### 需要的操作
1. 确认natapp配置，让80端口指向本地80端口
2. 或者使用方案3，创建单独的前端隧道

---

## 📋 服务启动脚本

### 停止所有服务
```bash
pkill -f "node.*server"
pkill -f "python.*stock_service"
```

### 启动所有服务（推荐顺序）
```bash
# 1. 启动Python后端（端口5000）
cd /Users/likan/.openclaw/workspace
nohup python3 stock_service.py > /tmp/stock_service.log 2>&1 &

# 2. 启动前端服务器（端口80）
cd stockbot-frontend
nohup node server-complete.js > /tmp/stockbot-frontend.log 2>&1 &
```

### 检查服务状态
```bash
# 查看进程
ps aux | grep -E "node.*server|python.*stock_service" | grep -v grep

# 查看端口
lsof -i :80 -i :5000

# 查看日志
tail -f /tmp/stock_service.log
tail -f /tmp/stockbot-frontend.log
```

---

## 🎯 测试清单

### 本地测试
```bash
# 前端页面
curl -I http://localhost/stock-analysis-final.html

# TOP3 API
curl http://localhost/api/top3?limit=3

# 统计API
curl http://localhost/api/stats/previous

# 后端健康检查
curl http://localhost:5000/api/health
```

### 公网测试（natapp配置后）
```bash
# 前端页面
curl -I http://stockbot.nat100.top/stock-analysis-final.html

# TOP3 API
curl http://stockbot.nat100.top/api/top3?limit=3

# 统计API
curl http://stockbot.nat100.top/api/stats/previous
```

---

## 📊 当前服务状态

| 服务 | 状态 | PID | 端口 |
|------|------|-----|------|
| 前端服务器 | ✅ 运行中 | 68387 | 80 |
| Python后端 | ✅ 运行中 | 68550 | 5000 |
| 本地访问 | ✅ 正常 | - | localhost:80 |
| 公网访问 | ❌ 需配置 | - | stockbot.nat100.top |

---

**更新时间**: 2026-03-12 12:10
**状态**: 本地功能完整，公网需要natapp配置
