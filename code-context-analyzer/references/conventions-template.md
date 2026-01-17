# 代码约定模板

项目遵循的编码规范，确保风格一致。

---

## 命名规范

| 类型 | 规范        | 示例               |
| ---- | ----------- | ------------------ |
| 组件 | PascalCase  | `UserProfile`      |
| 函数 | camelCase   | `getUserById`      |
| 常量 | UPPER_SNAKE | `MAX_RETRY`        |
| 文件 | kebab-case  | `user-profile.tsx` |

---

## 编码模式

- **错误处理**: [项目的错误处理方式]
- **日志**: [日志规范，如禁止 console.log]
- **异步**: [async/await 或其他模式]
- **状态管理**: [Redux / Zustand / Context 等]

---

## 测试要求

- [测试文件命名约定]
- [覆盖率要求]
- [必须测试的场景]

---

## 代码风格

- **缩进**: [2空格 / 4空格 / Tab]
- **引号**: [单引号 / 双引号]
- **分号**: [使用 / 不使用]
- **行宽**: [80 / 100 / 120]

---

## 提交规范

- **格式**: `type(scope): description`
- **类型**: feat, fix, docs, refactor, test, chore
- **示例**: `feat(auth): add login api`
