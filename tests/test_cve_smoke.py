# ---------------------------------------------------------------------
# Copyright (c) 2025 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
"""
Smoke tests verifying upgraded dependencies import and function correctly
after CVE remediation.

Upgraded packages:
  - Pillow 11.3.0 -> 12.1.1 (CVE-2026-25990)
  - wheel  0.45.1 -> 0.46.2 (CVE-2026-24049)
"""
import importlib
import sys

import pytest


# ── Pillow (CVE-2026-25990) ──────────────────────────────────────────


class TestPillowUpgrade:
    def test_pillow_import(self) -> None:
        """Pillow imports without error."""
        import PIL

        assert PIL.__version__ >= "12.1.1"

    def test_image_new(self) -> None:
        """Image.new — most common API in this codebase."""
        from PIL import Image

        img = Image.new("RGB", (64, 64), color=(255, 0, 0))
        assert img.size == (64, 64)
        assert img.mode == "RGB"

    def test_image_open_and_save(self, tmp_path: object) -> None:
        """Image.open / save round-trip — used extensively in model demos."""
        from pathlib import Path

        from PIL import Image

        path = Path(str(tmp_path)) / "test.png"
        img = Image.new("RGBA", (32, 32), color=(0, 128, 255, 200))
        img.save(path)
        loaded = Image.open(path)
        assert loaded.size == (32, 32)
        assert loaded.mode == "RGBA"

    def test_image_fromarray(self) -> None:
        """Image.fromarray — used in many model post-processing pipelines."""
        import numpy as np
        from PIL.Image import fromarray

        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[25:75, 25:75] = [255, 128, 0]
        img = fromarray(arr)
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_image_resize_resampling(self) -> None:
        """Image.resize with Resampling enum — used in preprocessing."""
        from PIL.Image import Image, Resampling, fromarray

        import numpy as np

        arr = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        img = fromarray(arr)
        resized = img.resize((32, 32), resample=Resampling.BILINEAR)
        assert resized.size == (32, 32)

    def test_image_convert(self) -> None:
        """Image.convert — used for mode conversions (RGB/L/RGBA)."""
        from PIL import Image

        img = Image.new("RGB", (16, 16))
        gray = img.convert("L")
        assert gray.mode == "L"
        rgba = img.convert("RGBA")
        assert rgba.mode == "RGBA"

    def test_imagedraw(self) -> None:
        """ImageDraw — used in visualization/demo code."""
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 90], fill="red", outline="blue")
        # Verify the draw modified the image (center pixel should be red)
        pixel = img.getpixel((50, 50))
        assert pixel == (255, 0, 0)

    def test_unidentified_image_error(self) -> None:
        """UnidentifiedImageError — used in error handling."""
        from PIL import UnidentifiedImageError

        assert issubclass(UnidentifiedImageError, Exception)


# ── wheel (CVE-2026-24049) ───────────────────────────────────────────


class TestWheelUpgrade:
    def test_wheel_import(self) -> None:
        """wheel imports without error."""
        import wheel

        assert wheel.__version__ >= "0.46.2"

    def test_wheel_wheelfile(self) -> None:
        """WheelFile class is accessible — used during release builds."""
        from wheel.wheelfile import WheelFile

        assert WheelFile is not None

    def test_wheel_bdist_wheel(self) -> None:
        """bdist_wheel command is accessible."""
        from wheel.bdist_wheel import bdist_wheel

        assert bdist_wheel is not None
