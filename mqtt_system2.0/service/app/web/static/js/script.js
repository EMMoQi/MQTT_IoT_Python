// 设备状态卡片模板
/**
 * 根据设备数据生成状态卡片HTML
 * @param {Object} device - 设备对象
 * @param {string} device.id - 设备唯一标识符
 * @param {number} device.temperature - 设备当前温度(°C)
 * @param {number} device.voltage - 设备当前电压(V)
 * @param {string|number|Date} device.last_updated - 最后更新时间
 * @returns {string} 返回设备状态卡片的HTML字符串
 * 
 * 功能说明:
 * 1. 根据温度值(>28°C危险, >25°C警告, 其他正常)确定卡片边框颜色
 * 2. 计算电压百分比(3.3V-4.2V范围)
 * 3. 生成包含设备图标、ID、温度、电压和查看历史按钮的卡片
 */
function createStatusCard(device) {
    // 温度状态判断: 28°C以上为危险(红色), 25-28°C为警告(黄色), 其他为正常(绿色)
    const tempStatus = device.temperature > 28 ? 'danger' : device.temperature > 25 ? 'warning' : 'success';
    
    // 电压百分比计算: 将3.3V-4.2V线性映射到0-100%
    const voltPercentage = Math.round(((device.voltage - 3.3) / 0.9) * 100);

    return `
        <div class="device-card mb-3 p-3 rounded-3 shadow-sm border-start border-4 border-${tempStatus}">
            <!-- 设备标题区域: 包含设备图标、ID和最后更新时间 -->
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="mb-1">
                        <!-- 根据设备ID判断显示服务器图标还是温度计图标 -->
                        <i class="bi ${device.id.includes('server') ? 'bi-server' : 'bi-thermometer'}"></i>
                        ${device.id.toUpperCase()}
                    </h5>
                    <small class="text-muted">最后更新: ${formatTime(device.last_updated)}</small>
                </div>
                <!-- 温度徽章: 显示当前温度值并根据状态显示不同颜色 -->
                <span class="badge bg-${tempStatus} rounded-pill">
                    ${device.temperature}°C
                </span>
            </div>

            <!-- 电压显示区域: 包含电压数值和进度条 -->
            <div class="mt-2">
                <div class="d-flex justify-content-between small mb-1">
                    <span>电压</span>
                    <span class="fw-bold">${device.voltage}V</span>
                </div>
                <!-- 电压进度条: 显示电压百分比 -->
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-gradient" 
                         role="progressbar" 
                         style="width: ${voltPercentage}%"
                         aria-valuenow="${device.voltage}"
                         aria-valuemin="3.3"
                         aria-valuemax="4.2">
                    </div>
                </div>
            </div>

            <!-- 历史数据按钮: 点击触发showDeviceHistory函数查看该设备历史数据 -->
            <div class="mt-2">
                <button class="btn btn-sm btn-outline-secondary" 
                        onclick="showDeviceHistory('${device.id}')">
                    <i class="bi bi-clock-history"></i> 查看历史
                </button>
            </div>
        </div>
    `;
}

// 消息行模板
/**
 * 根据MQTT消息生成表格行HTML
 * @param {Object} msg - MQTT消息对象
 * @param {string} msg.topic - 消息主题
 * @param {string} msg.device_id - 设备ID
 * @param {number} msg.temperature - 温度值(°C)
 * @param {number} msg.voltage - 电压值(V)
 * @param {string|number|Date} msg.timestamp - 消息时间戳
 * @returns {string} 返回消息表格行的HTML字符串
 * 
 * 功能说明:
 * 1. 数据有效性验证
 * 2. 根据消息来源(server或device)确定行样式
 * 3. 生成包含时间、设备ID、主题、温度和电压的表格行
 */
function createMessageRow(msg) {
    // 数据验证: 确保msg对象及其必要字段存在
    if (!msg || typeof msg.topic !== 'string' || !msg.device_id) {
        // 返回错误提示行(红色背景)
        return `
            <tr class="table-danger">
                <td colspan="5">⚠️ 数据缺失或格式错误</td>
            </tr>
        `;
    }

    // 判断消息来源: 包含'server'的topic视为服务器消息(蓝色), 其他为设备消息(绿色)
    const isServer = msg.topic.includes('server');
    const directionClass = isServer ? 'table-primary' : 'table-success';

    // 生成消息表格行
    return `
        <tr class="${directionClass}">
            <!-- 时间列: 显示格式化后的时间 -->
            <td class="text-nowrap">${formatTime(msg.timestamp)}</td>
            <!-- 设备ID列: 显示带颜色徽章的设备ID -->
            <td><span class="badge bg-${isServer ? 'primary' : 'success'}">
                ${msg.device_id.toUpperCase()}
            </span></td>
            <!-- 主题列: 显示原始topic -->
            <td>${msg.topic}</td>
            <!-- 温度列: 高温(>28°C)显示为红色加粗 -->
            <td class="${msg.temperature > 28 ? 'text-danger fw-bold' : ''}">
                ${msg.temperature}°C
            </td>
            <!-- 电压列: 显示电压值 -->
            <td>${msg.voltage}V</td>
        </tr>
    `;
}

// 时间格式化函数
// 参数: timestamp - 时间戳，可以是数字、Date对象或ISO格式字符串
// 返回: 格式化后的时间字符串
function formatTime(timestamp) {
    try {
        // 如果timestamp已经是Date对象
        if (timestamp instanceof Date) {
            return timestamp.toLocaleTimeString() + ' ' + timestamp.toLocaleDateString();
        }
        
        // 如果是数字时间戳
        if (!isNaN(timestamp)) {
            const date = new Date(Number(timestamp));
            return date.toLocaleTimeString() + ' ' + date.toLocaleDateString();
        }
        
        // 如果是ISO格式字符串
        const date = new Date(timestamp);
        if (!isNaN(date.getTime())) {
            return date.toLocaleTimeString() + ' ' + date.toLocaleDateString();
        }
        
        // 如果都不匹配，返回原始值
        return timestamp;
    } catch (e) {
        console.error('时间格式化错误:', e);
        return '无效时间';
    }
}

