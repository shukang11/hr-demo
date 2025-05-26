# HR-Demo 桌面应用编译与使用指南

本文档提供关于如何编译 HR-Demo 桌面应用、支持多平台构建以及可用配置选项的详细说明。

## 1. 如何编译桌面应用

HR-Demo 桌面应用使用 PyInstaller 打包，支持在 macOS、Windows 和 Linux 系统上构建。根据您的操作系统，可以选择相应的构建方法。

### 1.1 前置条件

在开始构建前，请确保已安装以下依赖：

- Python 3.9+ 
- Node.js 16+ 或 Bun 1.0+
- UV 包管理工具 (`pip install uv`)

### 1.2 macOS/Linux 平台构建

在 macOS 或 Linux 系统上，使用提供的 `build.sh` 脚本进行构建：

```bash
# 切换到项目根目录
cd /path/to/hr-demo

# 运行构建脚本
./desktop/build.sh
```

构建过程包括以下步骤：
1. 检查环境依赖
2. 构建前端应用
3. 安装后端依赖
4. 使用 PyInstaller 打包应用
5. 生成最终的应用包

构建完成后，应用将位于 `desktop/dist/` 目录下：
- macOS: `HR-Desktop.app` 应用包
- Linux: `HR-Desktop` 可执行文件

### 1.3 Windows 平台构建

在 Windows 系统上，使用提供的 `build.bat` 脚本进行构建：

```
# 切换到项目根目录
cd C:\path\to\hr-demo

# 运行构建脚本
desktop\build.bat
```

构建完成后，可执行文件将位于 `desktop\dist\HR-Desktop.exe`。

### 1.4 手动构建步骤

若需要手动控制构建过程，可以分步执行以下命令：

```bash
# 1. 安装后端依赖
cd /path/to/hr-demo/api
uv sync --group desktop

# 2. 构建前端
cd /path/to/hr-demo/web
bun install
bun run build:desktop

# 3. 运行 PyInstaller
cd /path/to/hr-demo/desktop
pyinstaller hr_desktop.spec --clean
```

## 2. 如何编译其他平台的桌面应用

### 2.1 跨平台构建策略

HR-Demo 桌面应用支持所有主要桌面平台，但通常需要在目标平台上进行构建。以下是每个平台的构建说明：

### 2.2 在 macOS 上构建

```bash
# 构建 macOS 版本
cd /path/to/hr-demo
./desktop/build.sh
```

macOS 构建将生成 `.app` 应用包，支持 Intel 和 Apple Silicon 处理器。

### 2.3 在 Windows 上构建

```
# 构建 Windows 版本
cd C:\path\to\hr-demo
desktop\build.bat
```

Windows 构建将生成 `.exe` 可执行文件。

### 2.4 在 Linux 上构建

```bash
# 构建 Linux 版本
cd /path/to/hr-demo
./desktop/build.sh
```

Linux 构建将生成可执行文件。

### 2.5 高级：使用容器跨平台构建

对于需要在一个平台上构建多个平台版本的情况，可以考虑使用 Docker 容器：

```bash
# 构建 Linux 版本（在任何平台上）
docker run --rm -v "$(pwd):/app" -w /app python:3.11 ./desktop/build.sh

# 构建 Windows 版本（需要 Windows 容器）
# 注意：这需要特殊配置，不是所有环境都支持
```

注意：苹果的许可政策限制了 macOS 只能在 Apple 硬件上构建，无法通过容器跨平台构建。

## 3. 桌面应用设置选项

HR-Demo 桌面应用提供了多种配置选项，可以通过修改 `desktop/config.py` 文件进行自定义。

### 3.1 基础配置选项

| 配置项            | 描述         | 默认值       |
| ----------------- | ------------ | ------------ |
| APP_NAME          | 应用名称     | "HR管理系统" |
| APP_VERSION       | 应用版本     | "1.0.0"      |
| WINDOW_WIDTH      | 窗口宽度     | 1200         |
| WINDOW_HEIGHT     | 窗口高度     | 800          |
| WINDOW_MIN_WIDTH  | 最小窗口宽度 | 800          |
| WINDOW_MIN_HEIGHT | 最小窗口高度 | 600          |

### 3.2 服务器配置

| 配置项      | 描述           | 默认值      |
| ----------- | -------------- | ----------- |
| SERVER_HOST | 本地服务器主机 | "127.0.0.1" |
| SERVER_PORT | 本地服务器端口 | 5000        |

### 3.3 数据配置

| 配置项        | 描述           | 默认值                              |
| ------------- | -------------- | ----------------------------------- |
| DATABASE_PATH | 本地数据库路径 | BASE_DIR / "data" / "hr_desktop.db" |

### 3.4 修改配置示例

要修改应用配置，请编辑 `desktop/config.py` 文件：

```python
# 修改窗口大小和标题
APP_NAME = "我的HR系统"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# 修改服务器端口（如果默认端口被占用）
SERVER_PORT = 5001

# 修改数据库路径
DATABASE_PATH = Path.home() / "hr_data" / "database.db"
```

### 3.5 高级构建配置

构建过程可以通过修改 `hr_desktop.spec` 文件进行高级配置：

| 配置项        | 描述                             |
| ------------- | -------------------------------- |
| hiddenimports | 添加需要包含的Python模块         |
| excludes      | 排除不需要的Python模块以减小体积 |
| datas         | 添加额外的数据文件               |
| icon          | 设置应用图标                     |

示例：添加自定义图标
```python
# 在 hr_desktop.spec 中
exe = EXE(
    # ...
    icon='desktop/assets/icon.ico',  # Windows图标
)

# macOS图标
app = BUNDLE(
    exe,
    name='HR-Desktop.app',
    icon='desktop/assets/icon.icns',  # macOS图标
    # ...
)
```

## 4. 故障排除

### 4.1 常见问题解决

1. **端口占用问题**  
   错误信息：`地址已被使用`  
   解决方案：修改 `config.py` 中的 `SERVER_PORT` 为其他未使用的端口

2. **依赖问题**  
   错误信息：`找不到模块xxx`  
   解决方案：在 `hr_desktop.spec` 的 `hiddenimports` 列表中添加缺失的模块

3. **窗口显示问题**  
   问题：窗口大小不正确或UI显示异常  
   解决方案：调整 `config.py` 中的窗口尺寸设置

4. **打包大小过大**  
   解决方案：在 `hr_desktop.spec` 的 `excludes` 列表中添加不需要的大型库

### 4.2 日志查看

如果应用无法正常启动或运行，可以通过以下方式查看详细日志：

```bash
# macOS
/Volumes/Storage/workspace/project/hr-demo/desktop/dist/HR-Desktop.app/Contents/MacOS/HR-Desktop

# Windows (使用CMD)
C:\path\to\hr-demo\desktop\dist\HR-Desktop.exe --debug

# Linux
./HR-Desktop --debug
```

## 5. 最佳实践

1. **测试构建**：在发布前，使用 `test_final.py` 脚本测试打包应用是否正常工作
2. **版本管理**：更新应用时，同步修改 `config.py` 中的 `APP_VERSION` 值
3. **数据备份**：定期备份 `DATABASE_PATH` 指向的数据库文件
4. **性能优化**：按需调整 `excludes` 列表，去除不需要的模块减小应用体积
5. **权限处理**：确保应用有足够权限访问所需资源，尤其是数据库文件

---

_文档更新日期: 2025年5月26日_
