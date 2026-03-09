const express = require('express');
const path = require('path');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = 80;

// CORS 配置
const corsOptions = {
    origin: function(origin, callback) {
        callback(null, true);
    },
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', "Authorization", "x-openclaw-agent-id"]
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

// 启动 Gateway
function startGateway() {
    console.log('[Gateway] 启动中...');
    
    const gatewayProcess = spawn('openclaw', ['gateway'], {
        detached: true,
        stdio: 'ignore'
    });

    gatewayProcess.stdout.on('data', (data) => {
        console.log('[Gateway stdout] ' + data.toString());
    });

    gatewayProcess.stderr.on('data', (data) => {
        console.error('[Gateway stderr] ' + data.toString());
    });

    gatewayProcess.on('error', (err) => {
        console.error('[Gateway 错误] ' + err);
    });

    gatewayProcess.on('close', (code) => {
        console.log('[Gateway 退出] 代码: ' + code);
    });

    return gatewayProcess;
}

// 延迟启动 Gateway
setTimeout(() => {
    startGateway();
}, 2000);

// HTTP 服务器启动
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log('[HTTP] 服务器已启动');
    console.log('[HTTP] 前端: http://localhost:' + PORT + '/stock-analysis-final.html');
    console.log('[HTTP] 后端: http://localhost:18789/v1/chat/completions');
    console.log('[Gateway] 进程启动中...');
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('');
    console.log('[HTTP] 正在关闭服务器...');
    server.close(() => {
        console.log('[HTTP] 服务器已关闭');
        process.exit(0);
    });
});
