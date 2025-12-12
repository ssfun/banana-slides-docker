########################
# 构建阶段：clone + 构建前后端
########################
FROM python:3.10-slim AS builder

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    git nodejs npm build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN git clone https://github.com/Anionex/banana-slides.git ./

# 后端依赖
RUN uv sync --frozen || uv sync

# 前端依赖 + 打包
WORKDIR /src/frontend
RUN npm ci || npm install
RUN npm run build



########################
# 运行阶段：轻量化镜像
########################
FROM python:3.10-slim AS runtime

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH="/app:/app/backend"

WORKDIR /app

# 运行期依赖精简即可
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 从 builder 拷贝：后端代码 / 虚拟环境 / 前端 dist / run_server.py
COPY --from=builder /src/backend ./backend
COPY --from=builder /src/.venv ./.venv
COPY --from=builder /src/frontend/dist ./frontend/dist
COPY run_server.py ./run_server.py

EXPOSE 5000

CMD ["python", "run_server.py"]
