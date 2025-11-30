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
            checkInterval: 5 // 检查间隔（分钟）
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
        } catch (error) {
            console.error('初始化Telegram Bot失败:', error.message);
        }
    }
}

// 发送 Telegram 消息
async function sendTelegramMessage(message) {
    const config = getConfig();
    if (!bot || !config.telegramChatId) {
        console.log('Telegram未配置，跳过发送消息');
        return;
    }
    
    try {
        await bot.sendMessage(config.telegramChatId, message, { parse_mode: 'HTML' });
        console.log('Telegram消息已发送');
    } catch (error) {
        console.error('发送Telegram消息失败:', error.message);
    }
}

// 调用 Twitter API
async function callTwitterAPI(endpoint, params = {}) {
    const config = getConfig();
    if (!config.rapidApiKey) {
        throw new Error('RapidAPI Key未配置');
    }

    try {
        const response = await axios.get(`https://twitter241.p.rapidapi.com/${endpoint}`, {
            params: params,
            headers: {
                'X-RapidAPI-Key': config.rapidApiKey,
                'X-RapidAPI-Host': 'twitter241.p.rapidapi.com'
            },
            timeout: 15000
        });
        return response.data;
    } catch (error) {
        if (error.response) {
            console.error(`调用Twitter API失败 (${endpoint}):`, error.response.status, error.response.statusText);
            console.error('请求参数:', JSON.stringify(params));
        } else {
            console.error(`调用Twitter API失败 (${endpoint}):`, error.message);
        }
        throw error;
    }
}

// 获取用户信息
async function getUserByUsername(username) {
    return await callTwitterAPI('user', { username });
}

// 获取用户推文
async function getUserTweets(userId, count = 20) {
    console.log(`调用 user-tweets API, 用户ID: ${userId}, 数量: ${count}`);
    return await callTwitterAPI('user-tweets', { user: userId, count: count });
}

// 获取用户回复
async function getUserReplies(userId, count = 20) {
    console.log(`调用 user-replies API, 用户ID: ${userId}, 数量: ${count}`);
    return await callTwitterAPI('user-replies', { user: userId, count: count });
}

// 获取推文的转发列表
async function getPostRetweets(postId, count = 40) {
    console.log(`调用 retweets API, 推文ID: ${postId}, 数量: ${count}`);
    return await callTwitterAPI('retweets', { pid: postId, count: count });
}

// 检查新推文
async function checkNewTweets(user) {
    try {
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const tweets = await getUserTweets(user.userId, 20);
        
        if (!tweets || !tweets.result || !tweets.result.timeline || !tweets.result.timeline.instructions) {
            return;
        }

        // 解析推文数据
        const entries = tweets.result.timeline.instructions
            .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        
        const tweetEntries = entries.filter(e => e.entryId.startsWith('tweet-'));
        
        if (tweetEntries.length === 0) return;

        // 初始化缓存
        if (!userCache.lastTweetId) {
            userCache.lastTweetId = tweetEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);
            return;
        }

        // 检查新推文
        const newTweets = [];
        for (const entry of tweetEntries) {
            if (entry.sortIndex > userCache.lastTweetId) {
                const tweetData = entry.content?.itemContent?.tweet_results?.result;
                if (tweetData && tweetData.legacy) {
                    newTweets.push(tweetData.legacy);
                }
            }
        }

        if (newTweets.length > 0) {
            userCache.lastTweetId = tweetEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);

            for (const tweet of newTweets.reverse()) {
                const message = `
🐦 <b>新推文通知</b>

👤 用户: @${user.username}
📝 内容: ${tweet.full_text || tweet.text}
🔗 链接: https://twitter.com/${user.username}/status/${tweet.id_str}
⏰ 时间: ${new Date(tweet.created_at).toLocaleString('zh-CN')}
                `.trim();
                
                await sendTelegramMessage(message);
            }
        }
    } catch (error) {
        console.error(`检查用户 ${user.username} 的新推文失败:`, error.message);
    }
}

