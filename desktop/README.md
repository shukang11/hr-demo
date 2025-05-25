# Desktop Application

这个目录包含将 HR-Demo 打包为桌面应用的相关文件。

## 文件说明

- `main.py` - 桌面应用启动入口
- `config.py` - 桌面应用配置
- `requirements.txt` - 桌面应用依赖
- `build/` - 构建输出目录
- `assets/` - 应用图标等资源
- `static/` - 前端构建文件（由构建过程生成）

## 使用方法

1. 安装依赖：`uv sync --group desktop`
2. 构建前端：`cd ../web && bun run build`
3. 运行桌面应用：`python main.py`
