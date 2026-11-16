"""Image processor that resizes large images (max 2048px on long side)."""
from __future__ import annotations

import io
from PIL import Image


def process_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Tuple[bytes, str]:
    """Ensure image long side does not exceed 2048 px."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        max_dim = max(width, height)
        if max_dim > 2048:
            scale = 2048.0 / max_dim
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            out_buf = io.BytesIO()
            fmt = img.format or "JPEG"
            img.save(out_buf, format=fmt)
            return out_buf.getvalue(), mime_type
        return image_bytes, mime_type
    except Exception:
        return image_bytes, mime_type
