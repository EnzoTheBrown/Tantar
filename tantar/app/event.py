from fastapi import Depends, HTTPException, APIRouter, Query
from schemas.relational import (
    Company,
    File,
    JuridicCategory,
    User,
    EventCategoriesAPIModel,
    EventAPIModel,
    PVAGAPIModel,
    FileAPIModel,
    Contract,
)
from schemas.vector import EventInput
from schemas.file_model import EventType
from tantar.database import get_db, Session
from sqlmodel import select
from typing import Optional
from datetime import datetime
from tantar.utils.logger import get_logger
from tantar.vector_database import get_events, post_event
from .authenticate import get_current_user
import uuid
from typing import List

logger = get_logger(__name__)

event_router = APIRouter()


def build_event_api_model(event: EventInput, file: File) -> EventAPIModel:
    file_api = FileAPIModel.model_validate(file)
    pvag = PVAGAPIModel(original_id=file.original_id, file=file_api)
    if isinstance(event.type, EventType):
        event_type = event.type
    else:
        try:
            event_type = EventType(event.type)
        except ValueError:
            event_type = EventType.AUTRE
    if isinstance(event.label, JuridicCategory):
        event_label = event.label
    else:
        try:
            event_label = JuridicCategory(event.label)
        except ValueError:
            event_label = JuridicCategory.AUTRE
    event_date = None
    if getattr(event, "date", None):
        try:
            event_date = datetime.strptime(event.date, "%Y-%m-%d")
        except ValueError:
            event_date = None
    return EventAPIModel(
        original_id=event.original_id,
        text=event.text,
        title=event.title,
        page_index=event.page_index,
        type=event_type,
        label=event_label,
        pvag=pvag,
        date=event_date,
    )


@event_router.post("/company/{original_id}/event", status_code=201)
async def create_event(
    original_id: str,
    event: EventInput,
    db: Session = Depends(get_db),
):
    db_company = db.exec(
        select(Company).where(Company.original_id == original_id)
    ).first()
    file = db.exec(select(File).where(File.original_id == event.file_id)).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    user = db.exec(select(User).where(User.id == file.user_id)).first()
    account_id = user.original_id if user else ""
    new_event = EventInput(
        original_id=str(uuid.uuid4()),
        account_id=account_id,
        company_id=db_company.original_id,
        file_id=event.file_id,
        date=event.date,
        label=event.label,
        type=event.type,
        text=event.text,
        title=event.title,
        page_index=event.page_index,
        file_name=file.name,
        siren=db_company.siren,
    )
    post_event(new_event)
    return new_event


@event_router.get(
    "/events",
    response_model=EventCategoriesAPIModel,
)
async def get_events_(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    question: Optional[str] = Query(None),
    k: int = Query(10),
    company_id: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    events = get_events(
        account_id=user.original_id,
        question=question,
        company_id=company_id,
        label=JuridicCategory._value2member_map_[label] if label is not None else None,
        k=k,
        start_date=start_date,
        end_date=end_date,
        siren=None,
    )
    categories = list({event.label for event in events})
    events_api = []
    for event in events:
        file = db.exec(select(File).where(File.original_id == event.file_id)).first()
        if file is None:
            continue
        events_api.append(build_event_api_model(event, file))
    return EventCategoriesAPIModel(
        categories=categories,
        events=events_api,
    )


@event_router.get(
    "/categories",
)
def get_categories():
    return {category.name: category.value for category in JuridicCategory}


@event_router.get(
    "/events/{original_id}/authorized_contracts",
    response_model=List[Contract],
)
def get_authorized_contracts(
    original_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return []
