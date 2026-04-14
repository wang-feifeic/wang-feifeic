from __future__ import annotations

from pathlib import Path

import cv2
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer


class RealEsrganService:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.model_name = "RealESRGAN_x4plus"
        self.model_dir = output_dir.parent / "weights"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / f"{self.model_name}.pth"
        self._prepare_weights()

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)

        self.upsampler = RealESRGANer(
            scale=4,
            model_path=str(self.model_path),
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=torch.cuda.is_available(),
        )

    def _prepare_weights(self) -> None:
        if self.model_path.exists():
            return
        load_file_from_url(
            url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
            model_dir=str(self.model_dir),
            file_name=self.model_path.name,
        )

    def run(self, input_path: Path, output_path: Path, scale: int = 4, tile: int = 0) -> None:
        if scale not in {2, 3, 4}:
            raise ValueError("scale 仅支持 2/3/4")

        img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("图像读取失败")

        self.upsampler.tile = tile
        output, _ = self.upsampler.enhance(img, outscale=scale)
        ok = cv2.imwrite(str(output_path), output)
        if not ok:
            raise RuntimeError("输出图像保存失败")
