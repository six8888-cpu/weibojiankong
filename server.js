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

    // 构建完整的URL用于日志
    const queryString = Object.keys(params).map(key => `${key}=${params[key]}`).join('&');
    const fullUrl = `https://twitter241.p.rapidapi.com/${endpoint}?${queryString}`;
    
    console.log(`📡 API请求: ${fullUrl}`);
    console.log(`   参数:`, JSON.stringify(params));

    try {
        // 确保用户ID是字符串格式（API要求）
        const processedParams = { ...params };
        if (processedParams.user) {
            processedParams.user = String(processedParams.user);
        }
        if (processedParams.pid) {
            processedParams.pid = String(processedParams.pid);
        }
        
        const response = await axios.get(`https://twitter241.p.rapidapi.com/${endpoint}`, {
            params: processedParams,
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
            console.error(`   完整URL: ${fullUrl}`);
            console.error(`   请求参数:`, JSON.stringify(params));
            if (error.response.data) {
                console.error(`   错误响应:`, JSON.stringify(error.response.data).substring(0, 200));
            }
        } else {
            console.error(`❌ API请求失败 (${endpoint}):`, error.message);
            console.error(`   完整URL: ${fullUrl}`);
        }
        throw error;
    }
}

// 获取用户信息 - 使用 about-account 端点
async function getUserByUsername(username) {
    console.log(`📡 获取用户信息: /about-account?username=${username}`);
    return await callTwitterAPI('about-account', { username });
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

// 获取用户的转发推文（pid使用用户的rest_id）
async function getUserRetweets(userId, count = 40) {
    console.log(`调用 retweets API, 用户ID: ${userId}, 数量: ${count}`);
    return await callTwitterAPI('retweets', { pid: userId, count: count });
}

// 获取用户的引用推文（pid使用用户的rest_id）
async function getUserQuotes(userId, count = 40) {
    console.log(`调用 quotes API, 用户ID: ${userId}, 数量: ${count}`);
    return await callTwitterAPI('quotes', { pid: userId, count: count });
}

// 检查新推文
async function checkNewTweets(user) {
    try {
        console.log(`🔍 开始检查新推文 - 用户: @${user.username}, ID: ${user.userId} (类型: ${typeof user.userId})`);
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const tweets = await getUserTweets(user.userId, 20);
        
        // 调试：打印响应结构
        if (tweets) {
            console.log(`📦 API响应结构:`, JSON.stringify(Object.keys(tweets)).substring(0, 200));
            if (tweets.result) {
                console.log(`📦 result结构:`, JSON.stringify(Object.keys(tweets.result)).substring(0, 200));
            }
        }
        
        // 尝试多种可能的响应结构
        let entries = [];
        if (tweets?.result?.timeline?.instructions) {
            // 标准结构
            entries = tweets.result.timeline.instructions
                .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        } else if (tweets?.result?.entries) {
            // 直接entries结构
            entries = tweets.result.entries;
        } else if (tweets?.entries) {
            // 顶层entries结构
            entries = tweets.entries;
        } else if (Array.isArray(tweets)) {
            // 数组结构
            entries = tweets;
        } else {
            console.warn(`⚠️  无法解析API响应结构，响应:`, JSON.stringify(tweets).substring(0, 500));
            return;
        }

        // 解析推文数据
        const tweetEntries = entries.filter(e => {
            const entryId = e.entryId || e.id || e.tweet_id || '';
            return String(entryId).startsWith('tweet-') || String(entryId).includes('tweet');
        });
        
        console.log(`📊 找到 ${tweetEntries.length} 条推文条目`);
        
        if (tweetEntries.length === 0) {
            console.log(`⚠️  没有找到推文条目，可能API返回格式不同`);
            return;
        }

        // 初始化缓存（首次运行，不发送通知）
        if (!userCache.lastTweetId) {
            userCache.lastTweetId = tweetEntries[0].sortIndex;
            userCache.lastCheckTime = Date.now();
            cache[user.userId] = userCache;
            saveCache(cache);
            console.log(`   首次初始化，不发送通知`);
            return;
        }

        // 检查新推文（只通知1分钟内的）
        const now = Date.now();
        const oneMinuteAgo = now - 60 * 1000; // 1分钟前
        const newTweets = [];
        
        for (const entry of tweetEntries) {
            if (entry.sortIndex > userCache.lastTweetId) {
                const tweetData = entry.content?.itemContent?.tweet_results?.result;
                if (tweetData && tweetData.legacy) {
                    const tweet = tweetData.legacy;
                    const tweetTime = new Date(tweet.created_at).getTime();
                    
                    // 只添加1分钟内的推文
                    if (tweetTime >= oneMinuteAgo) {
                        console.log(`   发现新推文: ${tweet.id_str}, 发布时间: ${new Date(tweetTime).toLocaleString('zh-CN')}`);
                        newTweets.push(tweet);
                    } else {
                        console.log(`   跳过旧推文: ${tweet.id_str}, 发布于 ${new Date(tweetTime).toLocaleString('zh-CN')}`);
                    }
                }
            }
        }

        // 更新缓存
        if (tweetEntries.length > 0) {
            userCache.lastTweetId = tweetEntries[0].sortIndex;
            userCache.lastCheckTime = now;
            cache[user.userId] = userCache;
            saveCache(cache);
        }

        // 发送通知（不重复发送）
        if (newTweets.length > 0) {
            console.log(`   准备发送 ${newTweets.length} 条新推文通知`);
            
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
        } else {
            console.log(`   没有1分钟内的新推文`);
        }
    } catch (error) {
        console.error(`检查用户 ${user.username} 的新推文失败:`, error.message);
    }
}

// 检查推文回复
async function checkNewReplies(user) {
    try {
        console.log(`🔍 开始检查新回复 - 用户: @${user.username}, ID: ${user.userId}`);
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const replies = await getUserReplies(user.userId, 20);
        
        // 尝试多种可能的响应结构
        let entries = [];
        if (replies?.result?.timeline?.instructions) {
            entries = replies.result.timeline.instructions
                .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        } else if (replies?.result?.entries) {
            entries = replies.result.entries;
        } else if (replies?.entries) {
            entries = replies.entries;
        } else if (Array.isArray(replies)) {
            entries = replies;
        } else {
            console.warn(`⚠️  无法解析回复API响应结构`);
            return;
        }

        // 解析回复数据
        const replyEntries = entries.filter(e => {
            const entryId = e.entryId || e.id || e.tweet_id || '';
            return String(entryId).startsWith('tweet-') || String(entryId).includes('tweet');
        });
        
        console.log(`📊 找到 ${replyEntries.length} 条回复条目`);
        
        if (replyEntries.length === 0) return;

        // 初始化缓存（首次运行，不发送通知）
        if (!userCache.lastReplyId) {
            userCache.lastReplyId = replyEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);
            console.log(`   首次初始化回复缓存，不发送通知`);
            return;
        }

        // 检查新回复（只通知1分钟内的）
        const now = Date.now();
        const oneMinuteAgo = now - 60 * 1000;
        const newReplies = [];
        
        for (const entry of replyEntries) {
            if (entry.sortIndex > userCache.lastReplyId) {
                const replyData = entry.content?.itemContent?.tweet_results?.result;
                if (replyData && replyData.legacy) {
                    const reply = replyData.legacy;
                    const replyTime = new Date(reply.created_at).getTime();
                    
                    // 只添加1分钟内的回复
                    if (replyTime >= oneMinuteAgo) {
                        console.log(`   发现新回复: ${reply.id_str}`);
                        newReplies.push(reply);
                    } else {
                        console.log(`   跳过旧回复: ${reply.id_str}`);
                    }
                }
            }
        }

        // 更新缓存
        if (replyEntries.length > 0) {
            userCache.lastReplyId = replyEntries[0].sortIndex;
            cache[user.userId] = userCache;
            saveCache(cache);
        }

        // 发送通知
        if (newReplies.length > 0) {
            console.log(`   准备发送 ${newReplies.length} 条新回复通知`);
            
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
        } else {
            console.log(`   没有1分钟内的新回复`);
        }
    } catch (error) {
        console.error(`检查用户 ${user.username} 的新回复失败:`, error.message);
    }
}

