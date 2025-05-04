from .relational import CompanyAPIModel, Event, FileAPIModel
from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    type: str


class WebSocketNewEventMessage(WebSocketMessage):
    type: str = "new_event"
    event: Event


class WebSocketNewCompanyMessage(WebSocketMessage):
    type: str = "new_company"
    company: CompanyAPIModel


class WebSocketParsingError(WebSocketMessage):
    type: str = "parsing_error"
    file: FileAPIModel


class WebSocketNewFileMessage(WebSocketMessage):
    type: str = "new_file"
    file: FileAPIModel
