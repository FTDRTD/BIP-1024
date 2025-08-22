# 1. 使用轻量 Python 官方镜像
FROM python:3.12-slim

# 2. 安装 Nuitka 打包 Linux 所需依赖（必须要有 patchelf）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        patchelf \
        gcc \
        g++ \
        make \
        && rm -rf /var/lib/apt/lists/*

# 3. 创建工作目录
WORKDIR /app

# 4. 先复制依赖文件
COPY requirements.txt .

# 5. 安装 Python 依赖 + Nuitka
RUN pip install --no-cache-dir -r requirements.txt nuitka

# 6. 复制项目源码
COPY . .

# ⚠️ 注意：
# 这个镜像只是作为 GitHub Actions 里的“构建容器”，
# 不设置 CMD/ENTRYPOINT（由 workflow 里的 docker run 决定要执行的命令）
