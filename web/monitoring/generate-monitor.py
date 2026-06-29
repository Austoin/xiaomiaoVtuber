"""
生成增强版监控面板
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "monitor-dashboard-pro.html"

html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xiaomiaoVirtual Pro Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
            overflow-x: hidden;
        }

        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 30px 0;
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        h1 {
            font-size: 42px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 16px;
            color: rgba(255,255,255,0.6);
            letter-spacing: 2px;
        }

        .grid {
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }

        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            background: rgba(255,255,255,0.08);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .service-grid {
            display: grid;
            gap: 15px;
        }

        .service-card {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .service-card.running { border-left-color: #10b981; }
        .service-card.stopped { border-left-color: #ef4444; }
        .service-card.warning { border-left-color: #f59e0b; }

        .service-card:hover {
            background: rgba(0,0,0,0.5);
            transform: translateX(5px);
        }

        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .service-name {
            font-size: 16px;
            font-weight: 600;
        }

        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge.running {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }

        .status-badge.stopped {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        .status-badge.warning {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }

        .service-info {
            display: grid;
            gap: 8px;
            font-size: 13px;
            color: rgba(255,255,255,0.7);
        }

        .info-row {
            display: flex;
            justify-content: space-between;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        .stat-item {
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
        }

        .stat-value {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 12px;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
        }

        .timeline {
            padding: 20px 0;
        }

        .timeline-item {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            font-size: 13px;
        }

        .timeline-time {
            color: rgba(255,255,255,0.5);
            min-width: 60px;
        }

        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }

        button:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }

        button.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }

        canvas {
            width: 100%;
            height: 400px;
            border-radius: 12px;
            background: rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 xiaomiaoVirtual Monitor Pro</h1>
            <div class="subtitle">REAL-TIME SERVICE MONITORING DASHBOARD</div>
        </div>

        <div class="grid">
            <div class="sidebar">
                <div class="card">
                    <div class="card-title">📊 总览统计</div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value" id="runningCount">0</div>
                            <div class="stat-label">运行中</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="stoppedCount">0</div>
                            <div class="stat-label">已停止</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="warningCount">0</div>
                            <div class="stat-label">警告</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="uptimeValue">0s</div>
                            <div class="stat-label">运行时长</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">⚙️ 控制面板</div>
                    <div class="controls">
                        <button class="primary" onclick="checkAllServices()">🔄 刷新状态</button>
                        <button onclick="toggleAutoRefresh()">
                            <span id="autoIcon">▶️</span> <span id="autoText">自动刷新</span>
                        </button>
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="card">
                    <div class="card-title">🖥️ 服务状态</div>
                    <div class="service-grid" id="servicesContainer"></div>
                </div>
            </div>

            <div class="sidebar">
                <div class="card">
                    <div class="card-title">📝 活动日志</div>
                    <div class="timeline" id="timeline"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const services = {
            'napcat': { name: 'NapCat (QQ协议)', port: '5004', type: '协议层' },
            'agent-api': { name: 'xiaomiaoAgent API', port: '8900', type: 'API层' },
            'xiaomiao-bridge': { name: '小喵桌面桥接', port: '5519', type: '桥接层' },
            'xiaomiao-bot': { name: 'QQ Bot', port: '-', type: '应用层' },
            'stage-web': { name: 'Web 界面', port: '5175', type: '前端层' },
            'stage-tamagotchi': { name: '桌面端', port: '-', type: '前端层' },
            'tui': { name: 'TUI 终端', port: '-', type: '前端层' }
        };

        let serviceStates = {};
        let startTime = Date.now();
        let autoRefreshInterval = null;
        let logs = [];

        Object.keys(services).forEach(id => serviceStates[id] = 'stopped');

        function addLog(message) {
            logs.unshift({ time: new Date().toLocaleTimeString(), message });
            logs = logs.slice(0, 10);
            renderLogs();
        }

        function renderLogs() {
            const timeline = document.getElementById('timeline');
            timeline.innerHTML = logs.map(log => `
                <div class="timeline-item">
                    <div class="timeline-time">${log.time}</div>
                    <div>${log.message}</div>
                </div>
            `).join('');
        }

        function renderServices() {
            const container = document.getElementById('servicesContainer');
            container.innerHTML = Object.keys(services).map(id => {
                const s = services[id];
                const state = serviceStates[id];
                return `
                    <div class="service-card ${state}">
                        <div class="service-header">
                            <div class="service-name">${s.name}</div>
                            <div class="status-badge ${state}">
                                ${state === 'running' ? '运行中' : state === 'warning' ? '警告' : '已停止'}
                            </div>
                        </div>
                        <div class="service-info">
                            <div class="info-row">
                                <span>端口</span><span>${s.port}</span>
                            </div>
                            <div class="info-row">
                                <span>类型</span><span>${s.type}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            updateStats();
        }

        function updateStats() {
            const states = Object.values(serviceStates);
            document.getElementById('runningCount').textContent = states.filter(s => s === 'running').length;
            document.getElementById('stoppedCount').textContent = states.filter(s => s === 'stopped').length;
            document.getElementById('warningCount').textContent = states.filter(s => s === 'warning').length;

            const uptime = Math.floor((Date.now() - startTime) / 1000);
            const h = Math.floor(uptime / 3600);
            const m = Math.floor((uptime % 3600) / 60);
            const s = uptime % 60;
            document.getElementById('uptimeValue').textContent = h > 0 ? `${h}h ${m}m` : m > 0 ? `${m}m ${s}s` : `${s}s`;
        }

        async function checkAllServices() {
            addLog('开始检查服务状态...');
            try {
                const response = await fetch('http://127.0.0.1:8888/api/status');
                const data = await response.json();
                data.services.forEach(service => {
                    if (serviceStates.hasOwnProperty(service.id)) {
                        serviceStates[service.id] = service.status;
                    }
                });
                addLog('✓ 状态检查完成');
            } catch (error) {
                Object.keys(services).forEach(id => {
                    serviceStates[id] = Math.random() > 0.5 ? 'running' : 'stopped';
                });
                addLog('⚠ 使用模拟数据');
            }
            renderServices();
        }

        function toggleAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                document.getElementById('autoIcon').textContent = '▶️';
                document.getElementById('autoText').textContent = '自动刷新';
                addLog('× 已停止自动刷新');
            } else {
                autoRefreshInterval = setInterval(checkAllServices, 5000);
                document.getElementById('autoIcon').textContent = '⏸️';
                document.getElementById('autoText').textContent = '停止刷新';
                addLog('✓ 已开启自动刷新');
            }
        }

        setInterval(updateStats, 1000);
        renderServices();
        setTimeout(checkAllServices, 2000);
    </script>
</body>
</html>'''

# 保存文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ 监控面板已生成: {OUTPUT_FILE}")
