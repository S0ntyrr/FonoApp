from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


def _es_solo_lectura(directorio: Path) -> bool:
    """Verifica si el sistema de archivos del directorio es de solo lectura."""
    test_path = directorio / f".write_test_{uuid4().hex}"
    try:
        directorio.mkdir(parents=True, exist_ok=True)
        test_path.touch()
        test_path.unlink()
        return False
    except (OSError, PermissionError):
        return True


async def save_upload_safely(
    upload: UploadFile,
    *,
    upload_dir: Path,
    allowed_extensions: set[str],
    max_size_bytes: int,
    public_prefix: str,
) -> str | None:
    if not upload or not upload.filename:
        return None

    extension = Path(upload.filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión no permitida: {extension}",
        )

    contenido = await upload.read()
    if not contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido está vacío.",
        )

    if len(contenido) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el límite de {max_size_bytes} bytes.",
        )

    # En Vercel el filesystem es de solo lectura; intentar /tmp como fallback.
    directorio_efectivo = upload_dir
    if _es_solo_lectura(upload_dir):
        tmp_dir = Path("/tmp") / upload_dir.name
        try:
            tmp_dir.mkdir(parents=True, exist_ok=True)
            directorio_efectivo = tmp_dir
        except (OSError, PermissionError):
            # No se puede escribir en ningún lado — devolver None sin romper el flujo
            return None

    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta_fs = directorio_efectivo / nombre_archivo
    ruta_fs.write_bytes(contenido)
    return f"{public_prefix.rstrip('/')}/{nombre_archivo}"
