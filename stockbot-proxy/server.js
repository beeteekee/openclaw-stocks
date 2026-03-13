const express = require('express');
const http = require('http');
const cors = require('cors');

const app = express();
const PROXY_PORT = 80;
const GATEWAY_PORT = 18789;
const FLASK_PORT = 5000;
const TARGET_HOST = 'localhost';

// 静态文件服务
app.use(express.static(__dirname + '/public'));

// CORS 配置
app.use(cors({
    origin: '*',
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'x-openclaw-agent-id']
}));

// 代理函数（简化版，不依赖 HTTP 库）
function proxyRequest(req, res) {
    const options = {
        hostname: TARGET_HOST,
        port: TARGET_PORT,
        path: req.url,
        method: req.method,
        headers: {
            'host': TARGET_HOST + ':' + TARGET_PORT,
            'x-forwarded-host': req.headers['host'],
            'x-forwarded-proto': req.protocol || 'http',
            ...req.headers
        }
    };

    console.log('[代理] ' + req.method + ' ' + req.url + ' -> ' + TARGET_HOST + ':' + TARGET_PORT + req.url);

    const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
        console.error('[代理错误]', err);
        if (!res.headersSent) {
            res.status(500).json({ error: '代理错误', message: err.message });
        }
    });

    proxyReq.on('timeout', () => {
        console.error('[代理超时]');
        if (!res.headersSent) {
            res.status(504).json({ error: '代理超时' });
        }
    });

    req.pipe(proxyReq);
}

// 健康检查
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'stockbot-proxy',
        proxy_port: PROXY_PORT,
        target: TARGET_HOST + ':' + TARGET_PORT,
        timestamp: new Date().toISOString()
    });
});

// 请求超时（120秒 - 支持完整的股票分析）
const REQUEST_TIMEOUT = 120000;

// 代理 Flask API 请求（股票分析）
app.all('/api/*', (req, res) => {
    const options = {
        hostname: TARGET_HOST,
        port: FLASK_PORT,
        path: req.url,
        method: req.method,
        headers: {
            'host': TARGET_HOST + ':' + FLASK_PORT,
            'x-forwarded-host': req.headers['host'],
            'x-forwarded-proto': req.protocol || 'http',
            ...req.headers
        }
    };

    console.log('[代理 Flask API] ' + req.method + ' ' + req.url + ' -> ' + TARGET_HOST + ':' + FLASK_PORT + req.url);

    res.setTimeout(REQUEST_TIMEOUT);

    const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
        console.error('[Flask 代理错误]', err);
        if (!res.headersSent) {
            res.status(500).json({ error: 'Flask服务错误', message: err.message });
        }
    });

    req.pipe(proxyReq);
});

// 代理 Gateway 请求（OpenClaw API）
app.all('/v1/*', (req, res) => {
    console.log('[代理 Gateway] 收到请求:', req.method, req.url);

    res.setTimeout(REQUEST_TIMEOUT);

    proxyRequest(req, res);
});

// 404 处理
app.use((req, res) => {
    res.status(404).json({ error: 'Not Found', path: req.url });
});

// 启动服务器
const server = app.listen(PROXY_PORT, '0.0.0.0', () => {
    console.log('');
    console.log('╔════════════════════════════════════════════╗');
    console.log('║           🌐 股票分析代理服务器已启动               ║');
    console.log('╚═══════════════════════════════════════════════╝');
    console.log('');
    console.log('📋 服务信息');
    console.log('   代理端口:   ' + PROXY_PORT + ' (外网 80 端口转发）');
    console.log('   Flask服务:   ' + TARGET_HOST + ':' + FLASK_PORT + ' (股票分析API）');
    console.log('   Gateway服务: ' + TARGET_HOST + ':' + GATEWAY_PORT + ' (OpenClaw Gateway）');
    console.log('');
    console.log('🌐 访问地址');
    console.log('   外网网页:   http://stockbot.nat100.top/stock-analysis.html');
    console.log('   本地网页:   http://localhost:' + PROXY_PORT + '/stock-analysis.html');
    console.log('');
    console.log('🔧 代理配置');
    console.log('   /api/*   -> Flask:5000 (股票分析）');
    console.log('   /v1/*    -> Gateway:' + GATEWAY_PORT + ' (OpenClaw API）');
    console.log('   /*       -> 静态文件 (public/）');
    console.log('');
    console.log('💡 使用提示');
    console.log('   - 停止代理服务器: Ctrl + C');
    console.log('   - 重启代理服务器: npm start');
    console.log('   - HTML文件需放在 stockbot-proxy/public/ 目录');
    console.log('');
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('');
    console.log('🛑 正在关闭代理服务器...');
    server.close(() => {
        console.log('✅ 代理服务器已关闭');
        process.exit(0);
    });
});
