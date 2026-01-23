# 数据库结构

> 仅当数据库开发、写 SQL、加表时加载此文件

## 概览

| 数据库 | 表数量 | 迁移目录 |
| ------ | ------ | -------- |
| MySQL 8.0 | 5 | `migrations/` |

## 表结构

### users
```sql
CREATE TABLE users (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    username    VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名，登录用',
    email       VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱，找回密码用',
    password    VARCHAR(255) NOT NULL COMMENT 'bcrypt 哈希',
    status      TINYINT DEFAULT 1 COMMENT '状态: 0=禁用 1=正常 2=封禁',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status)
) COMMENT '用户表';
```

### orders
```sql
CREATE TABLE orders (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no    VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号: yyyyMMddHHmmss+6位随机',
    user_id     BIGINT NOT NULL COMMENT '下单用户',
    total       DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    status      TINYINT DEFAULT 0 COMMENT '状态: 0=待支付 1=已支付 2=已发货 3=已完成 4=已取消',
    paid_at     DATETIME COMMENT '支付时间',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) COMMENT '订单表';
```

### order_items
```sql
CREATE TABLE order_items (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id    BIGINT NOT NULL,
    product_id  BIGINT NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,
    price       DECIMAL(10,2) NOT NULL COMMENT '下单时单价（快照）',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order_id (order_id)
) COMMENT '订单明细';
```

### products
```sql
CREATE TABLE products (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku         VARCHAR(50) NOT NULL UNIQUE COMMENT '商品编码',
    name        VARCHAR(200) NOT NULL,
    price       DECIMAL(10,2) NOT NULL COMMENT '当前售价',
    stock       INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    status      TINYINT DEFAULT 1 COMMENT '状态: 0=下架 1=上架',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '商品表';
```

### payments
```sql
CREATE TABLE payments (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id        BIGINT NOT NULL,
    transaction_id  VARCHAR(64) UNIQUE COMMENT '第三方交易号',
    method          TINYINT NOT NULL COMMENT '支付方式: 1=支付宝 2=微信 3=信用卡',
    amount          DECIMAL(10,2) NOT NULL,
    status          TINYINT DEFAULT 0 COMMENT '状态: 0=待支付 1=成功 2=失败 3=已退款',
    paid_at         DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_order_id (order_id),
    INDEX idx_transaction_id (transaction_id)
) COMMENT '支付记录';
```

## 表关系

```
users (1) ──< (N) orders ──< (N) order_items >── (1) products
                   │
                   └──< (N) payments
```

## 枚举值速查

| 表.字段 | 值 | 含义 | 备注 |
| ------- | -- | ---- | ---- |
| users.status | 0/1/2 | 禁用/正常/封禁 | 0,2 不可登录 |
| orders.status | 0/1/2/3/4 | 待支付/已支付/已发货/已完成/已取消 | 3,4 是终态 |
| payments.method | 1/2/3 | 支付宝/微信/信用卡 | - |
| payments.status | 0/1/2/3 | 待支付/成功/失败/已退款 | - |

## 迁移历史

| 版本 | 文件 | 变更 |
| ---- | ---- | ---- |
| v1 | 001_init.sql | 初始化 users, products |
| v2 | 002_orders.sql | 新增 orders, order_items, payments |
| v3 | 003_index.sql | 添加查询优化索引 |
