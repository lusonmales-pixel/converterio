"""
Конвертация аудио: MP3, WAV, OGG, AAC, FLAC.
Использует pydub (требует ffmpeg в системе).
"""

import os
import subprocess
from pathlib import Path

from .base import ConversionError

# Проверка наличия pydub
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


def _check_ffmpeg() -> bool:
    """Проверяет наличие ffmpeg в системе."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_audio(source_path: str, source_fmt: str, target_fmt: str, output_dir: Path) -> str:
    """
    Конвертирует аудио через pydub/ffmpeg.
    """
    if not PYDUB_AVAILABLE:
        raise ConversionError('Модуль pydub не установлен. Выполните: pip install pydub')
    if not _check_ffmpeg():
        raise ConversionError(
            'Для конвертации аудио необходим ffmpeg. '
            'Скачайте: https://ffmpeg.org/download.html и добавьте в PATH'
        )

    fmt_map = {
        'mp3': 'mp3', 'wav': 'wav', 'ogg': 'ogg',
        'aac': 'aac', 'flac': 'flac',
    }
    out_ext = fmt_map.get(target_fmt, target_fmt)
    base = Path(source_path).stem
    out_path = output_dir / f'{base}.{out_ext}'

    try:
        audio = AudioSegment.from_file(source_path, format=source_fmt)
    except Exception as e:
        raise ConversionError(f'Не удалось открыть аудиофайл: {e}')

    export_format = out_ext
    export_params = {}
    if target_fmt == 'mp3':
        export_params['bitrate'] = '192k'
    elif target_fmt == 'aac':
        export_params['bitrate'] = '128k'

    try:
        audio.export(str(out_path), format=export_format, **export_params)
    except Exception as e:
        raise ConversionError(f'Ошибка экспорта аудио: {e}')

    return str(out_path)