// 检查推文回复
async function checkNewReplies(user) {
    try {
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const replies = await getUserReplies(user.userId, 20);
        
        if (!replies || !replies.result || !replies.result.timeline || !replies.result.timeline.instructions) {
            return;
        }

        // 解析回复数据
        const entries = replies.result.timeline.instructions
            .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        
        const replyEntries = entries.filter(e => e.entryId.startsWith('tweet-'));
        
        if (replyEntries.length === 0) return;

        // 初始化缓存
        if (!userCache.lastReplyId) {
            userCache.lastReplyId = replyEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);
            return;
        }

        // 检查新回复
        const newReplies = [];
        for (const entry of replyEntries) {
            if (entry.sortIndex > userCache.lastReplyId) {
                const replyData = entry.content?.itemContent?.tweet_results?.result;
                if (replyData && replyData.legacy) {
                    newReplies.push(replyData.legacy);
                }
            }
        }

        if (newReplies.length > 0) {
            userCache.lastReplyId = replyEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);

            for (const reply of newReplies.reverse()) {
                const message = `
💬 <b>新回复通知</b>

👤 用户: @${user.username}
📝 回复内容: ${reply.full_text || reply.text}
🔗 链接: https://twitter.com/${user.username}/status/${reply.id_str}
⏰ 时间: ${new Date(reply.created_at).toLocaleString('zh-CN')}
                `.trim();
                
                await sendTelegramMessage(message);
            }
        }
    } catch (error) {
        console.error(`检查用户 ${user.username} 的新回复失败:`, error.message);
    }
}

// 检查置顶推文
async function checkPinnedTweet(user) {
    try {
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const userData = await getUserByUsername(user.username);
        
        if (!userData || !userData.result) return;

        const pinnedTweetId = userData.result.legacy?.pinned_tweet_ids_str?.[0];
        
        if (!pinnedTweetId) return;

        // 初始化缓存
        if (!userCache.pinnedTweetId) {
            userCache.pinnedTweetId = pinnedTweetId;
            cache[user.userId] = userCache;
            saveCache(cache);
            return;
        }

        // 检查置顶推文是否变化
        if (pinnedTweetId !== userCache.pinnedTweetId) {
            userCache.pinnedTweetId = pinnedTweetId;
            cache[user.userId] = userCache;
            saveCache(cache);

            const message = `
📌 <b>置顶推文变化通知</b>

👤 用户: @${user.username}
🔗 新置顶推文: https://twitter.com/${user.username}/status/${pinnedTweetId}
⏰ 检测时间: ${new Date().toLocaleString('zh-CN')}
            `.trim();
            
            await sendTelegramMessage(message);
        }
    } catch (error) {
        console.error(`检查用户 ${user.username} 的置顶推文失败:`, error.message);
    }
}

// 检查转发推文
async function checkRetweets(user) {
    try {
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const tweets = await getUserTweets(user.userId, 20);
        
        if (!tweets || !tweets.result || !tweets.result.timeline || !tweets.result.timeline.instructions) {
            return;
        }

        // 解析推文数据
        const entries = tweets.result.timeline.instructions
            .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        
        const tweetEntries = entries.filter(e => e.entryId.startsWith('tweet-'));
        
        if (!userCache.checkedRetweets) {
            userCache.checkedRetweets = {};
        }

        // 检查转发
        for (const entry of tweetEntries) {
            const tweetData = entry.content?.itemContent?.tweet_results?.result;
            if (tweetData && tweetData.legacy) {
                const tweet = tweetData.legacy;
                
                // 检查是否是转发
                if (tweet.retweeted_status_result) {
                    const tweetId = tweet.id_str;
                    
                    if (!userCache.checkedRetweets[tweetId]) {
                        userCache.checkedRetweets[tweetId] = true;
                        
                        const originalTweet = tweet.retweeted_status_result.result?.legacy;
                        const originalUser = tweet.retweeted_status_result.result?.core?.user_results?.result?.legacy;
                        
                        const message = `
🔄 <b>转发推文通知</b>

👤 用户: @${user.username}
📝 转发了: @${originalUser?.screen_name || '未知用户'}
💭 原文: ${originalTweet?.full_text || originalTweet?.text || '无内容'}
🔗 链接: https://twitter.com/${user.username}/status/${tweetId}
⏰ 时间: ${new Date(tweet.created_at).toLocaleString('zh-CN')}
                        `.trim();
                        
                        await sendTelegramMessage(message);
                    }
                }
            }
        }

        cache[user.userId] = userCache;
        saveCache(cache);
    } catch (error) {
        console.error(`检查用户 ${user.username} 的转发推文失败:`, error.message);
    }
}

// 执行监控任务
async function runMonitoringTask() {
    console.log('开始执行监控任务...', new Date().toLocaleString('zh-CN'));
    
    const users = getMonitoredUsers();
    
    for (const user of users) {
        if (!user.enabled) continue;
        
        console.log(`检查用户: @${user.username}`);
        
        try {
            // 检查新推文
            if (user.monitorTweets) {
                await checkNewTweets(user);
            }
            
            // 检查回复
            if (user.monitorReplies) {
                await checkNewReplies(user);
            }
            
            // 检查置顶推文
            if (user.monitorPinned) {
                await checkPinnedTweet(user);
            }
            
            // 检查转发
            if (user.monitorRetweets) {
                await checkRetweets(user);
            }
            
            // 延迟，避免API限制
            await new Promise(resolve => setTimeout(resolve, 2000));
        } catch (error) {
            console.error(`监控用户 ${user.username} 时出错:`, error.message);
        }
    }
    
    console.log('监控任务完成');
}

