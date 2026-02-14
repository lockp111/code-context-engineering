# 项目概览

> 首次接触项目或需完整架构图时加载

## 基本信息

| 属性         | 值                              |
| ------------ | ------------------------------- |
| **名称**     | [项目名称]                      |
| **类型**     | [Web App / API / CLI / Library] |
| **主语言**   | [TypeScript / Python / Go]      |
| **框架**     | [Express / Next.js / FastAPI]   |
| **描述**     | [一句话描述]                    |
| **更新触发** | 新增模块、引入新依赖、重大重构  |

## Ubiquitous Language

> 统一术语含义，避免歧义

| 术语      | 定义                   | 对应代码       | 备注                  |
| --------- | ---------------------- | -------------- | --------------------- |
| **User**  | 注册并登录的终端用户   | `models/User`  | 不包含管理员          |
| **Admin** | 后台管理人员           | `models/Admin` | 与 User 表隔离        |
| **Order** | 用户购买商品的交易记录 | `models/Order` |                       |
| **SKU**   | 库存最小单位           | `models/Sku`   | 注意与 Product 的区别 |

## 目录结构

```
project-root/
├── src/
│   ├── routes/          # API 路由
│   ├── services/        # 业务逻辑
│   ├── repositories/    # 数据访问
│   ├── models/          # 数据模型
│   ├── middleware/      # 中间件
│   ├── utils/           # 工具函数
│   └── index.ts         # 入口
├── tests/               # 测试
├── migrations/          # 数据库迁移
└── config/              # 配置
```

## Entry Points

> 最小代价跑通全流程

| 场景           | 入口文件         | 启动命令         | 关键断点位置                      |
| -------------- | ---------------- | ---------------- | --------------------------------- |
| **Web Server** | `src/index.ts`   | `npm run dev`    | `src/middleware/auth.ts`          |
| **Worker**     | `src/worker.ts`  | `npm run worker` | `src/jobs/processOrder.ts`        |
| **Tests**      | `jest.config.js` | `npm test`       | `tests/integration/order.test.ts` |

## 核心模块详情

### auth - 认证授权
| 属性     | 值                                              |
| -------- | ----------------------------------------------- |
| 路径     | `src/services/auth.ts`                          |
| 职责     | 登录、注册、Token、权限                         |
| 复杂度   | 🟠 中                                            |
| 关键函数 | `login()`, `verifyToken()`, `checkPermission()` |
| 依赖     | user, cache                                     |

### order - 订单管理
| 属性     | 值                                          |
| -------- | ------------------------------------------- |
| 路径     | `src/services/order.ts`                     |
| 职责     | 创建、状态流转、取消退款                    |
| 复杂度   | 🔴 高                                        |
| 关键函数 | `create()`, `pay()`, `cancel()`, `refund()` |
| 依赖     | payment, inventory, user                    |

### payment - 支付集成
| 属性   | 值                          |
| ------ | --------------------------- |
| 路径   | `src/services/payment/`     |
| 职责   | 第三方支付、回调处理        |
| 复杂度 | 🔴 高                        |
| 注意   | 涉及资金，修改需双人 Review |

## 关键依赖

### 生产依赖

| 包           | 版本  | 用途      | 注意               |
| ------------ | ----- | --------- | ------------------ |
| express      | ^4.18 | Web 框架  | -                  |
| prisma       | ^5.0  | ORM       | 修改 schema 需迁移 |
| redis        | ^4.0  | 缓存/会话 | 集群配置不同       |
| jsonwebtoken | ^9.0  | JWT       | 密钥在环境变量     |
| zod          | ^3.22 | 参数校验  | -                  |

### 第三方服务

| 服务       | 用途     | 接入文档   |
| ---------- | -------- | ---------- |
| 支付宝     | 在线支付 | [沙箱文档] |
| 阿里云 OSS | 文件存储 | [SDK 文档] |
| 阿里云短信 | 验证码   | [API 文档] |

## 技术决策

| 决策 | 选择   | 原因                 |
| ---- | ------ | -------------------- |
| ORM  | Prisma | 类型安全、迁移方便   |
| 缓存 | Redis  | 分布式、数据结构丰富 |
| 认证 | JWT    | 无状态、易扩展       |
| 校验 | Zod    | 类型推导、错误友好   |
