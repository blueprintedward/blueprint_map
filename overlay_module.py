"""Overlay new nodes on the blueprint PDF image at grid coordinates."""

import os

import fitz
from PIL import Image, ImageDraw, ImageFont


def load_blueprint_image(pdf_path: str, dpi: int = 150) -> Image.Image:
    """Load first page of PDF as RGB PIL Image."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def grid_to_pixel(
    col: int,
    row: int,
    image_width: int,
    image_height: int,
    grid_cols: int = 12,
    grid_rows: int = 12,
) -> tuple[int, int]:
    """Map grid (col, row) to pixel (x, y) at cell center. 0-based."""
    cw = image_width / grid_cols
    ch = image_height / grid_rows
    x = int((col + 0.5) * cw)
    y = int((row + 0.5) * ch)
    return x, y


def _get_cjk_font(size: int = 14):
    """Return a font that supports Chinese, or default."""
    candidates = [
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msjhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_point_and_label(
    image: Image.Image,
    x: int,
    y: int,
    label: str,
    font_path: str | None = None,
    point_radius: int = 8,
) -> Image.Image:
    """Draw a circle at (x, y) and label text to the right. Modifies image in place, returns it."""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 14) if font_path and os.path.isfile(font_path) else _get_cjk_font(14)
    draw.ellipse([x - point_radius, y - point_radius, x + point_radius, y + point_radius], fill=(70, 130, 220), outline=(30, 60, 120), width=2)
    draw.text((x + point_radius + 4, y - 7), label, fill=(40, 40, 40), font=font)
    return image
