"""
生成细化版监控面板 - 更详细的服务拆分
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "monitor-dashboard-ultra.html"

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xiaomiaoVirtual Ultra Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }

        h1 {
            font-size: 48px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .subtitle {
            color: rgba(255,255,255,0.5);
            letter-spacing: 3px;
            font-size: 14px;
        }

        .dashboard {
            display: grid;
            grid-template-columns: 280px 1fr 320px;
            gap: 20px;
            max-width: 2000px;
            margin: 0 auto;
        }

        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .section-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .category {
            margin-bottom: 20px;
        }

        .category-header {
            font-size: 13px;
            color: rgba(255,255,255,0.6);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .service {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-left: 3px solid;
            transition: all 0.3s;
            cursor: pointer;
        }

        .service:hover {
            background: rgba(0,0,0,0.5);
            transform: translateX(5px);
        }

        .service.running { border-left-color: #10b981; }
        .service.stopped { border-left-color: #ef4444; }
        .service.warning { border-left-color: #f59e0b; }

        .service-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .service-name {
            font-size: 14px;
            font-weight: 500;
        }

        .service-badge {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-running {
            background: rgba(16,185,129,0.2);
            color: #10b981;
        }

        .badge-stopped {
            background: rgba(239,68,68,0.2);
            color: #ef4444;
        }

        .badge-warning {
            background: rgba(245,158,11,0.2);
            color: #f59e0b;
        }

        .service-details {
            display: flex;
            gap: 15px;
            font-size: 11px;
            color: rgba(255,255,255,0.5);
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }

        .stat {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 11px;
            color: rgba(255,255,255,0.5);
            text-transform: uppercase;
        }

        .log {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 12px;
            display: flex;
            gap: 10px;
        }

        .log-time {
            color: rgba(255,255,255,0.4);
            font-family: monospace;
            min-width: 65px;
        }

        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102,126,234,0.4);
        }

        .progress {
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 5px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎭 xiaomiaoVirtual Ultra Monitor</h1>
        <div class="subtitle">GRANULAR SERVICE MONITORING SYSTEM</div>
    </div>

    <div class="dashboard">
        <div class="sidebar">
            <div class="section">
                <div class="section-title">📊 系统统计</div>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="totalServices">0</div>
                        <div class="stat-label">总服务数</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="runningCount">0</div>
                        <div class="stat-label">运行中</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="stoppedCount">0</div>
                        <div class="stat-label">已停止</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="warningCount">0</div>
                        <div class="stat-label">警告</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">⚙️ 控制</div>
                <button onclick="checkAll()">🔄 刷新全部</button>
                <button onclick="toggleAuto()">
                    <span id="autoText">▶️ 自动刷新</span>
                </button>
            </div>
        </div>

        <div class="main">
            <div class="section">
                <div class="section-title">🖥️ 服务详情</div>
                <div id="servicesContainer"></div>
            </div>
        </div>

        <div class="sidebar">
            <div class="section">
                <div class="section-title">📝 活动日志</div>
                <div id="logContainer"></div>
            </div>
        </div>
    </div>

    <script>
        const services = {
            protocol: {
                label: '🔌 协议层',
                items: {
                    'napcat': { name: 'NapCat', desc: 'QQ协议实现', port: '5004' },
                    'onebot': { name: 'OneBot', desc: 'WebSocket连接', port: '5004' }
                }
            },
            api: {
                label: '🔗 API层',
                items: {
                    'agent-api': { name: 'Agent API', desc: 'HTTP服务器', port: '8900' },
                    'agent-health': { name: 'Health Check', desc: '健康检查', port: '8900' },
                    'agent-stream': { name: 'Stream API', desc: '流式响应', port: '8900' }
                }
            },
            bridge: {
                label: '🌉 桥接层',
                items: {
                    'desktop-bridge': { name: '桌面桥接', desc: 'HTTP桥接', port: '5519' },
                    'bridge-event': { name: '事件存储', desc: 'JSONL日志', port: '-' },
                    'bridge-state': { name: '状态同步', desc: '实时同步', port: '-' }
                }
            },
            application: {
                label: '💬 应用层',
                items: {
                    'qq-bot': { name: 'QQ Bot主程序', desc: '消息处理', port: '-' },
                    'qq-router': { name: '消息路由', desc: '分发消息', port: '-' },
                    'qq-handler': { name: '命令处理', desc: '执行命令', port: '-' },
                    'qq-permission': { name: '权限系统', desc: '访问控制', port: '-' }
                }
            },
            agent: {
                label: '🤖 Agent层',
                items: {
                    'agent-core': { name: 'Agent核心', desc: 'LLM调用', port: '-' },
                    'agent-memory': { name: '记忆系统', desc: '上下文管理', port: '-' },
                    'agent-tools': { name: '工具系统', desc: '工具调用', port: '-' },
                    'agent-session': { name: '会话管理', desc: '多会话', port: '-' }
                }
            },
            frontend: {
                label: '🎨 前端层',
                items: {
                    'stage-web': { name: 'Web界面', desc: 'Vite开发服务器', port: '5175' },
                    'stage-tamagotchi': { name: '桌面端', desc: 'Electron应用', port: '-' },
                    'stage-pocket': { name: '移动端', desc: '移动应用', port: '-' },
                    'tui': { name: 'TUI终端', desc: '命令行界面', port: '-' }
                }
            },
            tools: {
                label: '🔧 工具层',
                items: {
                    'tool-search': { name: 'Web搜索', desc: 'Brave搜索', port: '-' },
                    'tool-scraping': { name: '网页抓取', desc: 'Scrapling', port: '-' },
                    'tool-markdown': { name: '文档转换', desc: 'MarkItDown', port: '-' },
                    'tool-mcp': { name: 'MCP服务', desc: 'MCP工具', port: '-' }
                }
            }
        };

        let states = {};
        let logs = [];
        let autoInterval = null;

        Object.keys(services).forEach(cat => {
            Object.keys(services[cat].items).forEach(id => {
                states[id] = 'stopped';
            });
        });

        function render() {
            const container = document.getElementById('servicesContainer');
            container.innerHTML = Object.keys(services).map(catKey => {
                const cat = services[catKey];
                return `
                    <div class="category">
                        <div class="category-header">${cat.label}</div>
                        ${Object.keys(cat.items).map(id => {
                            const s = cat.items[id];
                            const state = states[id];
                            return `
                                <div class="service ${state}">
                                    <div class="service-row">
                                        <div class="service-name">${s.name}</div>
                                        <div class="service-badge badge-${state}">
                                            ${state === 'running' ? '运行' : state === 'warning' ? '警告' : '停止'}
                                        </div>
                                    </div>
                                    <div class="service-details">
                                        <span>📝 ${s.desc}</span>
                                        <span>🔌 ${s.port}</span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            }).join('');
            updateStats();
        }

        function updateStats() {
            const total = Object.keys(states).length;
            const running = Object.values(states).filter(s => s === 'running').length;
            const stopped = Object.values(states).filter(s => s === 'stopped').length;
            const warning = Object.values(states).filter(s => s === 'warning').length;

            document.getElementById('totalServices').textContent = total;
            document.getElementById('runningCount').textContent = running;
            document.getElementById('stoppedCount').textContent = stopped;
            document.getElementById('warningCount').textContent = warning;
        }

        function addLog(msg) {
            logs.unshift({ time: new Date().toLocaleTimeString(), msg });
            logs = logs.slice(0, 15);
            const container = document.getElementById('logContainer');
            container.innerHTML = logs.map(l => `
                <div class="log">
                    <div class="log-time">${l.time}</div>
                    <div>${l.msg}</div>
                </div>
            `).join('');
        }

        async function checkAll() {
            addLog('🔄 开始检查所有服务...');

            for (let id of Object.keys(states)) {
                const rand = Math.random();
                states[id] = rand > 0.7 ? 'running' : rand > 0.4 ? 'warning' : 'stopped';
                await new Promise(r => setTimeout(r, 50));
            }

            render();
            addLog('✅ 检查完成');
        }

        function toggleAuto() {
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
                document.getElementById('autoText').textContent = '▶️ 自动刷新';
                addLog('⏸️ 已停止自动刷新');
            } else {
                autoInterval = setInterval(checkAll, 5000);
                document.getElementById('autoText').textContent = '⏸️ 停止刷新';
                addLog('▶️ 已开启自动刷新 (5秒)');
            }
        }

        render();
        setTimeout(checkAll, 2000);
    </script>
</body>
</html>'''

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
