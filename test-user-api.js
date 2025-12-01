// 测试用户API调用脚本
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 读取配置
const CONFIG_FILE = path.join(__dirname, 'data', 'config.json');
const USERS_FILE = path.join(__dirname, 'data', 'monitored_users.json');

if (!fs.existsSync(CONFIG_FILE)) {
    console.error('❌ 配置文件不存在！请先配置系统。');
    process.exit(1);
}

const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

const API_KEY = config.rapidApiKey;
const API_HOST = 'twitter241.p.rapidapi.com';

if (!API_KEY) {
    console.error('❌ RapidAPI Key未配置！');
    process.exit(1);
}

console.log('========================================');
console.log('Twitter API 测试工具');
console.log('========================================\n');

if (users.length === 0) {
    console.log('⚠️  没有监控用户，请先添加用户');
    process.exit(1);
}

async function testAPI(endpoint, params, description) {
    const queryString = Object.keys(params).map(key => `${key}=${params[key]}`).join('&');
    const url = `https://${API_HOST}/${endpoint}?${queryString}`;
    
    console.log(`\n${description}`);
    console.log(`URL: ${url}`);
    console.log(`参数:`, JSON.stringify(params));
    
    try {
        const response = await axios.get(`https://${API_HOST}/${endpoint}`, {
            params: params,
            headers: {
                'X-RapidAPI-Key': API_KEY,
                'X-RapidAPI-Host': API_HOST
            },
            timeout: 15000
        });
        
        console.log(`✅ 成功! 状态码: ${response.status}`);
        console.log(`响应数据大小: ${JSON.stringify(response.data).length} 字符`);
        
        // 检查响应结构
        if (response.data && response.data.result) {
            console.log(`✅ 响应包含 result 字段`);
        } else {
            console.log(`⚠️  响应结构可能不同:`, Object.keys(response.data || {}));
        }
        
        return { success: true, data: response.data };
    } catch (error) {
        if (error.response) {
            console.log(`❌ 失败! 状态码: ${error.response.status}`);
            console.log(`错误信息: ${error.response.statusText}`);
            if (error.response.data) {
                console.log(`错误详情:`, JSON.stringify(error.response.data).substring(0, 200));
            }
        } else {
            console.log(`❌ 失败! 错误: ${error.message}`);
        }
        return { success: false, error: error.response?.status || error.message };
    }
}

async function runTests() {
    // 测试第一个监控用户
    const testUser = users[0];
    console.log(`测试用户: @${testUser.username}`);
    console.log(`用户ID: ${testUser.userId} (类型: ${typeof testUser.userId})\n`);
    
    // 测试1: 获取用户信息
    await testAPI('user', { username: testUser.username }, '测试1: 获取用户信息');
    
    // 测试2: 获取用户推文（使用用户ID）
    await testAPI('user-tweets', { user: testUser.userId, count: 5 }, '测试2: 获取用户推文 (使用ID)');
    
    // 测试3: 获取用户推文（使用用户名，如果ID失败）
    await testAPI('user-tweets', { user: testUser.username, count: 5 }, '测试3: 获取用户推文 (使用用户名)');
    
    // 测试4: 获取用户回复
    await testAPI('user-replies', { user: testUser.userId, count: 5 }, '测试4: 获取用户回复 (使用ID)');
    
    // 测试5: 获取用户回复（使用用户名）
    await testAPI('user-replies', { user: testUser.username, count: 5 }, '测试5: 获取用户回复 (使用用户名)');
    
    console.log('\n========================================');
    console.log('测试完成');
    console.log('========================================\n');
    
    console.log('💡 建议:');
    console.log('1. 如果所有测试都失败，检查RapidAPI订阅状态');
    console.log('2. 如果只有某些端点失败，可能是端点名称或参数格式不对');
    console.log('3. 查看上面的详细错误信息');
}

runTests().catch(error => {
    console.error('测试过程出错:', error);
    process.exit(1);
});

