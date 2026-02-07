"""
Конвертация видео: MP4, WEBM, MOV, AVI.
Использует ffmpeg через subprocess.
"""

import subprocess
from pathlib import Path

from .base import ConversionError


def _check_ffmpeg() -> bool:
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_video(source_path: str, source_fmt: str, target_fmt: str, output_dir: Path) -> str:
    """
    Конвертирует видео через ffmpeg.
    """
    if not _check_ffmpeg():
        raise ConversionError(
            'Для конвертации видео необходим ffmpeg. '
            'Скачайте: https://ffmpeg.org/download.html и добавьте в PATH'
        )

    base = Path(source_path).stem
    out_path = output_dir / f'{base}.{target_fmt}'

    if target_fmt == 'webm':
        cmd = ['ffmpeg', '-y', '-i', source_path, '-c:v', 'libvpx-vp9', '-c:a', 'libvorbis', str(out_path)]
    else:
        cmd = ['ffmpeg', '-y', '-i', source_path, '-c:v', 'libx264', '-c:a', 'aac', str(out_path)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            err = result.stderr[-500:] if result.stderr else 'Unknown error'
            raise ConversionError(f'Ошибка ffmpeg: {err}')
    except subprocess.TimeoutExpired:
        raise ConversionError('Конвертация видео заняла слишком много времени')
    except Exception as e:
        if isinstance(e, ConversionError):
            raise
        raise ConversionError(f'Ошибка конвертации видео: {e}')

    if not out_path.exists():
        raise ConversionError('Результирующий файл не был создан')

    return str(out_path)
