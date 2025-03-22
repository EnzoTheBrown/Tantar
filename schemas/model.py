from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pydantic import BaseModel, Field, EmailStr, ConfigDict, BeforeValidator
from typing import List, Optional, Union, Annotated
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
import uuid
from schemas.file_model import FileType, JuridicCategory, EventType, ContractType
from enum import Enum

embedder = get_registry().get("openai").create()
VectorType = Vector(embedder.ndims())


class BaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseSQLModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    original_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


"""
    Account
"""


class Account(BaseSQLModel, table=True):
    name: str
    users: list["User"] = Relationship(back_populates="account")
    companies: list["Company"] = Relationship(back_populates="account")
    files: list["File"] = Relationship(back_populates="account")


class AccountInputModel(BaseModel):
    name: str


class AccountAPIModel(BaseModel):
    original_id: str
    name: str


"""
    User
"""


class User(BaseSQLModel, table=True):
    email: str
    hashed_password: str
    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship(back_populates="users")


class UserInputModel(BaseModel):
    email: EmailStr
    password: str
    invitation_token: Optional[str] = None


class UserAPIModel(BaseModel):
    email: EmailStr
    original_id: str
    account: AccountAPIModel


"""
    Company
"""


class Company(BaseSQLModel, table=True):
    name: str
    siren: str
    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship(back_populates="companies")
    files: list["File"] = Relationship(back_populates="company")
    details: Optional["CompanyDetails"] = Relationship(back_populates="company")


class CompanyInputModel(BaseModel):
    name: str
    siren: str


class CompanyAPIModel(BaseModel):
    original_id: str
    name: str
    siren: str
    account: Optional[AccountAPIModel] = None
    details: Optional["CompanyDetailsAPIModel"] = None


class CompanyDetails(BaseSQLModel, table=True):
    siren: str
    name: str
    naf_code: str
    activity: str
    capital: Optional[float] = None
    juridic_form: Optional[str] = None
    company_id: int = Field(foreign_key="company.id")
    company: Company = Relationship(back_populates="details")


class CompanyDetailsAPIModel(BaseModel):
    siren: str
    name: str
    naf_code: str
    activity: str
    capital: float
    juridic_form: str


"""
    File
"""


class FileChunk(BaseModel):
    text: str
    page_number: int


def format_siren(siren: str):
    siren = siren.replace(" ", "")
    if len(siren) != 9:
        raise ValueError("Siren must be 9 characters long")
    return siren


class FileMetadata(BaseModel):
    title: str = Field(description="Le titre du document")
    type: FileType = Field(description="Le type de document")
    siren: Annotated[Optional[str], BeforeValidator(format_siren)] = Field(
        description="The siren of the company", default=None
    )
    date: Optional[datetime] = Field(description="The date of the file", default=None)
    name: Optional[str] = Field(description="The name of the company", default=None)


class File(BaseSQLModel, table=True):
    name: str
    s3_path: str
    status: int = Field(default=0)
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")
    account: Optional[Account] = Relationship(back_populates="files")
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="files")
    created_at: datetime = Field(default_factory=datetime.now)
    watched_at: Optional[datetime] = Field(default=None)
    type: Optional[FileType] = Field(default=None)
    events: List["EventDBModel"] = Relationship(
        back_populates="file", cascade_delete=True
    )
    contracts: List["ContractDBModel"] = Relationship(
        back_populates="file", cascade_delete=True
    )


class FileInputModel(BaseModel):
    name: str
    s3_path: str


class FileAPIModel(BaseModel):
    original_id: str
    name: str
    s3_path: str
    status: int
    company: Optional[CompanyAPIModel] = None
    created_at: datetime
    watched_at: Optional[datetime] = None
    type: Optional[FileType] = None


class SerFileAPIModel(BaseModel):
    original_id: str
    name: str
    s3_path: str
    status: int
    company: Optional[CompanyAPIModel] = None
    type: Optional[FileType] = None


"""
    Person
"""


class PhysicalPersonModel(BaseModel):
    firstname: str = Field(description="firstname")
    lastname: str = Field(description="lastname")


class MoralPersonModel(BaseModel):
    name: str = Field(description="The name of the moral person")


class PhysicalPerson(BaseSQLModel, table=True):
    firstname: str
    lastname: str

    @property
    def name(self):
        return f"{self.firstname} {self.lastname}"


class PhysicalPersonDBModel(BaseSQLModel, table=True):
    firstname: str
    lastname: str


class MoralPerson(BaseSQLModel, table=True):
    name: str


