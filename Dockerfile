# 1. 使用一个轻量的官方 Python 镜像作为基础环境
FROM python:3.12-slim

# 2. 在容器内部创建一个工作目录
WORKDIR /app

# 3. 将依赖文件复制到容器中
COPY requirements.txt .

# 4. 安装所有 Python 依赖
# 使用 --no-cache-dir 可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 5. 将你项目中的所有文件复制到容器的工作目录中
COPY . .

# 注意：因为我们只是把这个 Docker 镜像当作一个“构建环境”来使用，
# 而不是要直接运行一个服务，所以我们不需要设置 CMD 或 ENTRYPOINT。