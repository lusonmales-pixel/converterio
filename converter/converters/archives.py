"""
Конвертация архивов: ZIP <-> TAR.
"""

import io
import tarfile
import zipfile
from pathlib import Path

from .base import ConversionError


def convert_archive(source_path: str, source_fmt: str, target_fmt: str, output_dir: Path) -> str:
    """
    ZIP -> TAR или TAR -> ZIP.
    """
    base = Path(source_path).stem
    out_path = output_dir / f'{base}.{target_fmt}'

    if source_fmt == 'zip' and target_fmt == 'tar':
        return _zip_to_tar(source_path, str(out_path))
    if source_fmt == 'tar' and target_fmt == 'zip':
        return _tar_to_zip(source_path, str(out_path))

    raise ConversionError(f'Конвертация {source_fmt} -> {target_fmt} не поддерживается')


def _zip_to_tar(zip_path: str, tar_path: str) -> str:
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with tarfile.open(tar_path, 'w') as tf:
                for name in zf.namelist():
                    data = zf.read(name)
                    ti = tarfile.TarInfo(name=name)
                    ti.size = len(data)
                    tf.addfile(ti, io.BytesIO(data))
        return tar_path
    except Exception as e:
        raise ConversionError(f'Ошибка ZIP->TAR: {e}')


def _tar_to_zip(tar_path: str, zip_path: str) -> str:
    try:
        with tarfile.open(tar_path, 'r') as tf:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for member in tf.getmembers():
                    if member.isfile():
                        data = tf.extractfile(member).read()
                        zf.writestr(member.name, data)
        return zip_path
    except Exception as e:
        raise ConversionError(f'Ошибка TAR->ZIP: {e}')
