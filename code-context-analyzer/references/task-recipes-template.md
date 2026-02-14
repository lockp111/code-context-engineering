# 任务配方

> 执行构建、测试、部署时加载

## 常用命令

| 命令 | 用途 |
| ---- | ---- |
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run test` | 运行所有测试 |
| `npm run test:watch` | 监听模式测试 |
| `npm run lint` | 代码检查 |
| `npm run db:migrate` | 执行数据库迁移 |
| `npm run db:seed` | 填充测试数据 |
| `npm run deploy:staging` | 部署到预发布 |

## 环境配置

| 环境 | 配置文件 | 特点 |
| ---- | -------- | ---- |
| local | `.env.local` | 本地开发，mock 服务 |
| dev | `.env.dev` | 联调环境 |
| staging | `.env.staging` | 预发布，生产数据副本 |
| prod | `.env.prod` | 🔴 生产环境 |

**切换**: `NODE_ENV=staging npm run build`

## 任务流程

### 添加新 API

```
routes/{resource}.ts      → 路由定义
services/{resource}.ts    → 业务逻辑
repositories/{resource}.ts → 数据访问
types/{resource}.ts       → 类型定义
tests/api/{resource}.test.ts → 测试
```

### 添加新表

```
1. npm run db:migration:create -- add_xxx_table
2. 编写 DDL（🔴 只能追加，禁止改已有 migration）
3. npm run db:migrate
4. 创建 model + repository
5. 更新 database-schema.md
```

### 修复 Bug

```
1. 复现 → 编写失败测试
2. 定位 → 查日志/调试
3. 修复 → 最小改动
4. 验证 → 测试通过
5. 检查 → 影响范围（查 impact-analysis.md）
```

## 测试策略

| 层级 | 覆盖目标 | 命令 |
| ---- | -------- | ---- |
| 单元 | 工具函数、纯逻辑 | `npm run test:unit` |
| 集成 | API、数据库交互 | `npm run test:integration` |
| E2E | 关键用户流程 | `npm run test:e2e` |

**必测**: 核心流程、边界、错误处理、权限

## 部署流程

```
本地测试 → PR → Review → 合并 main → 自动部署 staging → 验证 → 手动触发 prod
```

**回滚**: `npm run deploy:rollback -- v1.2.3`

## 重构检查

```
1. 确保有测试覆盖（无测试先补）
2. 小步修改，频繁提交
3. 每步运行测试
4. 更新相关文档
```
