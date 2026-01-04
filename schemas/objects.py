from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Union, Annotated

from schemas.file_model import EventType, JuridicCategory, FileType

from datetime import datetime


class Event(BaseModel):
    text: str = Field(description="Full text describing the event")
    title: str = Field(description="Short text explaining the event", title=None)
    page_index: int = Field(description="The index of the page in the file")
    type: EventType = Field(description="The type of the event")
    label: JuridicCategory = Field(description="The juridic category of the event")


class MoralPerson(BaseModel):
    name: str = Field(
        description="The name of a company, can't be something else than a company"
    )


class PhysicalPerson(BaseModel):
    firstname: str = Field(description="firstname of the person")
    lastname: str = Field(description="lastname of the person")

    @property
    def name(self):
        return f"{self.firstname} {self.lastname}"


Person = Union[PhysicalPerson, MoralPerson]


def format_siren(siren: str):
    siren = siren.replace(" ", "")
    if len(siren) != 9:
        raise ValueError("Siren must be 9 characters long")
    return siren


class FileMetadata(BaseModel):
    title: str = Field(description="Le titre du document")
    type: FileType = Field(description="Le type de document")
    siren: Annotated[Optional[str], BeforeValidator(format_siren)] = Field(
        description="The siren of the company If this is a contract this must be the offeree not the offeror",
        default=None,
    )
    date: Optional[datetime] = Field(description="The date of the file", default=None)
    name: Optional[str] = Field(description="The name of the company", default=None)


class ContractParties(BaseModel):
    offeree: Person = Field(description="The offeree of the contract")
    offeror: Person = Field(description="The offeror of the contract")


class Shares(BaseModel):
    person: Person = Field(description="The person who owns the shares")
    shares: int = Field(description="The number of shares owned by the person")
    percentage: float = Field(
        description="The percentage of shares owned by the person"
    )
