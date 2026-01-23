---
description: Code Context Index
alwaysApply: true
---
# {project_name} 上下文索引

## AI 行为指南

| 任务类型 | 行为 |
| -------- | ---- |
| 新增功能 | 先查「关键路径」定位文件 → 遵循「代码规范」→ 检查「常见陷阱」 |
| 修改现有代码 | 先查「风险区域」→ 确认状态机/枚举约束 → 评估影响范围 |
| 修 Bug | 定位相关服务 → 检查状态转换是否合法 → 查看关联表约束 |
| 数据库变更 | 🔴 只能追加 migration，禁止改已有文件 → 更新 `database-schema.md` |

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

**操作路径**:
- 新增 API: `routes/` → `services/` → `repositories/`
- 添加表: `models/` + `migrations/`

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

## 子文件加载指南

| 触发场景 | 加载文件 |
| -------- | -------- |
| 首次接触项目 / 需要完整架构图 | `project-overview.md` |
| 开发特定功能模块 / 不确定文件边界 | `context-boundaries.md` |
| 需要详细编码规范 / Code Review | `conventions.md` |
| 执行构建、测试、部署命令 | `task-recipes.md` |
| 修改 🔴🟠 风险区域前 | `danger-zones.md` |
| 重构 / 评估改动影响范围 | `impact-analysis.md` |
| 数据库开发 / 写 SQL / 加表 | `database-schema.md` |
| 理解复杂业务流程 / 状态机细节 | `critical-flows.md` |
