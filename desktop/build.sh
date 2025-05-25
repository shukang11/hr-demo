#!/bin/bash
# HR-Demo 桌面应用打包脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="${PROJECT_ROOT}/desktop"
API_DIR="${PROJECT_ROOT}/api"
WEB_DIR="${PROJECT_ROOT}/web"

echo -e "${BLUE}🚀 开始构建 HR-Demo 桌面应用${NC}"

# 1. 检查依赖
echo -e "${YELLOW}📋 检查依赖...${NC}"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python 未安装${NC}"
    exit 1
fi

# 检查 Node.js 环境 (for frontend build)
if ! command -v bun &> /dev/null; then
    echo -e "${RED}❌ Bun 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 依赖检查完成${NC}"

# 2. 构建前端
echo -e "${YELLOW}🔨 构建前端应用...${NC}"
cd "${WEB_DIR}"

# 安装依赖
bun install

# 构建桌面版本
bun run build:desktop

echo -e "${GREEN}✅ 前端构建完成${NC}"

# 3. 安装后端依赖
echo -e "${YELLOW}📦 安装后端依赖...${NC}"
cd "${API_DIR}"

# 确保安装了桌面相关依赖
uv sync --group desktop

echo -e "${GREEN}✅ 后端依赖安装完成${NC}"

# 4. 运行 PyInstaller
echo -e "${YELLOW}📦 开始打包应用...${NC}"
cd "${DESKTOP_DIR}"

# 清理之前的构建
rm -rf build/ dist/

# 使用 PyInstaller 打包
pyinstaller hr_desktop.spec --clean --noconfirm

echo -e "${GREEN}✅ 应用打包完成${NC}"

# 5. 检查输出
OUTPUT_DIR="${DESKTOP_DIR}/dist"
if [[ "$OSTYPE" == "darwin"* ]]; then
    APP_FILE="${OUTPUT_DIR}/HR-Desktop.app"
    if [ -d "${APP_FILE}" ]; then
        echo -e "${GREEN}🎉 成功！应用已打包到: ${APP_FILE}${NC}"
        echo -e "${BLUE}💡 使用以下命令启动: open '${APP_FILE}'${NC}"
    else
        echo -e "${RED}❌ 打包失败：未找到应用文件${NC}"
        exit 1
    fi
else
    EXE_FILE="${OUTPUT_DIR}/HR-Desktop"
    if [ -f "${EXE_FILE}" ]; then
        echo -e "${GREEN}🎉 成功！应用已打包到: ${EXE_FILE}${NC}"
        echo -e "${BLUE}💡 使用以下命令启动: ${EXE_FILE}${NC}"
    else
        echo -e "${RED}❌ 打包失败：未找到可执行文件${NC}"
        exit 1
    fi
fi

# 6. 显示文件大小
echo -e "${YELLOW}📏 文件大小信息:${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    du -sh "${OUTPUT_DIR}/HR-Desktop.app"
else
    du -sh "${OUTPUT_DIR}/HR-Desktop"
fi

echo -e "${GREEN}🔥 构建完成！${NC}"