// 定时任务
let cronJob = null;

function startCronJob() {
    if (cronJob) {
        cronJob.stop();
    }
    
    const config = getConfig();
    const interval = config.checkInterval || 5;
    
    // 每N分钟执行一次
    cronJob = cron.schedule(`*/${interval} * * * *`, () => {
        runMonitoringTask();
    });
    
    console.log(`定时任务已启动，每 ${interval} 分钟执行一次`);
}

// API 路由

// 获取配置
app.get('/api/config', (req, res) => {
    const config = getConfig();
    // 不返回敏感信息的完整内容
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
        
        // 如果提供了完整的key，则更新
        if (req.body.rapidApiKey && req.body.rapidApiKey !== '已配置') {
            newConfig.rapidApiKey = req.body.rapidApiKey;
        }
        if (req.body.telegramBotToken && req.body.telegramBotToken !== '已配置') {
            newConfig.telegramBotToken = req.body.telegramBotToken;
            initTelegramBot();
        }
        
        saveConfig(newConfig);
        
        // 重启定时任务
        startCronJob();
        
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

// 添加监控用户
app.post('/api/users', async (req, res) => {
    try {
        const { username } = req.body;
        
        if (!username) {
            return res.status(400).json({ success: false, message: '用户名不能为空' });
        }
        
        console.log(`尝试添加用户: ${username}`);
        
        // 获取用户信息
        const userData = await getUserByUsername(username);
        
        console.log(`获取用户信息结果:`, JSON.stringify(userData, null, 2));
        
        if (!userData || !userData.result) {
            return res.status(404).json({ success: false, message: '用户不存在' });
        }
        
        const userId = userData.result.rest_id;
        console.log(`用户 @${username} 的ID: ${userId} (类型: ${typeof userId})`);
        
        const users = getMonitoredUsers();
        
        // 检查是否已存在
        if (users.find(u => u.userId === userId)) {
            return res.status(400).json({ success: false, message: '该用户已在监控列表中' });
        }
        
        // 添加用户
        const newUser = {
            userId,
            username,
            displayName: userData.result.legacy?.name || username,
            enabled: true,
            monitorTweets: true,
            monitorReplies: true,
            monitorPinned: true,
            monitorRetweets: true,
            addedAt: new Date().toISOString()
        };
        
        console.log(`保存用户数据:`, JSON.stringify(newUser, null, 2));
        
        users.push(newUser);
        saveMonitoredUsers(users);
        
        res.json({ success: true, message: '用户添加成功' });
    } catch (error) {
        console.error('添加用户失败:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 更新监控用户
app.put('/api/users/:userId', (req, res) => {
    try {
        const { userId } = req.params;
        const users = getMonitoredUsers();
        
        const userIndex = users.findIndex(u => u.userId === userId);
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
        console.log(`删除用户请求，userId: ${userId} (类型: ${typeof userId})`);
        
        let users = getMonitoredUsers();
        const beforeCount = users.length;
        console.log(`删除前用户数量: ${beforeCount}`);
        
        // 使用字符串比较（因为URL参数总是字符串）
        users = users.filter(u => {
            const match = String(u.userId) !== String(userId);
            if (!match) {
                console.log(`找到匹配用户: ${u.username} (ID: ${u.userId})`);
            }
            return match;
        });
        
        const afterCount = users.length;
        console.log(`删除后用户数量: ${afterCount}`);
        
        if (beforeCount === afterCount) {
            console.warn(`警告: 没有找到ID为 ${userId} 的用户`);
            return res.status(404).json({ success: false, message: '用户不存在' });
        }
        
        saveMonitoredUsers(users);
        
        // 清理缓存
        const cache = getCache();
        delete cache[userId];
        delete cache[String(userId)]; // 同时删除字符串形式的key
        saveCache(cache);
        
        console.log(`✅ 用户删除成功`);
        res.json({ success: true, message: '用户删除成功' });
    } catch (error) {
        console.error('删除用户失败:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 手动执行监控
app.post('/api/monitor/run', async (req, res) => {
    try {
        res.json({ success: true, message: '监控任务已启动' });
        // 异步执行
        runMonitoringTask();
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 测试Telegram
app.post('/api/test-telegram', async (req, res) => {
    try {
        await sendTelegramMessage('🔔 测试消息：Twitter监控系统运行正常！');
        res.json({ success: true, message: 'Telegram消息已发送' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`服务器运行在 http://localhost:${PORT}`);
    initTelegramBot();
    startCronJob();
    console.log('Twitter监控系统已启动！');
});

