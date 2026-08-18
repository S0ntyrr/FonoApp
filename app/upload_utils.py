from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


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

    upload_dir.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta_fs = upload_dir / nombre_archivo
    ruta_fs.write_bytes(contenido)
    return f"{public_prefix.rstrip('/')}/{nombre_archivo}"
