"""
Модули конвертации по категориям.
"""

from .base import ConversionError
from .images import convert_image
from .audio import convert_audio
from .video import convert_video
from .documents import convert_document
from .archives import convert_archive

CONVERTERS = {
    'image': convert_image,
    'audio': convert_audio,
    'video': convert_video,
    'document': convert_document,
    'archive': convert_archive,
}


def convert_file(source_path, source_ext: str, target_ext: str, output_dir) -> str:
    """
    Выбирает подходящий конвертер и выполняет конвертацию.
    Возвращает путь к результирующему файлу.
    """
    from converter.formats import get_category, normalize_format

    source_key = normalize_format(source_ext)
    target_key = normalize_format(target_ext)
    if not source_key or not target_key:
        raise ConversionError('Неподдерживаемый формат файла')

    category = get_category(source_key)
    if not category or category not in CONVERTERS:
        raise ConversionError(f'Конвертация из {source_ext} не поддерживается')

    converter_fn = CONVERTERS[category]
    return converter_fn(source_path, source_key, target_key, output_dir)
