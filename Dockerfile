# 步骤 1: 使用一个稳定且轻量的 Python 官方镜像
FROM python:3.12-slim

# 步骤 2: 安装 PySide6 (Qt6) 运行所需的系统级依赖
# 这包括 C++ 编译器、OpenGL 库、XCB (X11) 相关库等
# patchelf 是 Nuitka 在 Linux 下经常使用的一个工具，用于修改可执行文件的依赖路径
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    patchelf \
    libgl1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# 步骤 3: 在容器内设置一个工作目录
WORKDIR /app

# 步骤 4: 仅复制依赖描述文件，并安装 Python 包
# 这样做可以充分利用 Docker 的层缓存机制。只要 requirements.txt 不变，
# 这一层就不需要重新构建，可以加快后续的构建速度。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt nuitka

# 注意：我们在这里没有使用 `COPY . .`
# 因为在 GitHub Actions 工作流中，我们会通过挂载卷的方式，
# 将最新的代码动态地映射到容器的 /app 目录中进行编译。
# 这样做更灵活，也让这个 Docker 镜像可以被重复用于不同版本的代码编译。