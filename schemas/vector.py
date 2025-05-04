from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pydantic import BaseModel
from .file_model import ContractType, EventType, JuridicCategory

embedder = get_registry().get("openai").create()
VectorType = Vector(embedder.ndims())


class MoralPersonInput(LanceModel):
    account_id: int
    original_id: str
    name: str = embedder.SourceField()


class PhysicalPersonInput(LanceModel):
    account_id: int
    original_id: str
    firstname: str = embedder.SourceField()
    lastname: str = embedder.SourceField()

    @property
    def name(self):
        return f"{self.firstname} {self.lastname}"


class MoralPersonVector(LanceModel):
    account_id: int
    original_id: str
    name: str = embedder.SourceField()
    vector: VectorType = embedder.VectorField()


class PhysicalPersonVector(LanceModel):
    account_id: int
    original_id: str
    firstname: str = embedder.SourceField()
    lastname: str = embedder.SourceField()
    vector: VectorType = embedder.VectorField()

    @property
    def name(self):
        return f"{self.firstname} {self.lastname}"


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


class EventVector(LanceModel):
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


class FileChunk(BaseModel):
    text: str
    page_index: int
