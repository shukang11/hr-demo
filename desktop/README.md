# Desktop Application

这个目录包含将 HR-Demo 打包为桌面应用的相关文件。

## 文件说明

- `main.py` - 桌面应用启动入口
- `config.py` - 桌面应用配置
- `requirements.txt` - 桌面应用依赖
- `build/` - 构建输出目录
- `assets/` - 应用图标等资源
- `static/` - 前端构建文件（由构建过程生成）
- `hr_desktop.spec` - PyInstaller 打包配置文件
- `build.sh` - macOS/Linux 构建脚本
- `build.bat` - Windows 构建脚本
- `hooks/` - PyInstaller 钩子目录

## 使用方法

1. 安装依赖：`uv sync --group desktop`
2. 构建前端：`cd ../web && bun run build`
3. 运行桌面应用：`python main.py`

## 构建说明

### 快速构建

使用提供的构建脚本快速构建桌面应用：

```bash
# macOS/Linux
./build.sh

# Windows
build.bat
```

### 详细文档

完整的应用编译和配置文档，请参考：[桌面应用编译与使用指南](/document/desktop-application-guide.md)
