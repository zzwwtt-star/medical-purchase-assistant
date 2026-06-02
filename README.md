# 基于 AI 的医疗购药助手

毕业设计项目 —— 一个集成 AI 语音交互的在线购药平台，包含用户端、商家管理端和 Python 后端服务。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask + SQLAlchemy + PyMySQL + Socket.IO + eventlet |
| 用户端 | Vue 3 + Vite + Vue Router + Socket.IO Client |
| 商家端 | Vue 3 + Vite + Vue Router + Chart.js |
| AI | Ollama + Qwen2.5:3b + faster-whisper + edge-tts |
| 数据库 | MySQL 8.0+ |

## 功能

### 用户端
- 注册 / 登录
- 药品浏览、搜索、分类筛选
- 购物车管理（添加、修改数量、选择结算）
- 下单结算
- 订单查看
- 修改密码 / 修改收货地址
- AI 语音购药助手（实时 WebSocket 语音对话）
- AI 文本对话（SSE 流式响应）

### 商家端
- 登录 / 注册
- 药品管理（上架 / 编辑 / 下架）
- 订单管理
- 数据概览仪表盘（Chart.js 图表）

### 后端

- RESTful API（用户、药品、购物车、订单）
- WebSocket 语音对话管线：VAD 检测 → Whisper 转写 → Qwen 生成回复 → edge-tts 合成语音 → 流式推送
- SSE 流式 AI 文本对话
- CSV 药品数据导入 (`medicine.csv`)

## 快速开始

### 1. 环境准备

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- [Ollama](https://ollama.com/)（需拉取 Qwen2.5:3b 模型）

```bash
# 安装并启动 Ollama，然后拉取模型
ollama pull qwen2.5:3b
```

### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的数据库密码等信息

# 初始化数据库（可选两种方式）
python init_db_minimal.py          # 基础建表
# 或
python init_db.py                  # 建表 + 导入 medicine.csv 药品数据

# 启动服务（端口 5000）
python app.py
```

### 3. 用户端

```bash
cd frontend
npm install
npm run dev
```

默认运行在 `http://localhost:5173`。

### 4. 商家端

```bash
cd merchant-frontend
npm install
npm run dev
```

默认运行在 `http://localhost:5174`。

## 环境变量

在 `backend/.env` 中配置：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<your-password>
DB_NAME=graduation_design
DB_AUTH_PLUGIN=caching_sha2_password
```

## 项目结构

```
├── backend/                  # Flask 后端
│   ├── app.py                # 应用入口 + Flask-SocketIO 启动
│   ├── routes.py             # RESTful API 路由（auth / medicines / cart / orders）
│   ├── models.py             # SQLAlchemy 数据模型
│   ├── config.py             # 环境变量与数据库连接配置
│   ├── voice_pipeline.py     # 语音处理管线（Whisper + Qwen + edge-tts）
│   ├── voice_events.py       # WebSocket 语音事件注册
│   ├── utils.py              # 工具函数（统一响应格式）
│   ├── init_db.py            # 数据库初始化 + CSV 药品数据导入
│   ├── init_db_minimal.py    # 仅建表（不含数据导入）
│   ├── API.md                # API 接口文档
│   ├── requirements.txt      # Python 依赖
│   └── .env.example          # 环境变量模板
│
├── frontend/                 # 用户端（Vue 3）
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── login/        # 登录
│   │   │   ├── register/     # 注册
│   │   │   ├── home/         # 首页
│   │   │   ├── medicine/     # 药品列表 / 详情
│   │   │   ├── cart/         # 购物车
│   │   │   ├── order/        # 订单 / 结算
│   │   │   ├── user/         # 个人中心 / 修改密码
│   │   │   └── voice/        # AI 语音助手
│   │   ├── composables/      # 组合式函数
│   │   │   ├── useVoiceSocket.js  # WebSocket 连接
│   │   │   ├── useVAD.js          # VAD 语音活动检测
│   │   │   ├── useMicCapture.js   # 麦克风采集
│   │   │   └── useAudioQueue.js   # 音频播放队列
│   │   ├── router/           # 路由配置
│   │   └── api/              # HTTP API 封装
│   └── package.json
│
├── merchant-frontend/        # 商家管理端（Vue 3）
│   ├── src/
│   │   ├── views/
│   │   │   ├── login/        # 登录
│   │   │   ├── register/     # 注册
│   │   │   ├── dashboard/    # 数据概览
│   │   │   ├── products/     # 药品管理 / 详情
│   │   │   └── orders/       # 订单管理
│   │   ├── components/       # 公共组件（Header / Sidebar）
│   │   ├── router/           # 路由配置
│   │   └── api/              # HTTP API 封装
│   └── package.json
│
├── medicine.csv              # 药品示例数据
└── .gitignore
```

## API 接口

详见 [backend/API.md](backend/API.md)。

简要概览：

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/register` | 用户注册 |
| 认证 | `POST /api/auth/login` | 用户登录 |
| 用户 | `GET /api/users/<id>` | 获取用户信息 |
| 药品 | `GET /api/medicines` | 药品列表（支持 keyword 搜索） |
| 药品 | `GET /api/medicines/<id>` | 药品详情 |
| 购物车 | `GET/POST /api/cart` | 查看 / 添加购物车 |
| 购物车 | `PUT/DELETE /api/cart/<id>` | 更新 / 删除购物车项 |
| 订单 | `POST /api/orders` | 创建订单 |
| 订单 | `GET /api/orders?user_id=<id>` | 订单列表 |
| 订单 | `GET /api/orders/<id>` | 订单详情 |
