# 股票分析服务部署说明

## 📊 服务状态（2026-03-12 10:35）

### 本地服务
- ✅ **Gateway**：运行中（PID 95406，端口18789）
- ✅ **Python后端**：运行中（PID 5548，端口5000）
- ✅ **前端服务器**：运行中（PID 64545，端口80）
- ✅ **API端点**：http://localhost/api/stats/previous ✅
- ✅ **静态页面**：http://localhost/stock-analysis-final.html ✅

### 公网访问
- ❓ **公网80端口**：http://stockbot.nat100.top/
  - 状态：端口可能映射到其他服务
  - 静态页面：可以访问 ✅
  - API端点：返回404 ❌

- ❓ **公网5000端口**：http://stockbot.nat100.top:5000/
  - 状态：无法访问（000错误）

---

## 🔧 部署架构

### 当前配置
```
┌─────────────────────────────────────────┐
│  公网用户                           │
└────────────┬────────────────────────┬─┴──────────────┐
             │                        │
        HTTP (80)                   │
             │                        │
    [stockbot.nat100.top]              │
             │                        │
             ▼                        ▼
    ┌────────────────┐         ┌────────────────┐
    │  反向代理/Nginx? │         │  本地服务      │
    │  (其他机器?)   │         │  本地无法访问   │
    └────────────────┘         └────────────────┘
```

### 期望配置
```
┌─────────────────────────────────────────┐
│  公网用户                           │
└────────────┬────────────────────────┬────────────┐
             │                        │
        HTTP (80)               HTTP (5000)
             │                        │
    [stockbot.nat100.top]    [stockbot.nat100.top]
             │                        │
             └────────┬───────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │  本地前端服务   │
              │  (Node.js: 80)  │
              └─────────────────┘
                      │
              ┌───────┴─────────┐
              │                 │
              ▼                 ▼
    ┌─────────────────┐ ┌─────────────────┐
    │  统计API       │ │  静态文件      │
    │  /api/stats/*   │ │  /public/*      │
    └─────────────────┘ └─────────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │  Python后端    │
              │  (端口 5000)   │
              └─────────────────┘
```

---

## 🚀 功能清单

### ✅ 已实现功能

#### 1. 股票分析
- **页面**：stock-analysis-final.html
- **后端API**：Python stock_service.py
- **端点**：/api/analyze, /api/top3, /api/sentiment
- **状态**：✅ 本地可用，公网待确认

#### 2. 统计信息
- **日期**：当前日期
- **查询次数**：每日查询统计
- **股票数量**：每日股票数量统计
- **存储**：stats.json（本地文件）
- **API端点**：
  - POST /api/stats/record - 记录查询
  - GET /api/stats/previous - 获取统计数据
- **状态**：✅ 本地可用，公网待确认

#### 3. 移动端优化
- **版本**：V3（最新）
- **桌面端**：横向排列
- **移动端**：纵向堆叠，左右布局
- **字体**：标签13px，数值20px
- **触控**：48px高度
- **状态**：✅ 已完成

---

## 🌐 公网访问配置

### 需要检查的内容

1. **端口映射**
   - stockbot.nat100.top:80 映射到哪台机器？
   - stockbot.nat100.top:5000 是否可用？
   - 是否需要配置端口转发？

2. **反向代理**
   - 是否有Nginx或其他反向代理？
   - 反向代理配置是什么？
   - API路由是否正确配置？

3. **防火墙**
   - 本地防火墙是否允许端口80和5000？
   - 路由器端口转发是否正确？

---

## 📝 本地测试命令

### 测试前端服务
```bash
# 测试静态页面
curl http://localhost/stock-analysis-final.html

# 测试API端点
curl http://localhost/api/stats/previous
curl -X POST http://localhost/api/stats/record -H "Content-Type: application/json" -d '{"stockCode":"002594"}'
```

### 测试后端服务
```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 测试股票分析
curl "http://localhost:5000/api/analyze?code=002594"

# 测试TOP3精选
curl http://localhost:5000/api/top3
```

### 查看服务状态
```bash
# 查看端口监听
lsof -i :80 -i :5000

# 查看进程
ps aux | grep -E "node.*server|python.*stock_service"

# 查看日志
tail -f /tmp/stockbot-frontend.log
```

---

## 🎯 下一步行动

### 选项1：确认端口映射
检查stockbot.nat100.top:80和:5000的映射配置，确保指向正确的本地服务。

### 选项2：配置反向代理
如果使用反向代理，配置API路由转发到本地5000端口。

### 选项3：内网穿透
使用内网穿透工具（如ngrok、frp）将本地服务暴露到公网。

### 选项4：本地开发
先在本地开发测试，确认所有功能正常后再部署到公网。

---

## 📊 服务启动脚本

### 停止所有服务
```bash
pkill -f "node.*server"
pkill -f "python.*stock_service"
```

### 启动所有服务
```bash
# 启动Python后端（后台）
cd /Users/likan/.openclaw/workspace
python3 stock_service.py &

# 启动前端服务（后台）
cd stockbot-frontend
node server-complete.js &
```

### 检查服务状态
```bash
# 查看进程
ps aux | grep -E "node.*server|python.*stock_service" | grep -v grep

# 查看端口
lsof -i :80 -i :5000
```

---

**更新时间**: 2026-03-12 10:35
**状态**: 本地服务正常，公网待确认
