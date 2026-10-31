#!/usr/bin/env bash
# 一键安装：创建虚拟环境、安装依赖并自检
set -e

cd "$(dirname "$0")"

echo "==> 检查 Python"
if ! command -v python3 >/dev/null 2>&1; then
    echo "未找到 python3，请先安装 Python 3"
    exit 1
fi
python3 --version

echo "==> 检查系统依赖 libzbar（Pyzbar 必需）"
if ! ldconfig -p 2>/dev/null | grep -q libzbar; then
    echo "缺少 ZBar 动态库，请先执行："
    echo "    sudo apt install libzbar0"
    exit 1
fi

echo "==> 创建虚拟环境"
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

echo "==> 安装 Python 依赖"
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "==> 自检"
.venv/bin/python -c "import cv2; print('opencv', cv2.__version__)"
.venv/bin/python -c "from pyzbar.pyzbar import decode; print('pyzbar OK')"
.venv/bin/python -c "import paho.mqtt.client; print('paho-mqtt OK')"

echo
echo "安装完成。执行 ./run.sh 启动程序。"
echo "MQTT 推送默认关闭，需要时在 src/config.py 中设置 MQTT_ENABLED = True。"
