# 基于 AI 的医疗购药助手

毕业设计项目 —— 一个集成 AI 语音交互的在线购药平台，包含用户端、商家管理端和 Python 后端服务。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask + SQLAlchemy + MySQL + Socket.IO |
| 用户端 | Vue 3 + Vite + Vue Router |
| 商家端 | Vue 3 + Vite |
| AI | Ollama + Qwen2.5:3b + Whisper 语音识别 + edge-tts 语音合成 |

## 功能

### 用户端
- 注册 / 登录
- 药品浏览、搜索、分类筛选
- 购物车管理
- 下单结算
- 订单查看
- AI 语音购药助手（实时 WebSocket 语音对话）

### 商家端
- 登录 / 注册
- 药品管理（上架 / 编辑 / 下架）
- 订单管理
- 数据概览

### 后端
- RESTful API
- WebSocket 语音对话（VAD 检测 → Whisper 转写 → Qwen 生成回复 → edge-tts 合成语音）
- SSE 流式 AI 文本对话

## 快速开始

### 1. 环境准备

- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env，填入实际值）
cp .env.example .env

# 初始化数据库
python init_db.py

# 启动服务
python app.py
```

### 3. 用户端

```bash
cd frontend
npm install
npm run dev
```

### 4. 商家端

```bash
cd merchant-frontend
npm install
npm run dev
```

## 环境变量

在 `backend/.env` 中配置：

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<your-password>
DB_NAME=graduation_design
```

## 项目结构

```
├── backend/             # Flask 后端
│   ├── app.py           # 应用入口
│   ├── routes.py        # API 路由
│   ├── models.py        # 数据模型
│   ├── voice_pipeline.py # 语音处理管线
│   ├── voice_events.py   # WebSocket 语音事件
│   └── config.py         # 配置
├── frontend/            # 用户端（Vue 3）
│   └── src/
│       ├── views/       # 页面组件
│       ├── composables/ # 组合式函数（语音 VAD、Socket 等）
│       ├── router/      # 路由配置
│       └── api/         # API 封装
└── merchant-frontend/   # 商家管理端（Vue 3）
```
