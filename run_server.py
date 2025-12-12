import os
import sys

from flask import send_from_directory, request

# === 确保能导入 backend.app ===
BASE_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app import app  # 这里会创建 Flask app，并注册原本所有路由

# 前端打包后的目录
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")


def frontend_index():
    """
    覆盖原来的 index 视图：根路径直接返回前端构建好的 index.html
    """
    index_file = os.path.join(DIST_DIR, "index.html")
    if not os.path.isfile(index_file):
        # 构建失败或路径不对时，返回简单错误方便排查
        return {
            "error": "frontend dist not found",
            "dist_dir": DIST_DIR,
        }, 500

    return send_from_directory(DIST_DIR, "index.html")


# 用前端入口覆盖 backend.app 里原来的 index 视图函数
# backend/app.py 里原来有：
#   @app.route('/')
#   def index(): ...
# endpoint 名叫 "index"，这里直接换成我们的
app.view_functions["index"] = frontend_index


@app.errorhandler(404)
def spa_fallback(error):
    """
    SPA / 静态资源兜底：
    - 对于 /api、/health、/files 开头的路径，保留原始 404 行为
    - 其它路径：
        1. 如果 dist 目录下有同名文件，返回该静态文件
        2. 否则一律回退到 index.html（前端路由交给 React）
    """
    # 原始请求路径，如 "/assets/main-xxxx.js"
    req_path = request.path.lstrip("/")  # 去掉开头的 "/"

    # 保留后端 API 的 404 行为
    if req_path.startswith(("api", "health", "files")):
        return error

    # 尝试以 "静态文件" 的方式处理
    candidate_path = os.path.join(DIST_DIR, req_path)
    if os.path.exists(candidate_path) and os.path.isfile(candidate_path):
        directory, filename = os.path.split(candidate_path)
        return send_from_directory(directory, filename)

    # 否则，作为前端路由，回退到 index.html
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_file):
        return send_from_directory(DIST_DIR, "index.html")

    # 如果连 index.html 都没了，那就老老实实返回原始 404
    return error


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
