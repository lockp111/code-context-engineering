# 代码约定

> 仅当需要详细规范或 Code Review 时加载此文件

## 命名规范

| 类型 | 规范 | 示例 |
| ---- | ---- | ---- |
| 文件 | kebab-case | `user-profile.tsx` |
| 组件/类 | PascalCase | `UserProfile` |
| 函数/变量 | camelCase | `getUserById` |
| 常量 | UPPER_SNAKE | `MAX_RETRY` |
| 数据库表 | snake_case | `user_orders` |
| API 路径 | kebab-case | `/api/user-profile` |

## 错误码体系

| 范围 | 类型 | 示例 |
| ---- | ---- | ---- |
| 1000-1999 | 通用错误 | 1001 参数错误, 1002 未找到 |
| 2000-2999 | 认证授权 | 2001 未登录, 2002 无权限, 2003 Token过期 |
| 3000-3999 | 业务错误 | 3001 库存不足, 3002 订单已取消 |
| 4000-4999 | 第三方服务 | 4001 支付失败, 4002 短信发送失败 |

**错误抛出**: `throw new BizError(code, message, data?)`

**错误响应**: `{ code: 3001, message: "库存不足", data: { stock: 0 } }`

## API 设计

| 操作 | 方法 | 路径模式 |
| ---- | ---- | -------- |
| 列表 | GET | `/resources` |
| 详情 | GET | `/resources/:id` |
| 创建 | POST | `/resources` |
| 更新 | PUT | `/resources/:id` |
| 删除 | DELETE | `/resources/:id` |
| 操作 | POST | `/resources/:id/action` |

**命名**: 请求体 `XxxRequest/DTO`，响应体 `XxxResponse/VO`

## 日志规范

| 级别 | 用途 | 示例 |
| ---- | ---- | ---- |
| error | 需立即处理 | 支付失败、数据库连接失败 |
| warn | 潜在问题 | 重试、降级 |
| info | 关键节点 | 登录、支付、状态变更 |
| debug | 调试用 | 生产环境关闭 |

**禁止**: `console.log`、打印完整对象、日志含敏感信息

## 代码风格

| 项目 | 规范 |
| ---- | ---- |
| 缩进 | 2 空格 |
| 引号 | 单引号 |
| 分号 | 不使用 |
| 行宽 | 100 |
| 尾逗号 | 多行时使用 |

## 提交规范

**格式**: `type(scope): description`

| 类型 | 说明 | 示例 |
| ---- | ---- | ---- |
| feat | 新功能 | `feat(order): add cancel api` |
| fix | 修复 | `fix(auth): token expiry check` |
| refactor | 重构 | `refactor(utils): extract helper` |
| perf | 性能 | `perf(query): add index` |
| docs | 文档 | `docs: update readme` |
| test | 测试 | `test(order): add cancel test` |