class MoralPersonDBModel(BaseSQLModel, table=True):
    name: str
    account_id: int = Field(foreign_key="account.id")


Person = Union[PhysicalPerson, MoralPerson]


"""
    Event
"""


class Event(FileChunk):
    text: str = Field(description="Full text describing the event")
    title: str = Field(description="Short text explaining the event", title=None)
    physical_persons: List[PhysicalPerson] = Field(
        description="The list of physical persons", default=[]
    )
    moral_persons: List[MoralPerson] = Field(
        description="The list of moral persons", default=[]
    )
    page_number: int = Field(description="The index of the page in the file")
    type: EventType = Field(description="The type of the event")
    label: JuridicCategory = Field(description="The category of the event")

    @property
    def name(self):
        return self.title


class EventDBModel(BaseSQLModel, table=True):
    text: str
    title: str
    page_number: int
    type: EventType
    label: JuridicCategory
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="events")
    date: Optional[datetime] = Field(default=None)

    @property
    def name(self):
        return self.title


class JuridicEvents(BaseModel):
    events: List[Event] = Field(description="The list of juridic events")


class ClassifiedJuridicEvent(Event):
    type: EventType = Field(description="The type of the event")
    juridic_category: JuridicCategory = Field(description="The category of the event")


class EventInput(BaseModel):
    original_id: str
    account_id: str
    company_id: str
    file_id: str
    date: str
    label: JuridicCategory
    type: EventType
    text: str
    title: str
    page_index: int
    file_name: str
    siren: str

    @property
    def name(self):
        return self.title


class VectorEvent(LanceModel):
    original_id: str
    account_id: str
    company_id: str
    file_id: str
    date: str
    type: str
    text: str = embedder.SourceField()
    title: str
    page_index: int
    file_name: str
    siren: str
    label: str
    vector: VectorType = embedder.VectorField()


class EventCategoriesAPIModel(BaseModel):
    events: List[Event]
    categories: List[str]


"""
    Contract
"""


class Contract(BaseModel):
    type: ContractType = Field(description="The type of the contract")
    title: str = Field(description="The title of the contract")
    offeror: Person = Field(description="The offeror")
    offeree: Person = Field(description="The offeree")


class ContractDBModel(BaseSQLModel, table=True):
    type: ContractType
    title: str
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="contracts")


class ContractChunkInput(BaseModel):
    account_id: str
    type: ContractType
    original_id: str
    text: str
    page_index: int
    file_id: str
    file_name: str
    date: str
    company_id: str
    siren: str


class ContractChunk(LanceModel):
    """
    This class represents a chunk of text extracted from a document.
    It is used to store the text, the label, and the vector representation of the chunk.
    """

    account_id: str
    original_id: str
    type: str
    text: str = embedder.SourceField()
    page_index: int
    file_id: str
    file_name: str
    date: str
    company_id: str
    siren: str
    vector: VectorType = embedder.VectorField()


"""
    Graph
"""


class NodeType(str, Enum):
    COMPANY = "company"
    CONTRACT = "contract"
    PV_AG = "pv_ag"
    EVENT = "event"
    MORAL_PERSON = "moral_person"
    PHYSICAL_PERSON = "physical_person"


class GraphNode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: NodeType
    original_id: str
    name: str

    source_edges: List["GraphEdge"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={"foreign_keys": "[GraphEdge.source_id]"},
    )
    target_edges: List["GraphEdge"] = Relationship(
        back_populates="target",
        sa_relationship_kwargs={"foreign_keys": "[GraphEdge.target_id]"},
    )

    def __str__(self):
        return self.label

    @classmethod
    def create_node(cls, entity: Union["Company", "File", "Event"]):
        return cls(
            label=entity.__class__.__name__,
            original_id=entity.original_id,
            name=entity.name,
        )


class EdgeLabel(str, Enum):
    DECIDES = "DECIDES"
    OFFEROR = "OFFEROR"
    OFFEREE = "OFFEREE"
    ORGANIZED = "ORGANIZED"
    AUTHORIZED = "AUTHORIZED"


class GraphEdge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="graphnode.id")
    target_id: int = Field(foreign_key="graphnode.id")
    label: EdgeLabel

    source: GraphNode = Relationship(
        back_populates="source_edges",
        sa_relationship_kwargs={"foreign_keys": "[GraphEdge.source_id]"},
    )
    target: GraphNode = Relationship(
        back_populates="target_edges",
        sa_relationship_kwargs={"foreign_keys": "[GraphEdge.target_id]"},
    )

    @classmethod
    def create_edge(cls, source: GraphNode, target: GraphNode, label: str):
        return cls(source=source, target=target, label=label)
