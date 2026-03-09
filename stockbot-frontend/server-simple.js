const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 80;

// CORS 配置
const corsOptions = {
    origin: function(origin, callback) {
        callback(null, true);
    },
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'x-openclaw-agent-id']
};

// 静态文件服务
app.use(express.static(path.join(__dirname, 'public')));

// CORS 中间件
app.use(cors(corsOptions));

// 日志中间件
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log('[' + timestamp + '] ' + req.method + ' ' + req.url);
    next();
});

// 健康检查
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'stockbot-frontend',
        port: PORT,
        timestamp: new Date().toISOString()
    });
});

// HTTP 服务器启动（不自动启动 Gateway）
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log('');
    console.log('╔════════════════════════════════════════════╗');
    console.log('║  股票分析前端服务器已启动');
    console.log('╚═══════════════════════════════════════════╗');
    console.log('║                                                  ║');
    console.log('║  前端服务    http://localhost:' + PORT + '                    ║');
    console.log('║  静态页面    public/stock-analysis-final.html            ║');
    console.log('║  API 服务    http://localhost:18789               ║');
    console.log('║                                                  ║');
    console.log('║  注意: 需要手动启动 Gateway (openclaw gateway)       ║');
    console.log('║                                                  ║');
    console.log('╚════════════════════════════════════════════╝');
    console.log('');
    console.log('使用方法:');
    console.log('  1. 在浏览器中访问: http://localhost:' + PORT + '/stock-analysis-final.html');
    console.log('  2. 确保 Gateway 正在运行: openclaw gateway');
    console.log('');
    console.log('停止服务器: Ctrl + C');
    console.log('');
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('');
    console.log('正在关闭服务器...');
    server.close(() => {
        console.log('服务器已关闭');
        process.exit(0);
    });
});
