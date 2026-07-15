# 汇报顺序抽签小程序

一个简单易用的汇报顺序抽签应用，支持微信群分享、实时数据同步。

## 功能特点

- 🎲 **10人汇报顺序随机抽签**
- 📱 **移动端友好**，适合微信内打开
- 📊 **管理后台**实时查看抽签结果
- 🔄 **自动刷新**，数据实时同步
- 🚀 **Python Flask 后端**，数据可靠存储
- 💾 **SQLite 数据库**，无需额外配置

## 快速开始

### 方式一：本地运行

#### 1. 安装 Python 依赖

```bash
cd lottery-draw
pip install -r requirements.txt
```

#### 2. 启动服务器

```bash
python app.py
```

#### 3. 打开浏览器

访问：http://localhost:5000

---

### 方式二：部署到免费云平台

#### 选项 1：Render.com（推荐）

1. 访问 [Render.com](https://render.com) 并注册
2. 创建新的 **Web Service**
3. 连接你的 GitHub 仓库（或将代码上传到 GitHub）
4. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. 部署完成后获得稳定的 HTTPS 链接

#### 选项 2：Railway.app

1. 访问 [Railway.app](https://railway.app) 并注册
2. 创建新项目，选择 **Python**
3. 连接 GitHub 仓库
4. 自动检测并部署
5. 获得部署链接

#### 选项 3：Fly.io

```bash
# 安装 flyctl
# 然后在项目目录运行：
fly launch
fly deploy
```

---

## 使用说明

### 抽签流程

#### 1. 管理员启动抽签

1. 启动服务器后，打开首页
2. 系统自动生成抽签会话码
3. 点击"管理员后台"
4. 复制抽签链接分享到微信群

#### 2. 参与者抽签

1. 点击微信群中的链接
2. 输入姓名
3. 点击"抽取我的顺序"
4. 查看抽签结果

#### 3. 管理员监控

1. 在后台页面实时查看抽签结果
2. 数据每 5 秒自动刷新
3. 抽签完成后可导出结果

### 抽签规则

- 每人只能抽签一次
- 10 个位置随机分配
- 重复姓名会提示已抽签
- 抽满 10 人后自动结束

---

## 项目结构

```
lottery-draw/
├── app.py              # Flask 后端服务器
├── index.html          # 抽签页面（参与者使用）
├── admin.html          # 管理后台
├── requirements.txt    # Python 依赖
├── lottery.db          # SQLite 数据库（运行后自动生成）
└── README.md           # 说明文档
```

---

## API 接口

### 获取/创建会话
```
GET /api/session?session={session_id}
```

### 执行抽签
```
POST /api/draw
Content-Type: application/json

{
  "session_id": "会话ID",
  "name": "姓名"
}
```

### 获取参与者列表
```
GET /api/participants?session={session_id}
```

### 重置会话
```
POST /api/reset
Content-Type: application/json

{
  "session_id": "会话ID"
}
```

---

## 常见问题

### Q: 数据存储在哪里？

A: 使用 SQLite 数据库文件 `lottery.db`，数据存储在服务器端。

### Q: 可以同时有多个抽签会话吗？

A: 可以！每个链接都有独立的会话 ID，互不干扰。

### Q: 如何修改抽签人数？

A: 在 `app.py` 中修改 `total_slots` 参数，默认为 10。

### Q: 部署到云平台后数据库会丢失吗？

A: 大多数云平台重启后文件会重置。建议：
1. 使用环境变量配置外部数据库（如 PostgreSQL）
2. 或使用支持持久化存储的平台

---

## 技术栈

- **后端**: Python Flask
- **数据库**: SQLite
- **前端**: HTML + CSS + JavaScript
- **部署**: 可部署到任何支持 Python 的平台

---

## 许可

MIT License - 自由使用和修改
