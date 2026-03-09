# 股票分析前端工程

## 项目结构
```
stockbot-frontend/
├── package.json          # 项目依赖
├── server.js            # Express 服务器（启动时自动启动 OpenClaw Gateway）
├── public/             # 静态文件目录
│   └── stock-analysis-final.html  # 股票分析页面
├── README.md           # 项目说明
└── .gitignore          # Git 忽略文件
```

## 功能特点

### 🌐 前端服务器
- **Express.js** - 提供 HTTP 静态文件服务
- **端口 80** - 默认 HTTP 端口
- **CORS 支持** - 允许所有来源访问
- **自动启动 Gateway** - 服务器启动时自动启动 OpenClaw Gateway
- **日志记录** - 详细的请求日志
- **优雅退出** - Ctrl+C 正常关闭

### 📊 股票分析页面
- **HTTP API** - 直接调用 OpenClaw Gateway 的 OpenAI 兼容 API
- **Token 认证** - 自动配置 Gateway Token
- **30 秒超时** - 避免请求一直等待
- **详细调试信息** - 显示 API 请求和响应
- **快速示例** - 预设热门股票标签

### 🚀 启动方式

#### 方式 1：使用 npm（推荐）
```bash
cd /Users/likan/.openclaw/workspace/stockbot-frontend
npm install
npm start
```

#### 方式 2：使用 nodemon（开发模式）
```bash
cd /Users/likan/.openclaw/workspace/stockbot-frontend
npm install
npm run dev
```

#### 方式 3：直接运行 Node.js（无需安装）
```bash
cd /Users/likan/.openclaw/workspace/stockbot-frontend
node server.js
```

## 访问地址

### 🌐 前端服务器（80 端口）
```
http://localhost
http://stockbot.nat100.top:80  # 如果配置了端口转发 80→内网
```

### 📊 页面路径
```
http://localhost/stock-analysis-final.html
http://localhost:stock-analysis.html  # 备用版本
```

### 🤖 后端 API（Gateway）
```
http://localhost:18789/v1/chat/completions
http://stockbot.nat100.top/v1/chat/completions
```

## 配置说明

### API 配置
页面中已配置以下 API 信息（在 `stock-analysis-final.html` 第 45-47 行）：
- **API URL**: `http://localhost:18789/v1/chat/completions`
- **API Token**: `2047e3763a3a15acfb3ef96e3c40eac23a59500c9c3f436b`
- **Agent ID**: `stock-analysis`

### CORS 配置
服务器已配置允许所有来源访问：
```javascript
const corsOptions = {
    origin: function(origin, callback) {
        callback(null, true); // 允许所有来源
    },
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'x-openclaw-agent-id']
};
```

## 故障排查

### 问题 1：前端服务器无法启动
**可能原因**：
- 80 端口被占用
- node_modules 未安装

**解决方法**：
```bash
# 检查端口占用
lsof -i :80

# 安装依赖
cd /Users/likan/.openclaw/workspace/stockbot-frontend
npm install

# 更改端口（如果需要）
# 编辑 server.js，修改 PORT = 8080
```

### 问题 2：页面显示"连接失败"
**可能原因**：
- Gateway 未运行
- Gateway 端口不是 18789
- Token 配置错误

**解决方法**：
```bash
# 检查 Gateway 是否运行
ps aux | grep openclaw-gateway

# 检查端口
lsof -i :18789

# 重启 Gateway（如果需要）
openclaw gateway restart
```

### 问题 3：API 请求超时
**可能原因**：
- Gateway 响应慢
- 网络问题

**解决方法**：
- 查看页面调试信息中的"最后响应"字段
- 查看页面底部显示的状态码

### 问题 4：返回"Unauthorized"错误
**可能原因**：
- Token 配置错误或过期

**解决方法**：
- 检查 Gateway 配置中的 Token
- 运行：`openclaw gateway config.get`
- 更新页面中的 Token（server.js 第 45 行附近）

## 开发建议

### 本地开发
1. 使用 `nodemon` 启动，修改代码后自动重启
2. 查看终端日志了解请求情况
3. 使用浏览器开发者工具（F12）查看网络请求

### 生产部署
1. 使用 PM2 管理进程：`npm install -g pm2`
2. 使用 Nginx 做反向代理
3. 配置 SSL 证书使用 HTTPS
4. 设置防火墙规则开放 80 和 18789 端口

## 更新日志

### 2026-02-14
- ✅ 创建完整前端工程项目
- ✅ 配置 Express 服务器
- ✅ 集成 OpenClaw Gateway 自动启动
- ✅ 复制股票分析页面到 public 目录
- ✅ 添加 CORS 支持
- ✅ 添加详细调试信息
- ✅ 创建项目文档

## 技术栈

- **前端服务器**: Node.js + Express.js
- **后端服务**: OpenClaw Gateway (WebSocket + HTTP API)
- **前端页面**: 原生 HTML + Vanilla JavaScript
- **API 协议**: OpenAI Chat Completions (HTTP)
- **认证方式**: Bearer Token
- **端口**: 前端 80，后端 18789

## 联系与支持

如遇问题，请检查：
1. 项目目录是否正确
2. 依赖是否已安装
3. Gateway 服务是否正常运行
4. 网络连接是否稳定

---

**开始使用：**
```bash
cd /Users/likan/.openclaw/workspace/stockbot-frontend
npm install
npm start
```
