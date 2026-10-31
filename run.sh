#!/usr/bin/env bash
# 启动程序
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "未找到 .venv，请先执行 ./install.sh"
    exit 1
fi

.venv/bin/python src/main.py