// 图表实例变量
let tempChart, voltChart;

// 初始化图表
function initCharts() {
    const tempCtx = document.getElementById('tempChart');
    const voltCtx = document.getElementById('voltChart');

    // 图表通用配置
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (context) => `${context.dataset.label}: ${context.raw}`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { maxRotation: 45, minRotation: 45 }
            },
            y: {
                min: 0,
                grace: '5%' // 自动留出5%的空白
            }
        }
    };

    // 温度图表初始化
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '温度 (°C)',
                data: [],
                borderColor: '#ff6384',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.3,
                fill: true,
                pointRadius: 3
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: { 
                    ...commonOptions.scales.y,
                    title: { display: true, text: '温度 (°C)' }
                }
            }
        }
    });

    // 电压图表初始化
    voltChart = new Chart(voltCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '电压 (V)',
                data: [],
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.3,
                fill: true,
                pointRadius: 3
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: { 
                    ...commonOptions.scales.y,
                    title: { display: true, text: '电压 (V)' }
                }
            }
        }
    });
}

// 更新图表数据
// 参数: data - 包含时间戳、温度、电压的数据数组
function updateCharts(data) {
    // 数据验证
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.warn('无有效图表数据');
        return;
    }

    // 数据预处理
    const validData = data
        .filter(item => item && item.timestamp && !isNaN(item.temperature) && !isNaN(item.voltage))
        .slice(0, 20) // 限制数据点数量
        .reverse();   // 反转使最新数据在右侧

    if (validData.length === 0) {
        console.warn('没有有效数据可用于图表');
        return;
    }

    // 准备图表数据
    const labels = validData.map(d => {
        try {
            return formatTime(d.timestamp).split(' ')[0]; // 只显示时间部分
        } catch (e) {
            return '';
        }
    });

    // 更新温度图表
    tempChart.data.labels = labels;
    tempChart.data.datasets[0].data = validData.map(d => d.temperature);
    tempChart.update();

    // 更新电压图表
    voltChart.data.labels = labels;
    voltChart.data.datasets[0].data = validData.map(d => d.voltage);
    voltChart.update();
}

// 显示设备历史模态框
function showDeviceHistory(deviceId) {
    fetch(`/api/message_history?device_id=${deviceId}`)
        .then(res => res.json())
        .then(data => {
            const modalBody = document.getElementById('historyModalBody');
            modalBody.innerHTML = data.map(msg => `
                <div class="history-item mb-2 p-2 border-bottom">
                    <div class="d-flex justify-content-between">
                        <strong>${formatTime(msg.timestamp)}</strong>
                        <span class="badge bg-${msg.topic.includes('server') ? 'primary' : 'success'}">
                            ${msg.topic}
                        </span>
                    </div>
                    <div>温度: ${msg.temperature}°C</div>
                    <div>电压: ${msg.voltage}V</div>
                </div>
            `).join('');

            document.getElementById('historyModalLabel').textContent = `${deviceId} 的历史数据`;
            new bootstrap.Modal(document.getElementById('historyModal')).show();
        });
}

// 主数据更新函数
async function updateAllData() {
    try {
        // [原有代码...]
        // 1. 获取当前状态
        const statusRes = await fetch('/api/current_status');
        const statusData = await statusRes.json();
        
        // 更新状态卡片
        document.getElementById('status-container').innerHTML = 
            statusData.map(createStatusCard).join('');
        
        // 2. 获取消息历史
        const msgRes = await fetch('/api/message_history');
        const msgData = await msgRes.json();

        console.log('原始消息数据:', msgData); // 添加这行
        
        if (msgData && msgData.length > 0) {
            console.log('第一条消息样本:', msgData[0]); // 添加这行
            
            const validData = msgData.filter(msg => {
                const isValid = msg && 
                              msg.timestamp && 
                              !isNaN(msg.temperature) && 
                              !isNaN(msg.voltage);
                if (!isValid) {
                    console.warn('无效数据条目:', msg);
                }
                return isValid;
            });
            
            // [其余代码...]
            // 更新消息表格
            const msgList = document.getElementById('message-list');
            msgList.innerHTML = validData.map(createMessageRow).join('');
            
            // 自动滚动到底部
            msgList.parentElement.scrollTop = msgList.parentElement.scrollHeight;
            
            // 3. 更新图表
            updateCharts(validData.slice(0, 20).reverse());
        }
    } catch (error) {
        // [原有错误处理...]
        console.error('数据获取失败:', error);
        showToast('数据更新失败，请检查网络连接', 'danger');
    }
}

// 显示Toast通知
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    const toastId = 'toast-' + Date.now();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle'}"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // 自动移除
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始化图表
    initCharts();

    // 首次加载数据
    updateAllData();

    // 设置定时刷新 (每2秒)
    setInterval(updateAllData, 2000);

    // 连接状态监控
    let connectionOk = true;
    setInterval(() => {
        fetch('/api/current_status')
            .then(res => {
                if (!connectionOk) {
                    showToast('连接已恢复', 'success');
                    connectionOk = true;
                }
            })
            .catch(() => {
                if (connectionOk) {
                    showToast('连接服务器失败', 'danger');
                    connectionOk = false;
                }
            });
    }, 5000);
});
