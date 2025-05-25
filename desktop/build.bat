@echo off
REM HR-Demo 桌面应用打包脚本 (Windows)

setlocal enabledelayedexpansion

echo 🚀 开始构建 HR-Demo 桌面应用

REM 项目路径
set "PROJECT_ROOT=%~dp0.."
set "DESKTOP_DIR=%PROJECT_ROOT%\desktop"
set "API_DIR=%PROJECT_ROOT%\api"
set "WEB_DIR=%PROJECT_ROOT%\web"

REM 1. 检查依赖
echo 📋 检查依赖...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    pause
    exit /b 1
)

where bun >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Bun 未安装
    pause
    exit /b 1
)

echo ✅ 依赖检查完成

REM 2. 构建前端
echo 🔨 构建前端应用...
cd /d "%WEB_DIR%"

bun install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)

bun run build:desktop
if %errorlevel% neq 0 (
    echo ❌ 前端构建失败
    pause
    exit /b 1
)

echo ✅ 前端构建完成

REM 3. 安装后端依赖
echo 📦 安装后端依赖...
cd /d "%API_DIR%"

uv sync --group desktop
if %errorlevel% neq 0 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)

echo ✅ 后端依赖安装完成

REM 4. 运行 PyInstaller
echo 📦 开始打包应用...
cd /d "%DESKTOP_DIR%"

REM 清理之前的构建
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 使用 PyInstaller 打包
pyinstaller hr_desktop.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo ❌ 应用打包失败
    pause
    exit /b 1
)

echo ✅ 应用打包完成

REM 5. 检查输出
set "OUTPUT_DIR=%DESKTOP_DIR%\dist"
set "EXE_FILE=%OUTPUT_DIR%\HR-Desktop.exe"

if exist "%EXE_FILE%" (
    echo 🎉 成功！应用已打包到: %EXE_FILE%
    echo 💡 双击可执行文件启动应用
) else (
    echo ❌ 打包失败：未找到可执行文件
    pause
    exit /b 1
)

echo 🔥 构建完成！
pause
