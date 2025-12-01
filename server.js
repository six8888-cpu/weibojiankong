const express = require('express');
const axios = require('axios');
const TelegramBot = require('node-telegram-bot-api');
const cron = require('node-cron');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// 中间件
app.use(express.json());
app.use(express.static('public'));

// 数据文件路径
const CONFIG_FILE = path.join(__dirname, 'data', 'config.json');
const USERS_FILE = path.join(__dirname, 'data', 'monitored_users.json');
const CACHE_FILE = path.join(__dirname, 'data', 'cache.json');

// 确保数据目录存在
if (!fs.existsSync('data')) {
    fs.mkdirSync('data');
}

// 初始化数据文件
function initDataFiles() {
    if (!fs.existsSync(CONFIG_FILE)) {
        fs.writeFileSync(CONFIG_FILE, JSON.stringify({
            rapidApiKey: '',
            telegramBotToken: '',
            telegramChatId: '',
            checkInterval: 5
        }, null, 2));
    }
    if (!fs.existsSync(USERS_FILE)) {
        fs.writeFileSync(USERS_FILE, JSON.stringify([], null, 2));
    }
    if (!fs.existsSync(CACHE_FILE)) {
        fs.writeFileSync(CACHE_FILE, JSON.stringify({}, null, 2));
    }
}

initDataFiles();

// 读取配置
function getConfig() {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
}

// 保存配置
function saveConfig(config) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// 读取监控用户列表
function getMonitoredUsers() {
    return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
}

// 保存监控用户列表
function saveMonitoredUsers(users) {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

// 读取缓存
function getCache() {
    return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
}

// 保存缓存
function saveCache(cache) {
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
}

// Telegram Bot 实例
let bot = null;

// 初始化 Telegram Bot
function initTelegramBot() {
    const config = getConfig();
    if (config.telegramBotToken) {
        try {
            bot = new TelegramBot(config.telegramBotToken, { polling: false });
            console.log('✅ Telegram Bot 已初始化');
        } catch (error) {
            console.error('❌ 初始化Telegram Bot失败:', error.message);
        }
    }
}

// 发送 Telegram 消息
async function sendTelegramMessage(message) {
    const config = getConfig();
    if (!bot || !config.telegramChatId) {
        console.log('⚠️  Telegram未配置，跳过发送消息');
        return false;
    }
    
    try {
        await bot.sendMessage(config.telegramChatId, message, { parse_mode: 'HTML' });
        console.log('✅ Telegram消息已发送');
        return true;
    } catch (error) {
        console.error('❌ 发送Telegram消息失败:', error.message);
        return false;
    }
}

// ============================================
// Twitter API 调用相关（等待实现）
// ============================================

// 调用 Twitter API 的基础函数
async function callTwitterAPI(endpoint, params = {}) {
    const config = getConfig();
    if (!config.rapidApiKey) {
        throw new Error('RapidAPI Key未配置');
    }

    const queryString = Object.keys(params).map(key => `${key}=${params[key]}`).join('&');
    const fullUrl = `https://twitter241.p.rapidapi.com/${endpoint}?${queryString}`;
    
    console.log(`📡 API请求: ${fullUrl}`);

    try {
        const response = await axios.get(`https://twitter241.p.rapidapi.com/${endpoint}`, {
            params: params,
            headers: {
                'x-rapidapi-key': config.rapidApiKey,
                'x-rapidapi-host': 'twitter241.p.rapidapi.com'
            },
            timeout: 15000
        });
        console.log(`✅ API请求成功: ${endpoint}`);
        return response.data;
    } catch (error) {
        if (error.response) {
            console.error(`❌ API请求失败 (${endpoint}):`, error.response.status, error.response.statusText);
            if (error.response.data) {
                console.error(`   错误响应:`, JSON.stringify(error.response.data).substring(0, 200));
            }
        } else {
            console.error(`❌ API请求失败 (${endpoint}):`, error.message);
        }
        throw error;
    }
}

// ============================================
// API 路由
// ============================================

// 获取配置
app.get('/api/config', (req, res) => {
    const config = getConfig();
    res.json({
        ...config,
        rapidApiKey: config.rapidApiKey ? '已配置' : '',
        telegramBotToken: config.telegramBotToken ? '已配置' : ''
    });
});

// 保存配置
app.post('/api/config', (req, res) => {
    try {
        const config = getConfig();
        const newConfig = { ...config, ...req.body };
        
        if (req.body.rapidApiKey && req.body.rapidApiKey !== '已配置') {
            newConfig.rapidApiKey = req.body.rapidApiKey;
        }
        if (req.body.telegramBotToken && req.body.telegramBotToken !== '已配置') {
            newConfig.telegramBotToken = req.body.telegramBotToken;
            initTelegramBot();
        }
        
        saveConfig(newConfig);
        
        res.json({ success: true, message: '配置已保存' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 获取监控用户列表
app.get('/api/users', (req, res) => {
    const users = getMonitoredUsers();
    res.json(users);
});

// 添加监控用户（等待实现）
app.post('/api/users', async (req, res) => {
    try {
        const { username } = req.body;
        
        if (!username) {
            return res.status(400).json({ success: false, message: '用户名不能为空' });
        }
        
        console.log(`📝 准备添加用户: ${username}`);
        
        // TODO: 实现获取用户信息的逻辑
        
        res.json({ success: false, message: '功能待实现，请等待指导' });
    } catch (error) {
        console.error('❌ 添加用户失败:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 更新监控用户
app.put('/api/users/:userId', (req, res) => {
    try {
        const { userId } = req.params;
        const users = getMonitoredUsers();
        
        const userIndex = users.findIndex(u => String(u.userId) === String(userId));
        if (userIndex === -1) {
            return res.status(404).json({ success: false, message: '用户不存在' });
        }
        
        users[userIndex] = { ...users[userIndex], ...req.body };
        saveMonitoredUsers(users);
        
        res.json({ success: true, message: '用户更新成功' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 删除监控用户
app.delete('/api/users/:userId', (req, res) => {
    try {
        const { userId } = req.params;
        let users = getMonitoredUsers();
        
        users = users.filter(u => String(u.userId) !== String(userId));
        saveMonitoredUsers(users);
        
        const cache = getCache();
        delete cache[userId];
        delete cache[String(userId)];
        saveCache(cache);
        
        res.json({ success: true, message: '用户删除成功' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 手动执行监控（等待实现）
app.post('/api/monitor/run', async (req, res) => {
    try {
        res.json({ success: false, message: '监控功能待实现' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 测试Telegram
app.post('/api/test-telegram', async (req, res) => {
    try {
        const success = await sendTelegramMessage('🔔 测试消息：Twitter监控系统运行正常！');
        if (success) {
            res.json({ success: true, message: 'Telegram消息已发送' });
        } else {
            res.json({ success: false, message: 'Telegram发送失败，请检查配置' });
        }
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`\n========================================`);
    console.log(`  Twitter 监控系统 - 基础版`);
    console.log(`========================================`);
    console.log(`✅ 服务器运行在 http://localhost:${PORT}`);
    console.log(`⏳ 等待配置和功能实现...\n`);
    initTelegramBot();
});