// 检查置顶推文
async function checkPinnedTweet(user) {
    try {
        console.log(`🔍 开始检查置顶推文 - 用户: @${user.username}`);
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        const userData = await getUserByUsername(user.username);
        
        if (!userData) {
            console.warn(`⚠️  无法获取用户信息`);
            return;
        }

        // 尝试从不同位置提取置顶推文ID
        let pinnedTweetId = null;
        if (userData.pinned_tweet_ids_str?.[0]) {
            pinnedTweetId = userData.pinned_tweet_ids_str[0];
        } else if (userData.legacy?.pinned_tweet_ids_str?.[0]) {
            pinnedTweetId = userData.legacy.pinned_tweet_ids_str[0];
        } else if (userData.result?.legacy?.pinned_tweet_ids_str?.[0]) {
            pinnedTweetId = userData.result.legacy.pinned_tweet_ids_str[0];
        }
        
        if (!pinnedTweetId) {
            console.log(`   用户没有置顶推文`);
            return;
        }
        
        console.log(`   当前置顶推文ID: ${pinnedTweetId}`);

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
        console.log(`🔍 开始检查转发 - 用户: @${user.username}, ID: ${user.userId}`);
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        // 使用 retweets API，pid 参数使用用户的 rest_id
        const tweets = await getUserRetweets(user.userId, 20);
        
        // 尝试多种可能的响应结构
        let entries = [];
        if (tweets?.result?.timeline?.instructions) {
            entries = tweets.result.timeline.instructions
                .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        } else if (tweets?.result?.entries) {
            entries = tweets.result.entries;
        } else if (tweets?.entries) {
            entries = tweets.entries;
        } else if (Array.isArray(tweets)) {
            entries = tweets;
        } else {
            console.warn(`⚠️  无法解析转发API响应结构`);
            return;
        }

        // 解析转发数据
        const tweetEntries = entries.filter(e => {
            const entryId = e.entryId || e.id || e.tweet_id || '';
            return String(entryId).startsWith('tweet-') || String(entryId).includes('tweet');
        });
        
        console.log(`📊 找到 ${tweetEntries.length} 条转发条目`);
        
        if (!userCache.checkedRetweets) {
            userCache.checkedRetweets = {};
        }

        // 检查转发（只通知1分钟内的）
        const now = Date.now();
        const oneMinuteAgo = now - 60 * 1000;
        let newRetweetsCount = 0;
        
        for (const entry of tweetEntries) {
            const tweetData = entry.content?.itemContent?.tweet_results?.result;
            if (tweetData && tweetData.legacy) {
                const tweet = tweetData.legacy;
                const tweetId = tweet.id_str;
                const tweetTime = new Date(tweet.created_at).getTime();
                
                // 只处理1分钟内且未检查过的转发
                if (!userCache.checkedRetweets[tweetId] && tweetTime >= oneMinuteAgo) {
                    userCache.checkedRetweets[tweetId] = true;
                    newRetweetsCount++;
                    
                    // 提取转发的原始推文信息
                    const originalTweet = tweet.retweeted_status_result?.result?.legacy;
                    const originalUser = tweet.retweeted_status_result?.result?.core?.user_results?.result?.legacy;
                    
                    console.log(`   发现新转发: ${tweetId}`);
                    
                    const message = `
🔄 <b>转发推文通知</b>

👤 用户: @${user.username}
📝 转发了: @${originalUser?.screen_name || '未知用户'}
💭 原文: ${originalTweet?.full_text || originalTweet?.text || tweet.full_text || '无内容'}
🔗 链接: https://twitter.com/${user.username}/status/${tweetId}
⏰ 时间: ${new Date(tweet.created_at).toLocaleString('zh-CN')}
                    `.trim();
                    
                    await sendTelegramMessage(message);
                } else if (userCache.checkedRetweets[tweetId]) {
                    console.log(`   跳过已通知的转发: ${tweetId}`);
                } else {
                    console.log(`   跳过旧转发: ${tweetId}`);
                }
            }
        }
        
        if (newRetweetsCount === 0) {
            console.log(`   没有1分钟内的新转发`);
        }

        cache[user.userId] = userCache;
        saveCache(cache);
    } catch (error) {
        console.error(`检查用户 ${user.username} 的转发推文失败:`, error.message);
    }
}

