# 使用一个稳定且轻量的 Python 官方镜像
FROM python:3.12-slim

# 安装 Nuitka 和 PySide6 (Qt6) 运行所需的系统级依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    patchelf \
    # 修复您日志中直接报错的库 (GLib)
    libglib2.0-0 \
    # OpenGL 相关的库 (这是被修正的行)
    libgl1 \
    # X11/XCB 窗口系统相关的核心库
    libx11-xcb1 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-cursor0 \
    # 字体和字体配置相关的库
    libfontconfig1 \
    libfreetype6 \
    # D-Bus 消息总线系统
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# 在容器内设置一个工作目录
WORKDIR /app

# 复制依赖描述文件，并安装 Python 包以利用 Docker 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt nuitka

# GitHub Actions 将会通过 volume 挂载源代码到 /app 目录