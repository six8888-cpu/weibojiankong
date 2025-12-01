#!/usr/bin/env node
// 完整流程测试脚本 - 验证用户名到用户ID到推文获取的完整流程

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 读取配置
const CONFIG_FILE = path.join(__dirname, 'data', 'config.json');

if (!fs.existsSync(CONFIG_FILE)) {
    console.error('❌ 配置文件不存在！请先运行服务器初始化配置。');
    process.exit(1);
}

const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
const API_KEY = config.rapidApiKey;
const API_HOST = 'twitter241.p.rapidapi.com';

if (!API_KEY || API_KEY === '') {
    console.error('❌ RapidAPI Key未配置！请在Web界面配置API Key。');
    process.exit(1);
}

// 从命令行参数获取测试用户名
const TEST_USERNAME = process.argv[2] || 'elonmusk';

console.log('========================================');
console.log('Twitter API 完整流程测试');
console.log('========================================\n');
console.log(`测试用户名: @${TEST_USERNAME}`);
console.log(`API密钥: ${API_KEY.substring(0, 10)}...${API_KEY.substring(API_KEY.length - 4)}\n`);

// 调用API的通用函数
async function callAPI(endpoint, params, description) {
    const queryString = Object.keys(params).map(key => `${key}=${params[key]}`).join('&');
    const url = `https://${API_HOST}/${endpoint}?${queryString}`;
    
    console.log(`\n${description}`);
    console.log(`📡 请求: ${url}`);
    
    try {
        const response = await axios.get(`https://${API_HOST}/${endpoint}`, {
            params: params,
            headers: {
                'x-rapidapi-key': API_KEY,
                'x-rapidapi-host': API_HOST
            },
            timeout: 15000
        });
        
        console.log(`✅ 成功! 状态码: ${response.status}`);
        return { success: true, data: response.data };
    } catch (error) {
        if (error.response) {
            console.log(`❌ 失败! 状态码: ${error.response.status}`);
            console.log(`   错误信息: ${error.response.statusText}`);
            if (error.response.data) {
                console.log(`   错误详情:`, JSON.stringify(error.response.data).substring(0, 200));
            }
        } else if (error.request) {
            console.log(`❌ 失败! 无响应`);
            console.log(`   错误: ${error.message}`);
        } else {
            console.log(`❌ 失败! ${error.message}`);
        }
        return { success: false, error: error.response?.status || error.message };
    }
}

