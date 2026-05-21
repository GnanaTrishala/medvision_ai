from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{user_id}/{filename}")
def serve_file(
    user_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    settings = get_settings()
    path = Path(settings.uploads_dir) / str(user_id) / filename
    if not path.is_file() or ".." in filename:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path)
