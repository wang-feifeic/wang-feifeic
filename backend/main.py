from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.service import RealEsrganService

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="遥感图像超分系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = RealEsrganService(output_dir=OUTPUT_DIR)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": service.model_name}


@app.post("/api/super-resolve")
async def super_resolve(
    file: UploadFile = File(...),
    scale: int = Form(4),
    tile: Optional[int] = Form(0),
) -> dict[str, str]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}:
        raise HTTPException(status_code=400, detail="仅支持常见图像格式")

    job_id = uuid.uuid4().hex
    input_path = UPLOAD_DIR / f"{job_id}{suffix}"
    output_path = OUTPUT_DIR / f"{job_id}_x{scale}.png"

    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        service.run(input_path=input_path, output_path=output_path, scale=scale, tile=tile or 0)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"超分失败: {exc}") from exc

    return {
        "job_id": job_id,
        "input_url": f"/api/files/{input_path.name}",
        "output_url": f"/api/files/{output_path.name}",
        "download_url": f"/api/download/{output_path.name}",
    }


@app.get("/api/files/{filename}")
def get_file(filename: str) -> FileResponse:
    for folder in (UPLOAD_DIR, OUTPUT_DIR):
        candidate = folder / filename
        if candidate.exists():
            return FileResponse(candidate)
    raise HTTPException(status_code=404, detail="文件不存在")


@app.get("/api/download/{filename}")
def download(filename: str) -> FileResponse:
    candidate = OUTPUT_DIR / filename
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(candidate, filename=filename)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