async function testFullFlow() {
    console.log('\n========================================');
    console.log('步骤1: 通过用户名获取用户信息');
    console.log('========================================');
    
    const userResult = await callAPI('user', { username: TEST_USERNAME }, '调用 /user 端点');
    
    if (!userResult.success) {
        console.log('\n❌ 无法获取用户信息，流程终止。');
        console.log('\n💡 可能的原因：');
        console.log('   1. RapidAPI Key 无效或已过期');
        console.log('   2. API订阅已过期或超出配额');
        console.log('   3. 用户名不存在');
        console.log('   4. API端点名称已更改');
        return;
    }
    
    // 提取用户ID
    let userId = null;
    if (userResult.data?.result?.rest_id) {
        userId = String(userResult.data.result.rest_id);
        console.log(`\n✅ 成功获取用户ID: ${userId}`);
        console.log(`   用户显示名: ${userResult.data.result.legacy?.name || 'N/A'}`);
        console.log(`   用户名: @${userResult.data.result.legacy?.screen_name || TEST_USERNAME}`);
    } else {
        console.log('\n⚠️  响应结构不符合预期');
        console.log('   响应结构:', JSON.stringify(Object.keys(userResult.data || {})));
        console.log('   尝试查找用户ID...');
        
        // 尝试从其他可能的位置提取
        if (userResult.data?.id) {
            userId = String(userResult.data.id);
            console.log(`   找到用户ID: ${userId}`);
        } else if (userResult.data?.user?.id) {
            userId = String(userResult.data.user.id);
            console.log(`   找到用户ID: ${userId}`);
        }
    }
    
    if (!userId) {
        console.log('\n❌ 无法提取用户ID，流程终止。');
        console.log('   完整响应:', JSON.stringify(userResult.data).substring(0, 500));
        return;
    }
    
    console.log('\n========================================');
    console.log('步骤2: 使用用户ID获取推文');
    console.log('========================================');
    console.log(`使用用户ID: ${userId} (类型: ${typeof userId})`);
    
    const tweetsResult = await callAPI('user-tweets', { user: userId, count: 5 }, '调用 /user-tweets 端点');
    
    if (!tweetsResult.success) {
        console.log('\n❌ 无法获取推文');
        console.log('\n💡 可能的原因：');
        console.log('   1. 端点名称不正确（可能是 tweets 而不是 user-tweets）');
        console.log('   2. 参数名称不正确（可能是 userId 而不是 user）');
        console.log('   3. 用户ID格式不对');
        
        console.log('\n🔄 尝试其他可能的端点和参数组合...');
        
        const alternatives = [
            { endpoint: 'tweets', params: { user: userId, count: 5 } },
            { endpoint: 'user-tweets', params: { userId: userId, count: 5 } },
            { endpoint: 'tweets', params: { userId: userId, count: 5 } },
            { endpoint: 'getUserTweets', params: { user: userId, count: 5 } },
        ];
        
        for (const alt of alternatives) {
            console.log(`\n尝试: ${alt.endpoint} with ${JSON.stringify(alt.params)}`);
            const altResult = await callAPI(alt.endpoint, alt.params, '');
            if (altResult.success) {
                console.log(`✅ 找到可用的组合！`);
                console.log(`   端点: ${alt.endpoint}`);
                console.log(`   参数: ${JSON.stringify(alt.params)}`);
                break;
            }
        }
    } else {
        console.log('\n✅ 成功获取推文！');
        console.log(`   响应结构:`, Object.keys(tweetsResult.data || {}));
    }
    
    console.log('\n========================================');
    console.log('步骤3: 使用用户ID获取回复');
    console.log('========================================');
    
    const repliesResult = await callAPI('user-replies', { user: userId, count: 5 }, '调用 /user-replies 端点');
    
    if (repliesResult.success) {
        console.log('\n✅ 成功获取回复！');
    } else {
        console.log('\n⚠️  无法获取回复（可能端点不同）');
    }
    
    console.log('\n========================================');
    console.log('测试总结');
    console.log('========================================\n');
    
    console.log('结果：');
    console.log(`  获取用户信息: ${userResult.success ? '✅ 成功' : '❌ 失败'}`);
    console.log(`  获取推文: ${tweetsResult.success ? '✅ 成功' : '❌ 失败'}`);
    console.log(`  获取回复: ${repliesResult.success ? '✅ 成功' : '❌ 失败'}`);
    
    if (userResult.success && userId) {
        console.log(`\n📋 提取的用户信息：`);
        console.log(`  用户ID: ${userId}`);
        console.log(`  用户名: @${TEST_USERNAME}`);
        
        if (tweetsResult.success) {
            console.log(`\n✅ 完整流程测试通过！`);
            console.log(`   系统应该可以正常监控此用户。`);
        } else {
            console.log(`\n⚠️  可以获取用户信息，但无法获取推文。`);
            console.log(`   可能需要调整 API 端点名称或参数。`);
        }
    } else {
        console.log(`\n❌ 测试失败，请检查：`);
        console.log(`   1. RapidAPI 订阅是否有效`);
        console.log(`   2. API Key 是否正确`);
        console.log(`   3. 用户名是否正确`);
    }
    
    console.log('\n========================================\n');
}

// 运行测试
testFullFlow().catch(error => {
    console.error('\n测试过程出错:', error);
    process.exit(1);
});

