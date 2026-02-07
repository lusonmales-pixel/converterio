"""
Конвертация изображений: JPG, PNG, WEBP, ICO, BMP, TIFF.
Использует Pillow (PIL).
"""

import os
from pathlib import Path

from PIL import Image

from .base import ConversionError


def convert_image(source_path: str, source_fmt: str, target_fmt: str, output_dir: Path) -> str:
    """
    Конвертирует изображение из source_fmt в target_fmt.
    Возвращает путь к созданному файлу.
    """
    try:
        img = Image.open(source_path)
    except Exception as e:
        raise ConversionError(f'Не удалось открыть изображение: {e}')

    # Конвертация в RGB для форматов, не поддерживающих прозрачность
    if target_fmt in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    elif target_fmt == 'ico':
        # ICO обычно требует нескольких размеров; сохраняем основной
        if img.mode == 'RGBA':
            pass
        elif img.mode != 'RGB':
            img = img.convert('RGB')

    # Расширение для целевого формата
    ext_map = {'jpg': 'jpg', 'jpeg': 'jpg', 'png': 'png', 'webp': 'webp', 'ico': 'ico', 'bmp': 'bmp', 'tiff': 'tiff'}
    out_ext = ext_map.get(target_fmt, target_fmt)
    base = Path(source_path).stem
    out_path = output_dir / f'{base}.{out_ext}'

    pillow_fmt = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP', 'ico': 'ICO', 'bmp': 'BMP', 'tiff': 'TIFF'}.get(target_fmt, 'PNG')

    save_kwargs = {}
    if target_fmt in ('jpg', 'jpeg'):
        save_kwargs['quality'] = 90
        save_kwargs['optimize'] = True
    elif target_fmt == 'webp':
        save_kwargs['quality'] = 90
    elif target_fmt == 'ico':
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        valid_sizes = [s for s in sizes if s[0] <= max(img.size)]
        img.save(out_path, 'ICO', sizes=valid_sizes if valid_sizes else [(256, 256)], **save_kwargs)
        return str(out_path)

    try:
        img.save(out_path, pillow_fmt, **save_kwargs)
    except Exception as e:
        raise ConversionError(f'Ошибка сохранения: {e}')

    return str(out_path)
