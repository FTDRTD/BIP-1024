# 使用 Debian 稳定版的精简镜像作为基础
FROM debian:stable-slim

# 设置工作目录
WORKDIR /app

# 关键优化：将 APT 源更换为国内的清华大学镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 关键修正：安装更完整的 tcl-dev 包
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-tk \
    tk-dev \
    tcl-dev \
    patchelf \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 将项目文件复制到容器中
COPY . .

# 安装 Nuitka 和 ttkbootstrap
RUN pip3 install nuitka ttkbootstrap --break-system-packages

# Dockerfile 结束。我们将在容器运行时执行打包命令