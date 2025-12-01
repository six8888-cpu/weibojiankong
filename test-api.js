// Twitter API 端点测试脚本
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 读取配置
const CONFIG_FILE = path.join(__dirname, 'data', 'config.json');
const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));

const API_KEY = config.rapidApiKey;
const API_HOST = 'twitter241.p.rapidapi.com';

// 测试用户
const TEST_USERNAME = 'elonmusk'; // 使用一个肯定存在的账号测试

console.log('========================================');
console.log('Twitter API 端点测试');
console.log('========================================\n');

// 可能的端点名称列表（根据实际API文档更新）
const possibleEndpoints = {
    userInfo: ['about-account', 'user', 'getUser', 'userByUsername', 'user-by-username'],
    userTweets: ['user-tweets', 'userTweets', 'tweets', 'getUserTweets', 'user/tweets'],
    userReplies: ['user-replies', 'userReplies', 'replies', 'getUserReplies', 'user/replies']
};

async function testEndpoint(endpoint, params) {
    try {
        const response = await axios.get(`https://${API_HOST}/${endpoint}`, {
            params: params,
            headers: {
                'X-RapidAPI-Key': API_KEY,
                'X-RapidAPI-Host': API_HOST
            },
            timeout: 10000
        });
        return { success: true, data: response.data };
    } catch (error) {
        return { 
            success: false, 
            error: error.response?.status || error.message 
        };
    }
}

async function findWorkingEndpoints() {
    console.log('步骤1: 测试获取用户信息的端点...\n');
    
    let userId = null;
    
    // 测试用户信息端点
    for (const endpoint of possibleEndpoints.userInfo) {
        process.stdout.write(`  测试: ${endpoint} ... `);
        const result = await testEndpoint(endpoint, { username: TEST_USERNAME });
        
        if (result.success) {
            console.log('✅ 成功!');
            console.log(`     正确端点: ${endpoint}`);
            console.log(`     参数: username=${TEST_USERNAME}`);
            
            // 尝试提取用户ID
            if (result.data?.result?.rest_id) {
                userId = result.data.result.rest_id;
                console.log(`     用户ID: ${userId}\n`);
            }
            break;
        } else {
            console.log(`❌ 失败 (${result.error})`);
        }
    }
    
    if (!userId) {
        console.log('\n⚠️  无法获取用户ID，将使用测试ID继续...\n');
        userId = '44196397'; // Elon Musk的ID
    }
    
    console.log('\n步骤2: 测试获取推文的端点...\n');
    
    // 测试推文端点
    for (const endpoint of possibleEndpoints.userTweets) {
        process.stdout.write(`  测试: ${endpoint} ... `);
        const result = await testEndpoint(endpoint, { user: userId, count: 5 });
        
        if (result.success) {
            console.log('✅ 成功!');
            console.log(`     正确端点: ${endpoint}`);
            console.log(`     参数: user=${userId}, count=5\n`);
            break;
        } else {
            console.log(`❌ 失败 (${result.error})`);
        }
    }
    
    console.log('\n步骤3: 测试获取回复的端点...\n');
    
    // 测试回复端点
    for (const endpoint of possibleEndpoints.userReplies) {
        process.stdout.write(`  测试: ${endpoint} ... `);
        const result = await testEndpoint(endpoint, { user: userId, count: 5 });
        
        if (result.success) {
            console.log('✅ 成功!');
            console.log(`     正确端点: ${endpoint}`);
            console.log(`     参数: user=${userId}, count=5\n`);
            break;
        } else {
            console.log(`❌ 失败 (${result.error})`);
        }
    }
    
    console.log('\n========================================');
    console.log('测试完成');
    console.log('========================================\n');
}

// 运行测试
findWorkingEndpoints().catch(error => {
    console.error('测试过程出错:', error.message);
    process.exit(1);
});



