# 项目结构说明

## 项目整体结构

HR-Demo 项目采用前后端分离的架构，主要由以下部分组成：

- `api/` - 后端服务（Flask）
- `web/` - 前端应用（React + Vite）
- `document/` - 项目文档

## 前端结构 (web/)

```
web/
├── bun.lock                  # Bun依赖锁定文件
├── index.html                # 主HTML入口
├── package.json              # 项目配置和依赖
├── postcss.config.js         # PostCSS配置
├── README.md                 # 前端项目说明
├── tailwind.config.js        # Tailwind CSS配置
├── tsconfig.json             # TypeScript配置
├── tsconfig.node.json        # Node环境TypeScript配置
├── vite.config.d.ts          # Vite配置类型定义
├── vite.config.js            # Vite构建工具配置
└── src/                      # 源代码目录
    ├── App.css               # 主应用样式
    ├── App.tsx               # 主应用组件
    ├── globals.css           # 全局样式
    ├── main.tsx              # 应用入口点
    ├── vite-env.d.ts         # Vite环境类型定义
    ├── app/                  # 应用页面
    │   ├── about/            # 关于页面
    │   ├── candidate/        # 候选人管理
    │   ├── company/          # 公司管理
    │   ├── dashboard/        # 仪表盘
    │   ├── department/       # 部门管理
    │   ├── employee/         # 员工管理
    │   └── position/         # 职位管理
    ├── assets/               # 静态资源
    ├── components/           # 共享组件
    │   ├── app-sidebar.tsx   # 应用侧边栏
    │   ├── providers.tsx     # 上下文提供者
    │   ├── theme-provider.tsx# 主题提供者
    │   └── ui/              # UI组件
    ├── hooks/                # 自定义React Hooks
    └── layout/               # 布局组件
        ├── app.tsx           # 应用布局
        ├── auth.tsx          # 认证布局
        └── root.tsx          # 根布局
```

## 后端结构 (api/)

```
api/
├── app.py                    # 应用入口点
├── commands.py               # 命令行工具
├── pyproject.toml            # Python项目配置
├── uv.lock                   # uv依赖锁定文件
├── configs/                  # 配置文件
│   ├── __init__.py
│   ├── _database.py          # 数据库配置
│   ├── create_config.py      # 配置创建
│   ├── deploy/               # 部署配置
│   └── feature/              # 功能配置
├── extensions/               # Flask扩展
│   ├── ext_compress.py       # 压缩扩展
│   ├── ext_database.py       # 数据库扩展
│   ├── ext_logging.py        # 日志扩展
│   ├── ext_login.py          # 登录扩展
│   └── ext_migrate.py        # 迁移扩展
├── fixture/                  # 测试数据
│   └── table.sql             # 表结构SQL
├── instance/                 # 实例特定配置
│   └── db.sqlite3            # SQLite数据库
├── libs/                     # 工具库
│   ├── helper.py             # 辅助函数
│   ├── models/               # 数据模型
│   └── schema/               # 数据架构
├── migrations/               # 数据库迁移
├── routes/                   # 路由定义
│   ├── __init__.py
│   ├── auth.py               # 认证路由
│   └── health.py             # 健康检查
├── services/                 # 业务服务
│   ├── __init__.py
│   ├── account/              # 账户服务
│   └── ...
└── tests/                    # 测试代码
```

## 文档结构 (document/)

```
document/
├── document-guide.md         # 文档管理指南
├── progress.md               # 当前版本规划与执行进度
├── status-report.md          # 当前版本问题与风险
├── structure.md              # 项目结构说明（本文档）
└── archive/                  # 历史版本文档存档
    └── {序号}-{版本内容}/     # 按版本存档的历史文档
```

## 技术栈

### 前端技术
- Bun - JavaScript运行时和包管理器
- Vite - 前端构建工具
- React - 用户界面库
- Shadcn - UI组件库
- TailwindCSS - 实用程序优先的CSS框架

### 后端技术
- UV - Python包管理工具
- Flask - Web框架
- Pydantic - 数据验证和设置管理
- SQLAlchemy - ORM和SQL工具包