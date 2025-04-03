from pydantic import BaseModel
from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
    status,
    File as FFile,
    Security,
    Query,
    BackgroundTasks,
)
from fastapi.responses import StreamingResponse
from schemas.model import FileAPIModel, Company, File, User
from tantar.database import get_db, Session
from sqlmodel import select
from tantar.settings import SETTINGS
import uuid
from tantar.utils.logger import get_logger
from .authenticate import get_current_user
from .websocket import notify, notify_account, notify_account
from typing import Optional, Annotated
from schemas.websocket import WebSocketParsingError, WebSocketNewFileMessage
from datetime import datetime
from process_file import run_process_file

logger = get_logger(__name__)
file_router = APIRouter()
s3 = SETTINGS.s3.client


@file_router.post("/file", status_code=201)
async def create_file(
    user: Annotated[
        User,
        Security(
            get_current_user,
        ),
    ],
    background_tasks: BackgroundTasks,
    company_id: Optional[str] = Query(None),
    file=FFile(...),
    db: Session = Depends(get_db),
):
    s3_key = f"{user.account.original_id}/{uuid.uuid4()}.pdf"
    s3.put_object(
        Bucket=SETTINGS.s3.bucket,
        Key=s3_key,
        Body=file.file,
    )
    if company_id:
        db_company = db.exec(
            select(Company).where(Company.original_id == company_id)
        ).first()
        if db_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
    else:
        db_company = None
    new_file = File(
        name=file.filename,
        s3_path=s3_key,
        company=db_company,
        account=user.account,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    file_model = FileAPIModel.model_validate(new_file)
    await notify_account(
        account_id=user.account.original_id,
        message=WebSocketNewFileMessage(file=file_model),
    )
    background_tasks.add_task(run_process_file, new_file.original_id)

    return file_model


@file_router.get("/files", response_model=list[FileAPIModel])
def get_files(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    company_id: Optional[str] = Query(None),
    ordered_by: Optional[str] = Query(
        None, description="Optional ordering field: 'created_at' or 'watched_at'"
    ),
):
    allowed_order_fields = {"created_at", "watched_at"}
    clause = File.account_id == user.account.id
    if company_id:
        clause = (clause) & (Company.original_id == company_id)
    if ordered_by:
        if ordered_by not in allowed_order_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ordered_by parameter. Must be one of: {', '.join(allowed_order_fields)}",
            )
        if ordered_by == "watched_at":
            clause = (clause) & (File.watched_at != None)
    else:
        ordered_by = "created_at"
    if company_id:
        query = select(File).join(Company).where(clause)
    else:
        query = select(File).where(clause)
    order_field = getattr(File, ordered_by)
    query = query.order_by(order_field.desc())

    files = db.exec(query).all()

    return [FileAPIModel.model_validate(f) for f in files]


@file_router.get("/file/{file_original_id}", response_model=FileAPIModel)
def get_file(
    file_original_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        file = db.exec(select(File).where(File.original_id == file_original_id)).one()
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")
    return FileAPIModel.model_validate(file)


@file_router.get("/file/{file_original_id}/download")
def download_file(
    file_original_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        file = db.exec(select(File).where(File.original_id == file_original_id)).one()
        file.watched_at = datetime.now()
        db.commit()
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")
    file_stream = s3.get_object(
        Bucket=SETTINGS.s3.bucket,
        Key=file.s3_path,
    )["Body"]
    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file.name}"},
    )


class FileInformation(BaseModel):
    title: Optional[str]
    company_name: Optional[str]
    siren: Optional[str]


@file_router.patch(
    "/company/{original_id}/file/{file_original_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
async def invalidate_file(
    original_id: str,
    file_original_id: str,
    file_information: FileInformation,
    db: Session = Depends(get_db),
):
    db_company = db.query(Company).filter(Company.original_id == original_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    file = db.query(File).filter(File.original_id == file_original_id).one()
    file.status = -1
    db.commit()
    db.refresh(file)
    validated_file = FileAPIModel.model_validate(file)
    await notify(
        company_id=original_id,
        message=WebSocketParsingError(file=validated_file),
        db=db,
    )
    return validated_file
