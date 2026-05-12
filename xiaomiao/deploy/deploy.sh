#!/bin/bash
# ============================================
# 小喵 QQ 机器人 - Linux 一键部署脚本
# 适用于：宝塔面板 / CentOS / Ubuntu / Debian
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
BOT_DIR="/www/wwwroot/xiaomiaoVirtual"
QQ_ACCOUNT=""
NAPCAT_WEBUI_PORT=6099
NAPCAT_WS_PORT=5004

# 打印带颜色的信息
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 显示 Banner
show_banner() {
    echo -e "${GREEN}"
    echo "============================================"
    echo "   小喵 QQ 机器人 - 一键部署脚本"
    echo "   XiaoMiao QQ Bot Deployment Script"
    echo "============================================"
    echo -e "${NC}"
}

# 检查 root 权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "请使用 root 用户运行此脚本: sudo bash deploy.sh"
    fi
}

# 检查系统
check_system() {
    info "检查系统环境..."
    
    if [ -f /etc/redhat-release ] || [ -f /etc/opencloudos-release ]; then
        OS="centos"
        PKG_MANAGER="yum"
    elif [ -f /etc/debian_version ]; then
        OS="debian"
        PKG_MANAGER="apt"
    elif grep -qi "opencloudos\|centos\|rhel\|fedora" /etc/os-release 2>/dev/null; then
        OS="centos"
        PKG_MANAGER="yum"
    elif grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
        OS="debian"
        PKG_MANAGER="apt"
    else
        # Default to yum for unknown systems
        OS="centos"
        PKG_MANAGER="yum"
        warn "未知系统，尝试使用 yum"
    fi
    
    success "系统: $OS"
}

# 安装基础依赖
install_dependencies() {
    info "安装基础依赖..."
    
    if [ "$PKG_MANAGER" = "yum" ]; then
        # RHEL/CentOS/OpenCloudOS 系列
        yum install -y python3 python3-pip docker unzip wget curl || true
        # python3-venv 在 RHEL 系列中不存在，使用 dnf 安装 virtualenv
        dnf install -y python3-virtualenv 2>/dev/null || yum install -y python3-virtualenv || true
    else
        # Debian/Ubuntu 系列
        apt update -y
        apt install -y python3 python3-pip python3-venv docker.io unzip wget curl
    fi
    
    # 启动 Docker
    systemctl start docker 2>/dev/null || true
    systemctl enable docker 2>/dev/null || true
    
    success "依赖安装完成"
}

# 获取 QQ 号
get_qq_account() {
    echo ""
    read -p "请输入机器人 QQ 号: " QQ_ACCOUNT
    
    if [ -z "$QQ_ACCOUNT" ]; then
        error "QQ 号不能为空"
    fi
    
    success "QQ 号: $QQ_ACCOUNT"
}

# 创建目录结构
setup_directories() {
    info "创建目录结构..."
    
    mkdir -p "$BOT_DIR"
    mkdir -p "$BOT_DIR/logs"
    mkdir -p "$BOT_DIR/temps"
    mkdir -p "$BOT_DIR/napcat_data"
    
    success "目录创建完成: $BOT_DIR"
}

# 解压项目文件
extract_files() {
    info "解压项目文件..."
    
    # 检查是否有 zip 文件
    if [ -f "$BOT_DIR/xiaomiaoVirtual.zip" ]; then
        cd "$BOT_DIR"
        unzip -o xiaomiaoVirtual.zip
        rm -f xiaomiaoVirtual.zip
        success "项目文件解压完成"
    else
        warn "未找到 xiaomiaoVirtual.zip，请手动上传项目文件到 $BOT_DIR"
    fi
}

# 创建 Python 虚拟环境
setup_python_env() {
    info "创建 Python 虚拟环境..."
    
    cd "$BOT_DIR"
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        success "Python 依赖安装完成"
    else
        warn "未找到 requirements.txt"
    fi
}

# 部署 NapCat Docker
deploy_napcat() {
    info "部署 NapCat Docker..."
    
    # 停止并删除旧容器
    docker stop napcat 2>/dev/null || true
    docker rm napcat 2>/dev/null || true
    
    # 拉取最新镜像
    docker pull mlikiowa/napcat-docker:latest
    
    # 运行容器
    docker run -d \
        --name napcat \
        -e ACCOUNT="$QQ_ACCOUNT" \
        -e WS_ENABLE=true \
        -e NAPCAT_GID=$(id -g) \
        -e NAPCAT_UID=$(id -u) \
        -p 3000:3000 \
        -p $NAPCAT_WS_PORT:3001 \
        -p $NAPCAT_WEBUI_PORT:6099 \
        -v "$BOT_DIR/napcat_data:/app/napcat/config" \
        --restart always \
        mlikiowa/napcat-docker:latest
    
    success "NapCat Docker 部署完成"
}

