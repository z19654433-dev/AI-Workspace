# 使用完整版 Python 镜像（slim 缺少编译 torch 等包的依赖）
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 先复制依赖文件
COPY requirements.txt .

# 安装依赖（使用清华镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
