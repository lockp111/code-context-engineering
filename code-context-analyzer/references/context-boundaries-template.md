# 上下文边界

> 仅当开发特定功能模块或不确定文件边界时加载此文件

## 功能模块边界

| 功能 | 关注 | 忽略 |
| ---- | ---- | ---- |
| 用户模块 | `services/user.ts`, `repositories/user.ts`, `models/user.ts` | admin/, billing/, payment/ |
| 订单模块 | `services/order.ts`, `repositories/order.ts`, `models/order*.ts` | user/, admin/ |
| 支付模块 | `services/payment/`, `models/payment.ts` | user/, components/ |
| 认证模块 | `services/auth.ts`, `middleware/auth.ts` | components/, styles/ |

## 开发类型边界

### API 开发
```
关注: routes/, services/, repositories/, middleware/, types/
忽略: components/, pages/, styles/, public/
```

### 前端开发
```
关注: components/, pages/, styles/, hooks/, stores/
忽略: services/, repositories/, migrations/
```

### 数据库开发
```
关注: models/, repositories/, migrations/, database-schema.md
忽略: components/, routes/, styles/
```

### 测试开发
```
关注: tests/, __mocks__/, jest.config.js, test-utils/
忽略: styles/, docs/, public/
```

### 配置/部署
```
关注: config/, scripts/, Dockerfile, docker-compose.yml, .env.*
忽略: components/, tests/unit/
```

## 跨模块依赖

| 模块 | 可依赖 | 禁止依赖 |
| ---- | ------ | -------- |
| routes | services, middleware | repositories, models |
| services | repositories, 其他 services | routes, components |
| repositories | models | services, routes |
| middleware | services, utils | repositories |
| components | hooks, stores, utils | services, repositories |

## 文件组织原则

| 原则 | 说明 |
| ---- | ---- |
| 按功能分组 | `features/order/` 包含该功能所有文件 |
| 单一职责 | 每个文件只做一件事 |
| 依赖向下 | 上层依赖下层，禁止反向 |
| 公共提取 | 多处使用的提取到 `shared/` |
