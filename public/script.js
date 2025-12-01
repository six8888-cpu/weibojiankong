// 全局变量
let config = {};
let users = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadUsers();
});

// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 切换配置面板
function toggleConfig() {
    const panel = document.getElementById('config-panel');
    const toggleText = document.getElementById('config-toggle-text');
    
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        toggleText.textContent = '隐藏';
    } else {
        panel.style.display = 'none';
        toggleText.textContent = '显示';
    }
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        config = data;
        
        // 填充表单
        document.getElementById('rapidApiKey').placeholder = data.rapidApiKey || '输入您的RapidAPI Key';
        document.getElementById('telegramBotToken').placeholder = data.telegramBotToken || '输入您的Telegram Bot Token';
        document.getElementById('telegramChatId').value = data.telegramChatId || '';
        document.getElementById('checkInterval').value = data.checkInterval || 5;
    } catch (error) {
        showToast('加载配置失败: ' + error.message, 'error');
    }
}

// 保存配置
async function saveConfig() {
    const rapidApiKey = document.getElementById('rapidApiKey').value.trim();
    const telegramBotToken = document.getElementById('telegramBotToken').value.trim();
    const telegramChatId = document.getElementById('telegramChatId').value.trim();
    const checkInterval = parseInt(document.getElementById('checkInterval').value);
    
    if (!checkInterval || checkInterval < 1 || checkInterval > 60) {
        showToast('检查间隔必须在1-60分钟之间', 'error');
        return;
    }
    
    try {
        const configData = {
            checkInterval,
            telegramChatId
        };
        
        // 只有在用户输入了新的key时才更新
        if (rapidApiKey && !rapidApiKey.includes('已配置')) {
            configData.rapidApiKey = rapidApiKey;
        }
        if (telegramBotToken && !telegramBotToken.includes('已配置')) {
            configData.telegramBotToken = telegramBotToken;
        }
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('配置保存成功！', 'success');
            loadConfig();
        } else {
            showToast('保存失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('保存配置失败: ' + error.message, 'error');
    }
}

// 测试Telegram
async function testTelegram() {
    try {
        const response = await fetch('/api/test-telegram', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('测试消息已发送，请检查Telegram！', 'success');
        } else {
            showToast('发送失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('测试失败: ' + error.message, 'error');
    }
}

// 加载用户列表
async function loadUsers() {
    const usersList = document.getElementById('users-list');
    usersList.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        // 添加时间戳防止缓存
        const timestamp = new Date().getTime();
        const response = await fetch(`/api/users?t=${timestamp}`);
        users = await response.json();
        
        console.log('加载用户列表:', users.length, '个用户');
        
        if (users.length === 0) {
            usersList.innerHTML = '<div class="empty">暂无监控用户，请添加</div>';
            return;
        }
        
        renderUsers();
    } catch (error) {
        console.error('加载用户列表失败:', error);
        usersList.innerHTML = '<div class="empty">加载失败: ' + error.message + '</div>';
    }
}

// 渲染用户列表
function renderUsers() {
    const usersList = document.getElementById('users-list');
    
    usersList.innerHTML = users.map(user => `
        <div class="user-card">
            <div class="user-header">
                <div class="user-info">
                    <h3>${user.displayName || user.username}</h3>
                    <p>@${user.username}</p>
                    <p style="color: #888; font-size: 0.9em;">用户ID: ${user.userId || '未设置'}</p>
                </div>
            </div>
            
            <div class="user-meta">
                <p>添加时间: ${new Date(user.addedAt).toLocaleString('zh-CN')}</p>
                <button class="btn btn-danger btn-sm" onclick="deleteUser('${user.userId}', '${user.username}')" style="float: right;">🗑️ 删除</button>
            </div>
        </div>
    `).join('');
}

// 添加用户
async function addUser() {
    const usernameInput = document.getElementById('username');
    const username = usernameInput.value.trim().replace('@', '');
    
    if (!username) {
        showToast('请输入用户名', 'error');
        return;
    }
    
    showToast('正在添加用户...', 'info');
    
    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('用户添加成功！', 'success');
            usernameInput.value = '';
            loadUsers();
        } else {
            showToast('添加失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('添加失败: ' + error.message, 'error');
    }
}

// 更新用户选项（暂未使用）
// async function updateUserOption(userId, option, value) { ... }

// 删除用户
async function deleteUser(userId, username) {
    if (!confirm(`确定要删除用户 @${username} 吗？`)) {
        return;
    }
    
    console.log(`删除用户: ${username}, ID: ${userId}`);
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        console.log('删除结果:', result);
        
        if (result.success) {
            showToast('用户已删除', 'success');
            // 等待一下再刷新，确保后端已保存
            await new Promise(resolve => setTimeout(resolve, 500));
            await loadUsers();
        } else {
            showToast('删除失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('删除用户错误:', error);
        showToast('删除失败: ' + error.message, 'error');
    }
}

// 手动执行监控（功能待实现）
// async function runMonitor() { ... }

// 处理回车键
function handleEnter(event) {
    if (event.key === 'Enter') {
        addUser();
    }
}

