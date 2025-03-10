import requests
from pydantic import BaseModel, Field
from tantar.settings import SETTINGS
from schemas.model import CompanyDetails, Company
from typing import Optional
from tantar.utils.logger import get_logger

logger = get_logger(__name__)


class PappersCompany(BaseModel):
    siren: str
    name: str = Field(alias="nom_entreprise")
    naf_code: str = Field(alias="code_naf")
    activity: str = Field(alias="domaine_activite")
    capital: Optional[float] = Field(alias="capital", default=None)
    juridic_form: Optional[str] = Field(alias="forme_juridique", default=None)


def get_pappers_company(siren: str) -> PappersCompany:
    url = f"{SETTINGS.pappers.url}/entreprise"
    headers = {"api-key": SETTINGS.pappers.key}
    response = requests.get(url, headers=headers, params={"siren": siren})
    if response.status_code != 200:
        raise Exception(f"Failed to get company from Pappers API: {response.text}")
    return PappersCompany(**response.json())


def create_company_details(company: Company) -> CompanyDetails:
    pappers_company = get_pappers_company(company.siren)
    logger.info(
        f"We got new elements from pappers to complete company details: {pappers_company.siren} {pappers_company.name}"
    )
    return CompanyDetails(
        siren=pappers_company.siren,
        name=pappers_company.name,
        naf_code=pappers_company.naf_code,
        activity=pappers_company.activity,
        capital=pappers_company.capital,
        company=company,
        juridic_form=pappers_company.juridic_form,
    )
