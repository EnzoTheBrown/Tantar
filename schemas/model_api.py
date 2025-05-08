from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, List
from .file_model import FileType


class PersonAPIModel(BaseModel):
    name: str = Field(..., description="The name of the person")
    is_moral: bool = Field(..., description="Indicates if the person is a moral entity")


class RoleAPIModel(BaseModel):
    name: str = Field(..., description="The name of the role")
    person: PersonAPIModel = Field(
        ..., description="The person associated with the role"
    )


class SharesAPIModel(BaseModel):
    person: PersonAPIModel = Field(
        ..., description="The person associated with the shares"
    )
    percentage: float = Field(
        ..., description="The percentage of shares held by the person"
    )


class PVAGAPIModel(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="The ID of the file from the external API")
    file_type: FileType = Field(
        description="The type of the file from the external API",
        default=FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE,
    )


class StatusAPIModel(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="The ID of the file from the external API")
    file_type: FileType = Field(
        description="The type of the file from the external API",
        default=FileType.STATUTS,
    )


class ContratAPIModel(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="The ID of the file from the external API")
    file_type: FileType = Field()
    offeror: Optional[PersonAPIModel] = Field(
        ..., description="The person making the offer"
    )
    offeree: Optional[PersonAPIModel] = Field(
        ..., description="The person receiving the offer"
    )


class OrdreDeMouvementAPIModel(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="The ID of the file from the external API")
    file_type: FileType = Field(
        description="The type of the file from the external API",
        default=FileType.ORDRE_DE_MOUVEMENT_DE_TITRES,
    )


class RegistreDeMouvementAPIModel(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="The ID of the file from the external API")
    file_type: FileType = Field(
        description="The type of the file from the external API",
        default=FileType.REGISTRE_DE_MOUVEMENT_DE_TITRES,
    )


FileAPIModel = Union[
    PVAGAPIModel,
    StatusAPIModel,
    ContratAPIModel,
    OrdreDeMouvementAPIModel,
    RegistreDeMouvementAPIModel,
]


class CompanyDetailsAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    siren: str
    name: str
    naf_code: str
    activity: str
    capital: Optional[float]
    juridic_form: Optional[str]


class CompanyAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str = Field(
        ..., description="The original ID of the company from the external API"
    )
    name: str = Field(..., description="The name of the company")
    siren: str = Field(..., description="The SIREN number of the company")
    roles: List[RoleAPIModel] = Field(
        ..., description="List of roles associated with the company"
    )
    shares: List[SharesAPIModel] = Field(
        ..., description="List of shares associated with the company"
    )
    files: List[FileAPIModel] = Field(
        ..., description="List of files associated with the company"
    )
    details: Optional[CompanyDetailsAPIModel] = Field(
        description="Details of the company", default=None
    )
