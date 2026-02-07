"""
Определение поддерживаемых форматов и правил конвертации.
Без хардкода — всё централизовано здесь.
"""

# Категория : список форматов с MIME и расширениями
FORMATS = {
    'image': {
        'jpg': {'mime': 'image/jpeg', 'extensions': ['jpg', 'jpeg']},
        'png': {'mime': 'image/png', 'extensions': ['png']},
        'webp': {'mime': 'image/webp', 'extensions': ['webp']},
        'ico': {'mime': 'image/x-icon', 'extensions': ['ico']},
        'bmp': {'mime': 'image/bmp', 'extensions': ['bmp']},
        'tiff': {'mime': 'image/tiff', 'extensions': ['tiff', 'tif']},
    },
    'audio': {
        'mp3': {'mime': 'audio/mpeg', 'extensions': ['mp3']},
        'wav': {'mime': 'audio/wav', 'extensions': ['wav']},
        'ogg': {'mime': 'audio/ogg', 'extensions': ['ogg']},
        'aac': {'mime': 'audio/aac', 'extensions': ['aac']},
        'flac': {'mime': 'audio/flac', 'extensions': ['flac']},
    },
    'video': {
        'mp4': {'mime': 'video/mp4', 'extensions': ['mp4']},
        'webm': {'mime': 'video/webm', 'extensions': ['webm']},
        'mov': {'mime': 'video/quicktime', 'extensions': ['mov']},
        'avi': {'mime': 'video/x-msvideo', 'extensions': ['avi']},
    },
    'document': {
        'pdf': {'mime': 'application/pdf', 'extensions': ['pdf']},
        'docx': {'mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'extensions': ['docx']},
        'txt': {'mime': 'text/plain', 'extensions': ['txt']},
        'html': {'mime': 'text/html', 'extensions': ['html', 'htm']},
    },
    'archive': {
        'zip': {'mime': 'application/zip', 'extensions': ['zip']},
        'tar': {'mime': 'application/x-tar', 'extensions': ['tar']},
    },
}

# Матрица допустимых конвертаций: source -> [targets]
CONVERSION_MATRIX = {
    # Images
    'jpg': ['png', 'webp'],
    'jpeg': ['png', 'webp'],
    'png': ['jpg', 'webp', 'ico'],
    'webp': ['jpg', 'png'],
    'bmp': ['png'],
    'tiff': ['jpg'],
    'tif': ['jpg'],
    'ico': [],  # только входящий
    # Audio
    'mp3': ['wav', 'ogg'],
    'wav': ['mp3', 'ogg', 'aac'],
    'ogg': ['mp3', 'wav'],
    'flac': ['mp3'],
    'aac': [],
    # Video
    'mp4': ['webm'],
    'webm': ['mp4'],
    'mov': ['mp4'],
    'avi': ['mp4'],
    # Documents
    'pdf': ['docx'],
    'docx': ['pdf'],
    'txt': ['pdf', 'docx'],
    'html': ['pdf'],
    'htm': ['pdf'],
    # Archives
    'zip': ['tar'],
    'tar': ['zip'],
}


def get_category(format_key: str) -> str | None:
    """Возвращает категорию формата или None."""
    for cat, formats in FORMATS.items():
        for key, data in formats.items():
            if key == format_key or format_key.lower() in data['extensions']:
                return cat
    return None


def normalize_format(ext: str) -> str | None:
    """Нормализует расширение к ключу формата."""
    ext = ext.lower().lstrip('.')
    for cat, formats in FORMATS.items():
        for key, data in formats.items():
            if ext in data['extensions'] or ext == key:
                return key
    return None


def get_available_targets(source_ext: str) -> list[str]:
    """Возвращает список доступных целевых форматов для исходного."""
    key = normalize_format(source_ext)
    if not key:
        return []
    targets = CONVERSION_MATRIX.get(key, [])
    return list(targets)


def is_conversion_allowed(source_ext: str, target_ext: str) -> bool:
    """Проверяет, допустима ли конвертация source -> target."""
    targets = get_available_targets(source_ext)
    target_key = normalize_format(target_ext)
    return target_key in targets if target_key else False


def get_mime_for_format(format_key: str) -> str:
    """Возвращает MIME для формата."""
    for cat, formats in FORMATS.items():
        if format_key in formats:
            return formats[format_key]['mime']
    return 'application/octet-stream'
