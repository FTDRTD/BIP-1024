FROM python:3.12-slim

# 安装 Nuitka 打包必须的依赖 + Tkinter 支持
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        patchelf \
        gcc \
        g++ \
        make \
        tk \
        tcl \
        libtk8.6 \
        libtcl8.6 \
        python3-tk \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖 + Nuitka
RUN pip install --no-cache-dir -r requirements.txt nuitka

# 复制项目源码
COPY . .
