# 上下文边界模板

处理不同功能时的关注范围，避免加载无关代码。

---

## 用户相关功能

```
关注: src/features/user/, src/services/user.ts
忽略: src/features/admin/, src/features/billing/
```

---

## API 开发

```
关注: src/routes/, src/services/, src/middleware/
忽略: src/components/, src/pages/, src/styles/
```

---

## UI 组件开发

```
关注: src/components/, src/styles/, src/hooks/
忽略: src/services/, src/routes/, src/migrations/
```

---

## 数据库相关

```
关注: src/models/, src/repositories/, migrations/
忽略: src/components/, src/routes/, src/styles/
```

---

## 测试相关

```
关注: tests/, src/test-utils/, jest.config.js
忽略: src/styles/, docs/
```

---

## 配置和部署

```
关注: config/, scripts/, Dockerfile, docker-compose.yml
忽略: src/components/, tests/
```
