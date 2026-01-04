from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Union, Annotated
from .file_model import JuridicCategory, EventType, FileType
from enum import Enum
from sqlmodel import SQLModel, select, Field as sql_field
from datetime import datetime


class CompanyDetails(BaseModel):
    name: str = Field(description="The name of the company")
    siren: str = Field(description="The siren of the company")
    naf_code: Optional[str] = Field(default=None)
    activity: Optional[str] = Field(default=None)
    capital: Optional[float] = Field(default=None)
    juridic_form: Optional[str] = Field(default=None)


class Company(BaseModel):
    name: str
    siren: str
    details: Optional[CompanyDetails] = Field(
        description="The details of the company",
        default=None,
    )


class File(BaseModel):
    name: str
    type: Optional[FileType] = Field(
        description="The type of the file",
        default=None,
    )


class PhysicalPerson(BaseModel):
    firstname: str = Field(description="firstname of the person")
    lastname: str = Field(description="lastname of the person")

    @property
    def name(self):
        return f"{self.firstname} {self.lastname}"


class MoralPerson(BaseModel):
    name: str = Field(
        description="The name of a company, can't be something else than a company"
    )


Person = Union[PhysicalPerson, MoralPerson]


class Event(BaseModel):
    text: str = Field(description="Full text describing the event")
    title: str = Field(description="Short text explaining the event", title=None)
    page_index: int = Field(description="The index of the page in the file")
    type: EventType = Field(description="The type of the event")
    label: JuridicCategory = Field(description="The category of the event")

    @property
    def name(self):
        return self.title


class Shares(BaseModel):
    share: float = Field(description="The share of the person in the company")
    date: str = Field(description="The date of the share")

    @property
    def name(self):
        return f"{self.share}%"


class RoleName(str, Enum):
    PRESIDENT = "PRESIDENT"
    DIRECTOR = "DIRECTOR"
    FOUNDER = "FOUNDER"
    ASSOCIATE = "ASSOCIATE"
    UNKNOW = "UNKNOW"


class Role(BaseModel):
    name: RoleName = Field(description="The name of the role")


NodeElement = Union[Event, Company, MoralPerson, PhysicalPerson, Role, Shares, File]

node_element_factory = {
    "Event": Event,
    "Company": Company,
    "Role": Role,
    "Shares": Shares,
    "File": File,
    "PhysicalPerson": PhysicalPerson,
    "MoralPerson": MoralPerson,
}


class Node(SQLModel, table=True):
    id: Optional[int] = sql_field(default=None, primary_key=True)
    type: str
    name: str
    content: str
    original_id: Optional[str] = sql_field(
        description="The original ID in the database",
        index=True,
    )


def create_node(db, node: NodeElement) -> Node:
    node = Node(
        name=node.name, content=node.model_dump_json(), type=node.__class__.__name__
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_node(db, node_id: int) -> Node:
    node = db.exec(select(Node).where(Node.id == node_id)).first()

    if node is None:
        raise ValueError("Node not found")
    return node


def get_nodes(db) -> List[Node]:
    nodes = db.exec(select(Node)).all()
    return nodes


class EdgeLabel(str, Enum):
    DECIDES = "DECIDES"
    IS = "IS"
    OF = "OF"
    OWNS = "OWNS"
    SIGNS = "SIGNS"
    IS_MENTIONNED = "IS_MENTIONNED"
    ORGANIZED = "ORGANIZED"
    AUTHORIZED = "AUTHORIZED"


class Edge(SQLModel, table=True):
    id: Optional[int] = sql_field(default=None, primary_key=True)
    source: int = sql_field(foreign_key="node.id")
    target: int = sql_field(foreign_key="node.id")
    label: EdgeLabel = sql_field(
        description="The label of the edge",
    )


def add_edge(
    db,
    source: Node,
    target: Node,
    label: EdgeLabel,
) -> None:
    if source.id is None:
        raise ValueError("Source node ID is None")
    if target.id is None:
        raise ValueError("Target node ID is None")
    source_node = get_node(db, source.id)
    target_node = get_node(db, target.id)
    edge = Edge(source=source_node.id, target=target_node.id, label=label)
    db.add(edge)
    db.commit()
    db.refresh(edge)


def get_edges(db) -> List[Edge]:
    edges = db.exec(select(Edge)).all()
    return edges


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
