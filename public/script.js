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
        const response = await fetch('/api/users');
        users = await response.json();
        
        if (users.length === 0) {
            usersList.innerHTML = '<div class="empty">暂无监控用户，请添加</div>';
            return;
        }
        
        renderUsers();
    } catch (error) {
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
                </div>
                <div class="user-actions">
                    <span class="status-badge ${user.enabled ? 'active' : 'inactive'}">
                        ${user.enabled ? '✓ 启用' : '✗ 禁用'}
                    </span>
                </div>
            </div>
            
            <div class="user-options">
                <div class="option-item">
                    <input type="checkbox" 
                           id="enabled-${user.userId}" 
                           ${user.enabled ? 'checked' : ''}
                           onchange="updateUserOption('${user.userId}', 'enabled', this.checked)">
                    <label for="enabled-${user.userId}">启用监控</label>
                </div>
                
                <div class="option-item">
                    <input type="checkbox" 
                           id="tweets-${user.userId}" 
                           ${user.monitorTweets ? 'checked' : ''}
                           onchange="updateUserOption('${user.userId}', 'monitorTweets', this.checked)">
                    <label for="tweets-${user.userId}">📝 新推文</label>
                </div>
                
                <div class="option-item">
                    <input type="checkbox" 
                           id="replies-${user.userId}" 
                           ${user.monitorReplies ? 'checked' : ''}
                           onchange="updateUserOption('${user.userId}', 'monitorReplies', this.checked)">
                    <label for="replies-${user.userId}">💬 回复</label>
                </div>
                
                <div class="option-item">
                    <input type="checkbox" 
                           id="pinned-${user.userId}" 
                           ${user.monitorPinned ? 'checked' : ''}
                           onchange="updateUserOption('${user.userId}', 'monitorPinned', this.checked)">
                    <label for="pinned-${user.userId}">📌 置顶</label>
                </div>
                
                <div class="option-item">
                    <input type="checkbox" 
                           id="retweets-${user.userId}" 
                           ${user.monitorRetweets ? 'checked' : ''}
                           onchange="updateUserOption('${user.userId}', 'monitorRetweets', this.checked)">
                    <label for="retweets-${user.userId}">🔄 转发</label>
                </div>
            </div>
            
            <div class="user-meta">
                添加时间: ${new Date(user.addedAt).toLocaleString('zh-CN')}
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

// 更新用户选项
async function updateUserOption(userId, option, value) {
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ [option]: value })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('更新成功', 'success');
            loadUsers();
        } else {
            showToast('更新失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('更新失败: ' + error.message, 'error');
    }
}

// 删除用户
async function deleteUser(userId, username) {
    if (!confirm(`确定要删除用户 @${username} 吗？`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('用户已删除', 'success');
            loadUsers();
        } else {
            showToast('删除失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

// 手动执行监控
async function runMonitor() {
    showToast('正在执行监控检查...', 'info');
    
    try {
        const response = await fetch('/api/monitor/run', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('监控任务已启动，请稍后查看Telegram', 'success');
        } else {
            showToast('启动失败: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('启动失败: ' + error.message, 'error');
    }
}

// 处理回车键
function handleEnter(event) {
    if (event.key === 'Enter') {
        addUser();
    }
}