// 检查引用推文
async function checkQuotes(user) {
    try {
        console.log(`🔍 开始检查引用 - 用户: @${user.username}, ID: ${user.userId}`);
        const cache = getCache();
        const userCache = cache[user.userId] || {};
        
        // 使用 quotes API，pid 参数使用用户的 rest_id
        const tweets = await getUserQuotes(user.userId, 20);
        
        // 尝试多种可能的响应结构
        let entries = [];
        if (tweets?.result?.timeline?.instructions) {
            entries = tweets.result.timeline.instructions
                .find(i => i.type === 'TimelineAddEntries')?.entries || [];
        } else if (tweets?.result?.entries) {
            entries = tweets.result.entries;
        } else if (tweets?.entries) {
            entries = tweets.entries;
        } else if (Array.isArray(tweets)) {
            entries = tweets;
        } else {
            console.warn(`⚠️  无法解析引用API响应结构`);
            return;
        }

        // 解析引用数据
        const tweetEntries = entries.filter(e => {
            const entryId = e.entryId || e.id || e.tweet_id || '';
            return String(entryId).startsWith('tweet-') || String(entryId).includes('tweet');
        });
        
        console.log(`📊 找到 ${tweetEntries.length} 条引用条目`);
        
        if (!userCache.checkedQuotes) {
            userCache.checkedQuotes = {};
        }

        // 检查引用（只通知1分钟内的）
        const now = Date.now();
        const oneMinuteAgo = now - 60 * 1000;
        let newQuotesCount = 0;
        
        for (const entry of tweetEntries) {
            const tweetData = entry.content?.itemContent?.tweet_results?.result;
            if (tweetData && tweetData.legacy) {
                const tweet = tweetData.legacy;
                const tweetId = tweet.id_str;
                const tweetTime = new Date(tweet.created_at).getTime();
                
                // 只处理1分钟内且未检查过的引用
                if (!userCache.checkedQuotes[tweetId] && tweetTime >= oneMinuteAgo) {
                    userCache.checkedQuotes[tweetId] = true;
                    newQuotesCount++;
                    
                    // 提取被引用的原始推文信息
                    const quotedTweet = tweet.quoted_status_result?.result?.legacy;
                    const quotedUser = tweet.quoted_status_result?.result?.core?.user_results?.result?.legacy;
                    
                    console.log(`   发现新引用: ${tweetId}`);
                    
                    const message = `
💬 <b>引用推文通知</b>

👤 用户: @${user.username}
📝 评论: ${tweet.full_text || tweet.text}
💭 引用了: @${quotedUser?.screen_name || '未知用户'}
📄 原文: ${quotedTweet?.full_text || quotedTweet?.text || '无内容'}
🔗 链接: https://twitter.com/${user.username}/status/${tweetId}
⏰ 时间: ${new Date(tweet.created_at).toLocaleString('zh-CN')}
                    `.trim();
                    
                    await sendTelegramMessage(message);
                } else if (userCache.checkedQuotes[tweetId]) {
                    console.log(`   跳过已通知的引用: ${tweetId}`);
                } else {
                    console.log(`   跳过旧引用: ${tweetId}`);
                }
            }
        }
        
        if (newQuotesCount === 0) {
            console.log(`   没有1分钟内的新引用`);
        }

        cache[user.userId] = userCache;
        saveCache(cache);
    } catch (error) {
        console.error(`检查用户 ${user.username} 的引用推文失败:`, error.message);
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
            
            // 检查引用（如果启用）
            if (user.monitorQuotes) {
                await checkQuotes(user);
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
        
        console.log(`\n========== API响应详情 ==========`);
        console.log(`完整响应:`, JSON.stringify(userData, null, 2));
        console.log(`响应顶层键:`, Object.keys(userData || {}));
        console.log(`================================\n`);
        
        if (!userData) {
            return res.status(404).json({ success: false, message: '用户不存在' });
        }
        
        // 从 about-account API 响应中提取 rest_id
        // 专门查找 rest_id 字段（纯数字）
        function findRestId(obj, path = '') {
            if (!obj || typeof obj !== 'object') return null;
            
            // 只查找名为 rest_id 的字段
            if (obj.hasOwnProperty('rest_id') && obj.rest_id) {
                const id = String(obj.rest_id);
                console.log(`   发现 rest_id 字段在 ${path || '根'}: "${id}"`);
                
                // 检查是否是纯数字
                if (/^\d+$/.test(id)) {
                    console.log(`   ✅ rest_id 是纯数字: ${id}`);
                    return id;
                } else {
                    console.log(`   ⚠️  rest_id 不是纯数字，跳过`);
                }
            }
            
            // 递归搜索所有子对象，继续查找 rest_id
            for (const key of Object.keys(obj)) {
                if (typeof obj[key] === 'object' && obj[key] !== null) {
                    const found = findRestId(obj[key], path ? `${path}.${key}` : key);
                    if (found) return found;
                }
            }
            
            return null;
        }
        
        console.log(`\n开始查找 rest_id 字段...`);
        const userId = findRestId(userData);
        console.log(`\n最终提取的用户ID: ${userId || '❌ 未找到 rest_id 字段'}\n`);
        
        if (!userId) {
            console.error(`❌ 无法从响应中提取用户ID`);
            console.error(`已尝试的路径: rest_id, id_str, id`);
            console.error(`响应的完整结构:`, JSON.stringify(userData).substring(0, 500));
            return res.status(500).json({ 
                success: false, 
                message: '无法获取用户ID，API响应格式异常。请查看服务器日志获取详细信息。' 
            });
        }
        
        console.log(`用户 @${username} 的ID: ${userId} (类型: ${typeof userId})`);
        
        const users = getMonitoredUsers();
        
        // 检查是否已存在（使用字符串比较）
        if (users.find(u => String(u.userId) === userId)) {
            return res.status(400).json({ success: false, message: '该用户已在监控列表中' });
        }
        
        // 添加用户（确保userId是字符串）
        const newUser = {
            userId: userId, // 明确保存为字符串
            username,
            displayName: userData.result.legacy?.name || username,
            enabled: true,
            monitorTweets: true,
            monitorReplies: true,
            monitorPinned: true,
            monitorRetweets: true,
            monitorQuotes: true,
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

