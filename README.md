# 遥感图像超分系统（Real-ESRGAN 3.0）

一个可直接运行的前后端项目：
- 前端：精美暗色科技风页面，支持上传、参数配置、结果预览与下载。
- 后端：FastAPI 接口，调用 Real-ESRGAN（`RealESRGAN_x4plus`）完成超分。

## 1. 环境要求

- Python 3.10+
- Linux/macOS（Windows 也可用，命令自行替换）
- 建议：有 NVIDIA GPU（无 GPU 也能跑，但会慢）

## 2. 一键运行

```bash
./run.sh
```

启动后访问：

- `http://127.0.0.1:8000`

> 首次运行会自动下载模型权重到 `weights/RealESRGAN_x4plus.pth`。

## 3. 手动运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. 功能说明

- 支持图片格式：`png/jpg/jpeg/tif/tiff/webp`
- 放大倍率：`x2/x3/x4`
- 分块处理：可选 `tile` 参数（大图防显存爆）
- 结果保存：
  - 上传图在 `uploads/`
  - 超分图在 `outputs/`

## 5. API

### 健康检查

`GET /api/health`

### 超分接口

`POST /api/super-resolve`

表单参数：
- `file`: 图像文件
- `scale`: 2/3/4
- `tile`: 可选，默认 0

返回示例：

```json
{
  "job_id": "...",
  "input_url": "/api/files/xxx.png",
  "output_url": "/api/files/xxx_x4.png",
  "download_url": "/api/download/xxx_x4.png"
}
```
