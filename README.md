# Banana Slides 🍌

一个简洁、现代、可本地运行的 AI 幻灯片生成工具。
后端基于 **Flask + SQLAlchemy + SQLite**，前端基于 **Vite + React**。

---

## ✨ 功能特性

* 使用自然语言生成 AI 幻灯片
* 支持多种大模型（OpenAI、Google 等）
* 在线可编辑的幻灯片编辑器
* 本地运行无需外部数据库（SQLite）
* 支持文件上传（图片、PDF）
* 支持 Docker 一键部署（All-in-One）

---

# 🐳 使用 Docker 一键部署（推荐）

本仓库提供 **all-in-one Docker 方式**，无需前后端分容器，也无需 nginx：

* 自动 git clone 项目
* 构建前端（Vite → dist）
* 构建后端虚拟环境
* 运行阶段镜像极简，仅包含 Flask + dist 静态文件
* 通过 Flask 单进程同时服务 **API + 前端静态资源**

---

## 1️⃣ 构建镜像

```bash
docker build -t banana-slides-all-in-one .
```

---

## 2️⃣ 数据持久化

应用会产生两类数据：

| 容器路径                    | 描述                     | 是否必须  |
| ----------------------- | ---------------------- | ----- |
| `/app/backend/instance` | SQLite 数据库（所有项目/页面/内容） | ✅ 必须  |
| `/app/uploads`          | 用户上传文件                 | ⚠️ 建议 |

在宿主机创建对应目录：

```bash
mkdir -p ./data/instance
mkdir -p ./data/uploads
```

---

## 3️⃣ 运行容器

```bash
docker run -d \
  --name banana-slides \
  --env-file .env \
  -p 5000:5000 \
  -v $(pwd)/data/instance:/app/backend/instance \
  -v $(pwd)/data/uploads:/app/uploads \
  banana-slides-all-in-one
```

访问：

```
http://localhost:5000
```

---

# 💾 数据持久化说明

| 类型   | 路径                                       | 说明         |
| ---- | ---------------------------------------- | ---------- |
| 数据库  | `/app/backend/instance/banana_slides.db` | 所有业务数据     |
| 上传文件 | `/app/uploads`                           | 图片、PDF 等资源 |

---

# ⚙ 环境变量 (.env)

复制默认配置：

```bash
cp .env.example .env
```

关键变量：

| 变量名                | 说明                         |
| ------------------ | -------------------------- |
| `AI_PROVIDER`      | openai / google |
| `OPENAI_API_KEY`   | OpenAI API 密钥              |
| `GOOGLE_API_KEY`   | Google Gemini 密钥           |
| `PORT`             | 服务端口（默认 5000）              |

---

# 🧱 项目结构（构建后）

```
backend/
  app.py
  models.py
  services/
  instance/          ← SQLite 数据库
frontend/
  dist/              ← 构建后的前端文件
uploads/             ← 上传文件
run_server.py        ← 生产环境入口（Flask 负责前端 + 后端）
Dockerfile           ← All-in-One 构建脚本
```

---

# 🛠 开发模式

### 后端

```bash
cd backend
uv sync
uv run python app.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

---

# 🔧 与原项目的差异（本仓库增强内容）

本仓库基于原项目 **[Anionex/banana-slides](https://github.com/Anionex/banana-slides)** 进行了大量工程化优化，以便更方便部署到本地/服务器生产环境。

以下是相较于原项目的主要变化：

## ✅ 1. 全自动 All-in-One Docker 构建

原项目需要：

* 手动 clone
* 前端 / 后端分别安装依赖
* 手动运行前端 dev server 或构建 dist
* 或通过 docker-compose 方式启动两个容器

本仓库实现：

* **单个 Dockerfile 完成 clone + build（前端 + 后端）+ runtime**
* **运行阶段只需一个容器（Flask）**
* 无需 node、git、npm、nginx 等运行时依赖
* 镜像体积更小、部署更快，更适合生产环境

---

## ✅ 2. 前端由 Flask 直接托管（无 nginx）

原项目默认用 Vite Dev Server 或 nginx 分发静态资源。
本仓库实现：

* 构建出的 `frontend/dist` 文件由 Flask 直接托管
* 覆盖根路由 `/`，自动返回前端 index.html
* 自动处理 `/assets/...` 静态资源
* 404 fallback 支持 SPA 路由
* API 路由模式完全保留

更适合简单部署场景（K3S、Docker、NAS 等）。

---

## ✅ 3. 自动 SPA fallback & 静态资源修复

原前端构建的静态资源路径需要额外配置。
本仓库提供：

* 自动检测 dist 内文件
* 后端自动 fallback → `index.html`，确保 SPA 正常路由
* 自动映射 `/assets/...` 静态资源
* 规避大量 404

---

## ✅ 4. 可选的数据持久化设计（生产可用）

原项目未提供明确的持久化路径说明。

本仓库：

* 明确标注需要持久化的路径（数据库 & uploads）
* README 中包含可复制的 Docker Volume 示例
* 消除了容器重建导致数据丢失的问题

---

## ✅ 5. 清晰的生产入口 `run_server.py`

新增的 `run_server.py` 提供：

* 服务前端静态资源
* 替换 `/` 原路由
* SPA fallback
* 保留原 API 路由
* 单入口运行生产服务

---

## ✅ 6. README 与部署文档全面升级

本 README 完整包含：

* 部署指南
* 运行指南
* 数据持久化
* 与原项目差异
* 鸣谢说明

非常适合实际部署、二次开发或教学使用。

---

# 🙏 鸣谢（原作者）

本项目基于原项目 **[Anionex/banana-slides](https://github.com/Anionex/banana-slides)** 进行优化与扩展。

特别感谢原作者及其贡献者提供：

* 项目的核心功能逻辑
* 前端编辑器
* 后端 AI 调用框架
* 数据结构与设计理念

本仓库在此基础上做了工程化增强，全部遵循原项目的许可证（MIT License）。
