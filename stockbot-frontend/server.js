const express = require('express');
const path = require('path');
const cors = require('cors');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = 80;

// 统计数据文件路径
const STATS_FILE = path.join(__dirname, 'stats.json');

// 初始化统计数据
function initStats() {
    if (!fs.existsSync(STATS_FILE)) {
        const today = new Date().toISOString().split('T')[0];
        const initialData = {
            daily: {
                [today]: {
                    date: today,
                    queryCount: 0,
                    stockCount: 0,
                    stocks: {}
                }
            }
        };
        fs.writeFileSync(STATS_FILE, JSON.stringify(initialData, null, 2));
    }
}

// 读取统计数据
function readStats() {
    try {
        const data = fs.readFileSync(STATS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('读取统计数据失败:', error);
        return { daily: {} };
    }
}

// 保存统计数据
function saveStats(stats) {
    try {
        fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2));
    } catch (error) {
        console.error('保存统计数据失败:', error);
    }
}

// 记录查询
function recordQuery(stockCode) {
    const stats = readStats();
    const today = new Date().toISOString().split('T')[0];

    if (!stats.daily[today]) {
        stats.daily[today] = {
            date: today,
            queryCount: 0,
            stockCount: 0,
            stocks: {}
        };
    }

    stats.daily[today].queryCount++;

    // 记录股票代码（只统计不同的股票）
    if (stockCode && !stats.daily[today].stocks[stockCode]) {
        stats.daily[today].stocks[stockCode] = true;
        stats.daily[today].stockCount++;
    }

    saveStats(stats);
}

// 获取前一天的统计数据
function getPreviousDayStats() {
    const stats = readStats();
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayDate = yesterday.toISOString().split('T')[0];

    const yesterdayStats = stats.daily[yesterdayDate];

    if (!yesterdayStats) {
        // 如果没有昨天的数据，返回默认值
        return {
            date: yesterdayDate,
            queryCount: 0,
            stockCount: 0
        };
    }

    return {
        date: yesterdayStats.date,
        queryCount: yesterdayStats.queryCount,
        stockCount: yesterdayStats.stockCount
    };
}

// 初始化统计数据
initStats();

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
    console.log(`[${timestamp}] ${req.method} ${req.url}`);
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

// 记录查询统计
app.post('/api/stats/record', (req, res) => {
    try {
        const { stockCode } = req.body;
        recordQuery(stockCode);
        res.json({ success: true });
    } catch (error) {
        console.error('记录统计失败:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取前一天的统计数据
app.get('/api/stats/previous', (req, res) => {
    try {
        const stats = getPreviousDayStats();
        res.json(stats);
    } catch (error) {
        console.error('获取统计数据失败:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// 启动 OpenClaw Gateway 的函数
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

// 延迟启动 Gateway（等待 2 秒）
setTimeout(() => {
    startGateway();
}, 2000);

// HTTP 服务器启动
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log('');
    console.log('[HTTP] 服务器已启动');
    console.log('[HTTP] 前端: http://localhost:' + PORT + '/stock-analysis-final.html');
    console.log('[HTTP] 后端: http://localhost:18789/v1/chat/completions');
    console.log('');
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