# 配置 NapCat WebSocket
configure_napcat() {
    info "等待 NapCat 启动..."
    sleep 10
    
    # 创建 OneBot11 配置
    NAPCAT_CONFIG_DIR="$BOT_DIR/napcat_data"
    mkdir -p "$NAPCAT_CONFIG_DIR"
    
    cat > "$NAPCAT_CONFIG_DIR/onebot11_$QQ_ACCOUNT.json" << EOF
{
    "network": {
        "httpServers": [],
        "httpClients": [],
        "websocketServers": [
            {
                "name": "Bot",
                "enable": true,
                "host": "0.0.0.0",
                "port": 3001,
                "token": "",
                "heartInterval": 30000,
                "enableForcePushEvent": true,
                "debug": false,
                "messagePostFormat": "array"
            }
        ],
        "websocketClients": []
    },
    "musicSignUrl": "",
    "enableLocalFile2Url": true,
    "parseMultMsg": true
}
EOF
    
    success "NapCat 配置完成"
}

# 更新机器人配置
update_bot_config() {
    info "更新机器人配置..."
    
    cd "$BOT_DIR"
    
    if [ -f "config.json" ]; then
        # 使用 Python 更新配置
        python3 << EOF
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

config['Connection']['host'] = '127.0.0.1'
config['Connection']['port'] = $NAPCAT_WS_PORT

with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print('配置更新完成')
EOF
        success "机器人配置更新完成"
    else
        warn "未找到 config.json，请手动配置"
    fi
}

# 创建启动脚本
create_start_script() {
    info "创建启动脚本..."
    
    cat > "$BOT_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF
    
    chmod +x "$BOT_DIR/start.sh"
    
    # 创建停止脚本
    cat > "$BOT_DIR/stop.sh" << 'EOF'
#!/bin/bash
pkill -f "python main.py" || true
echo "机器人已停止"
EOF
    
    chmod +x "$BOT_DIR/stop.sh"
    
    # 创建重启脚本
    cat > "$BOT_DIR/restart.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./stop.sh
sleep 2
nohup ./start.sh > logs/bot.log 2>&1 &
echo "机器人已重启"
EOF
    
    chmod +x "$BOT_DIR/restart.sh"
    
    success "启动脚本创建完成"
}

# 创建 Systemd 服务
create_systemd_service() {
    info "创建 Systemd 服务..."
    
    cat > /etc/systemd/system/xiaomiao-bot.service << EOF
[Unit]
Description=XiaoMiao QQ Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/main.py
ExecStop=/bin/kill -SIGTERM \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable xiaomiao-bot
    
    success "Systemd 服务创建完成"
}

# 显示登录信息
show_login_info() {
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}           部署完成！${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${YELLOW}【重要】首次登录步骤：${NC}"
    echo ""
    echo "1. 查看 NapCat 登录二维码："
    echo -e "   ${BLUE}docker logs -f napcat${NC}"
    echo ""
    echo "2. 或访问 NapCat WebUI："
    echo -e "   ${BLUE}http://你的服务器IP:$NAPCAT_WEBUI_PORT${NC}"
    echo ""
    echo "3. 扫码登录后，启动机器人："
    echo -e "   ${BLUE}systemctl start xiaomiao-bot${NC}"
    echo ""
    echo -e "${YELLOW}【常用命令】${NC}"
    echo "启动机器人: systemctl start xiaomiao-bot"
    echo "停止机器人: systemctl stop xiaomiao-bot"
    echo "重启机器人: systemctl restart xiaomiao-bot"
    echo "查看状态:   systemctl status xiaomiao-bot"
    echo "查看日志:   journalctl -u xiaomiao-bot -f"
    echo ""
    echo "重启 NapCat: docker restart napcat"
    echo "查看 NapCat 日志: docker logs -f napcat"
    echo ""
    echo -e "${GREEN}============================================${NC}"
}

# 主函数
main() {
    show_banner
    check_root
    check_system
    get_qq_account
    install_dependencies
    setup_directories
    extract_files
    setup_python_env
    deploy_napcat
    configure_napcat
    update_bot_config
    create_start_script
    create_systemd_service
    show_login_info
}

# 运行主函数
main "$@"
