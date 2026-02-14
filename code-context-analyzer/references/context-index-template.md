---
description: Code Context Index
alwaysApply: true
---
# {project_name} 上下文索引

## AI 行为指南

| 任务类型 | 行为 |
| -------- | ---- |
| 新增功能 | 查「关键路径」→ 遵循「代码规范」→ 查「常见陷阱」 |
| 修改现有代码 | 查「风险区域」→ 确认状态机/枚举 → 评估影响 |
| 修 Bug | 定位服务 → 校验状态转换 → 查关联表约束 |
| 数据库变更 | 🔴 只追加 migration → 更新 `database-schema.md` |

## 项目概览

| 主语言 | 框架 | 包管理 | 规模 |
| ------ | ---- | ------ | ---- |
| {languages} | {frameworks} | {package_manager} | {total_files} 文件 / ~{total_lines} 行 |

**入口**: `src/index.ts` → `src/app.ts` → `src/routes/`

## 关键路径

| 功能 | 文件 | 核心函数 |
| ---- | ---- | -------- |
| 用户认证 | `services/auth.ts` | `login()`, `register()`, `verifyToken()` |
| 订单处理 | `services/order.ts` | `create()`, `pay()`, `cancel()` |
| 支付集成 | `services/payment.ts` | `charge()`, `refund()`, `handleCallback()` |
| 数据访问 | `repositories/*.ts` | `findById()`, `create()`, `update()` |

**路径**: 新增 API `routes/`→`services/`→`repositories/`；加表 `models/`+`migrations/`

## 关键函数签名

```typescript
// services/order.ts
class OrderService {
  async create(userId: number, items: CartItem[]): Promise<Order>
  async pay(orderId: number, method: PaymentMethod): Promise<Payment>
  async cancel(orderId: number, reason?: string): Promise<void>
}

// services/auth.ts
class AuthService {
  async login(email: string, password: string): Promise<{ token: string, user: User }>
  async register(data: RegisterDTO): Promise<User>
  async verifyToken(token: string): Promise<TokenPayload>
}

// services/payment.ts
async function handleCallback(provider: 'alipay' | 'wechat', payload: any): Promise<void>
```

## 核心工作流

**订单流程** `OrderService.create()`:
```
下单 → 校验库存 → 创建(pending) → 支付 → 扣库存 → 完成(paid)
                                  ↓ 超时30min
                               取消(cancelled)
```

**认证流程** `AuthService.login()`:
```
验证凭证 → 生成Token → 创建会话 → 返回
   ↓ 失败5次
  锁定账户
```

## 状态机

**Order.status**: `pending(0)` → `paid(1)` → `shipped(2)` → `completed(3)` | `cancelled(4)`
- 🔴 `completed/cancelled` 是终态，禁止变更
- 🟠 退款仅 `paid` 状态允许

**User.status**: `inactive(0)` → `active(1)` ⇄ `suspended(2)`

## 数据模型

| 表 | 唯一约束 | 关键外键 |
| -- | -------- | -------- |
| users | email, username | - |
| orders | order_no | user_id → users |
| order_items | - | order_id, product_id |
| products | sku | - |
| payments | transaction_id | order_id → orders |

**关系**: `users` 1→N `orders` 1→N `order_items` N←1 `products`

## 枚举速查

| 枚举 | 值 | 判断函数 |
| ---- | -- | -------- |
| OrderStatus | PENDING=0, PAID=1, SHIPPED=2, COMPLETED=3, CANCELLED=4 | `isFinal()` |
| PaymentMethod | ALIPAY=1, WECHAT=2, CREDIT_CARD=3 | - |
| UserStatus | INACTIVE=0, ACTIVE=1, SUSPENDED=2 | `canLogin()` |

## 外部服务

| 服务 | 路径 | 回调端点 |
| ---- | ---- | -------- |
| 支付宝 | `services/payment/alipay.ts` | `POST /api/callback/alipay` |
| 微信 | `services/payment/wechat.ts` | `POST /api/callback/wechat` |
| 短信 | `services/sms.ts` | - |
| OSS | `services/storage.ts` | - |
| Redis | `services/cache.ts` | - |

## 风险区域

| 级别 | 区域 | 规则 |
| ---- | ---- | ---- |
| 🔴 高 | `migrations/` | 只追加，禁止修改/删除已有文件 |
| 🔴 高 | `services/payment/` | 涉及资金，必须双人 Review |
| 🟠 中 | `middleware/auth.ts` | 认证核心，需完整测试 |
| 🟠 中 | `config/prod.ts` | 生产配置，需人工审核 |
| 🟡 低 | `services/*.ts` | 业务逻辑，注意状态机约束 |

## 常见陷阱

| 陷阱 | 正确做法 |
| ---- | -------- |
| ❌ 直接修改订单状态字段 | ✅ 调用 `order.transitionTo(status)` 校验转换 |
| ❌ 在 service 层写 SQL | ✅ 通过 repository 访问数据库 |
| ❌ 用 `console.log` 调试 | ✅ 用 `logger.info/error` |
| ❌ 硬编码状态值 `status = 1` | ✅ 用枚举 `OrderStatus.PAID` |
| ❌ 支付回调不验签 | ✅ 先调用 `verifySignature()` |
| ❌ 修改已有 migration 文件 | ✅ 新建 migration 文件追加变更 |

## 代码规范

- **命名**: 文件 `kebab-case` / 类 `PascalCase` / 函数 `camelCase`
- **错误**: 业务错误 `throw new BizError(code, msg)` / 系统错误直接 throw
- **日志**: 禁止 `console.log`，用 `logger.info/warn/error`

## 环境变量

```
DATABASE_URL, REDIS_URL, JWT_SECRET, ALIPAY_APP_ID, WECHAT_APP_ID
```

## 子文件加载

| 场景 | 加载 |
| -------- | -------- |
| 首次接触 / 完整架构 | `project-overview.md` |
| 功能模块 / 文件边界 | `context-boundaries.md` |
| 编码规范 / Code Review | `conventions.md` |
| 构建、测试、部署 | `task-recipes.md` |
| 修改 🔴🟠 风险区 | `danger-zones.md` |
| 重构 / 影响评估 | `impact-analysis.md` |
| 数据库 / SQL / 加表 | `database-schema.md` |
| 复杂流程 / 状态机 | `critical-flows.md` |
