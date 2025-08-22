FROM python:3.12-slim

# 安装 Nuitka 打包必须依赖 + Tkinter
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        patchelf gcc g++ make tk tcl libtk8.6 libtcl8.6 python3-tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt nuitka ttkbootstrap

COPY . .
