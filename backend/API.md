# 后端接口文档

## 通用说明

- Base URL: `/api`
- 返回格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

- 失败时 `code != 0`，`message` 为错误提示。

## 认证与用户

### 注册

- `POST /api/auth/register`
- Body:

```json
{
  "username": "demo",
  "password": "123456",
  "address": "深圳市南山区"
}
```

- Response:

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "username": "demo",
    "address": "深圳市南山区"
  }
}
```

### 登录

- `POST /api/auth/login`
- Body:

```json
{
  "username": "demo",
  "password": "123456"
}
```

- Response:

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "username": "demo",
    "address": "深圳市南山区"
  }
}
```

### 获取用户信息

- `GET /api/users/{user_id}`

## 药品

### 药品列表

- `GET /api/medicines`
- Query:
  - `keyword` (可选)

### 药品详情

- `GET /api/medicines/{medicine_id}`

## 购物车

### 获取购物车

- `GET /api/cart?user_id=1`

### 添加购物车

- `POST /api/cart`
- Body:

```json
{
  "user_id": 1,
  "medicine_id": 10,
  "quantity": 2
}
```

### 更新购物车项

- `PUT /api/cart/{item_id}`
- Body:

```json
{
  "quantity": 3,
  "selected": true
}
```

### 删除购物车项

- `DELETE /api/cart/{item_id}`

## 订单

### 创建订单

- `POST /api/orders`
- Body:

```json
{
  "user_id": 1,
  "address": "深圳市南山区"
}
```

### 订单列表

- `GET /api/orders?user_id=1`

### 订单详情

- `GET /api/orders/{order_id}`
