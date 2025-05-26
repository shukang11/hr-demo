# 项目结构说明

## 项目整体结构

HR-Demo 项目采用 Rust + Web + Tauri 的架构，主要由以下部分组成：

- `crates/` - Rust 后端库和服务
- `src/` - 前端应用（React + Vite）
- `src-tauri/` - Tauri 桌面应用集成
- `document/` - 项目文档

## 前端结构 (src/)

```
src/
├── App.css                   # 主应用样式
├── App.tsx                   # 主应用组件
├── globals.css               # 全局样式
├── main.tsx                  # 应用入口点
├── vite-env.d.ts             # Vite环境类型定义
├── app/                      # 应用页面
│   ├── about/                # 关于页面
│   ├── auth/                 # 认证相关页面
│   │   └── login/            # 登录页面
│   ├── candidate/            # 候选人管理
│   ├── company/              # 公司管理
│   ├── customfield/          # 自定义字段
│   ├── dashboard/            # 仪表盘
│   ├── department/           # 部门管理
│   ├── employee/             # 员工管理
│   └── position/             # 职位管理
├── assets/                   # 静态资源
│   └── react.svg            
├── components/               # 共享组件
│   ├── app-sidebar.tsx       # 应用侧边栏
│   ├── providers.tsx         # 上下文提供者
│   ├── theme-provider.tsx    # 主题提供者
│   ├── charts/               # 图表组件
│   ├── company/              # 公司相关组件
│   ├── customfield/          # 自定义字段组件
│   └── ui/                   # UI组件
├── hooks/                    # 自定义React Hooks
│   ├── use-company-store.ts  # 公司状态管理
│   ├── use-debounce.ts       # 防抖Hook
│   ├── use-mobile.tsx        # 移动设备检测
│   └── use-toast.ts          # 提示消息
├── layout/                   # 布局组件
│   ├── app.tsx               # 应用布局
│   ├── auth.tsx              # 认证布局
│   └── root.tsx              # 根布局
└── lib/                      # 工具库
    ├── routes.ts             # 路由定义
    ├── types.ts              # 类型定义
    ├── utils.ts              # 工具函数
    ├── api/                  # API客户端
    ├── auth/                 # 认证工具
    └── type/                 # 类型定义
```

## Rust后端结构 (crates/)

```
crates/
├── examples/                 # 示例代码
│   ├── Cargo.toml            # 示例项目配置
│   └── migrate.rs            # 数据库迁移示例
├── lib/                      # 核心库
│   ├── lib-api/              # API服务
│   │   ├── Cargo.toml        # API库配置
│   │   ├── examples/         # API使用示例
│   │   │   └── run_api.rs    # 运行API服务示例
│   │   └── src/              # 源代码
│   │       ├── error.rs      # 错误处理
│   │       ├── handlers/     # 请求处理器
│   │       ├── lib.rs        # 库入口
│   │       ├── middlewares/  # 中间件
│   │       ├── response.rs   # 响应处理
│   │       ├── routes.rs     # 路由定义
│   │       └── server.rs     # 服务器实现
│   ├── lib-core/             # 核心业务逻辑
│   │   ├── Cargo.toml        # 核心库配置
│   │   └── src/              # 源代码
│   │       ├── lib.rs        # 库入口
│   │       └── services/     # 业务服务
│   │           ├── company.rs     # 公司服务
│   │           ├── department.rs  # 部门服务
│   │           ├── json_value.rs  # JSON值服务
│   │           └── position.rs    # 职位服务
│   ├── lib-entity/           # 数据实体
│   │   ├── Cargo.toml        # 实体库配置
│   │   └── src/              # 源代码
│   │       ├── entities/     # 数据表实体
│   │       └── lib.rs        # 库入口
│   ├── lib-schema/           # 数据架构
│   │   ├── Cargo.toml        # 架构库配置
│   │   └── src/              # 源代码
│   │       ├── common/       # 通用组件
│   │       │   └── page.rs   # 分页处理
│   │       ├── lib.rs        # 库入口
│   │       └── models/       # 数据模型
│   │           ├── company.rs    # 公司模型
│   │           ├── json_value.rs # JSON值模型
│   │           └── position.rs   # 职位模型
│   └── lib-utils/            # 工具库
│       ├── Cargo.toml        # 工具库配置
│       └── src/              # 源代码
│           ├── config.rs     # 配置处理
│           └── lib.rs        # 库入口
└── migration/                # 数据库迁移
    ├── Cargo.toml            # 迁移库配置
    ├── README.md             # 迁移说明
    └── src/                  # 源代码
        ├── lib.rs            # 库入口
        ├── m20241207_161705_init_tables.rs         # 初始表结构
        ├── m20241223_candidates.rs                 # 候选人表
        └── m20250212_001017_add_marital_emergency_contact.rs # 婚姻&紧急联系人
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

## Tauri桌面应用 (src-tauri/)

```
src-tauri/
├── build.rs                  # 构建脚本
├── Cargo.toml                # Rust项目配置
├── tauri.conf.json           # Tauri配置
├── capabilities/             # 权限配置
│   └── default.json          # 默认权限
├── gen/                      # 生成的代码
│   └── schemas/              # API模式
├── icons/                    # 应用图标
│   ├── 32x32.png             # 32x32图标
│   ├── 128x128.png           # 128x128图标
│   ├── icon.icns             # macOS图标
│   ├── icon.ico              # Windows图标
│   └── ...                   # 其他图标
└── src/                      # 源代码
    ├── lib.rs                # 库入口
    └── main.rs               # 主程序入口

```

## 根目录文件

```
/
├── bun.lockb                 # Bun锁定文件
├── Cargo.lock                # Cargo锁定文件
├── Cargo.toml                # Rust项目配置
├── components.json           # UI组件配置
├── docker-compose.yml        # Docker Compose配置
├── Dockerfile.backend        # 后端Docker配置
├── Dockerfile.frontend       # 前端Docker配置
├── index.html                # 主HTML入口
├── package.json              # 项目配置和依赖
├── postcss.config.js         # PostCSS配置
├── README.md                 # 项目说明
├── tailwind.config.js        # Tailwind CSS配置
├── tsconfig.json             # TypeScript配置
└── vite.config.ts            # Vite配置
```

## 技术栈

### 前端技术
- Bun - JavaScript运行时和包管理器
- Vite - 前端构建工具
- React - 用户界面库
- Tauri - 桌面应用框架
- Shadcn - UI组件库
- TailwindCSS - 实用程序优先的CSS框架

### 后端技术
- Rust - 系统编程语言
- Tokio - 异步运行时
- Axum - Web框架
- Sea-ORM - 数据库ORM
- SQLite - 嵌入式数据库