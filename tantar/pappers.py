import requests
from pydantic import BaseModel, Field
from tantar.settings import SETTINGS
from schemas.relational import Company
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


def create_company_details_(company: Company) -> Company:
    pappers_company = get_pappers_company(company.siren)
    logger.info(
        f"We got new elements from pappers to complete company details: {pappers_company.siren} {pappers_company.name}"
    )
    company.details_naf_code = pappers_company.naf_code
    company.details_activity = pappers_company.activity
    company.details_capital = pappers_company.capital
    company.details_juridic_form = pappers_company.juridic_form
    return company


def create_company_details(company: Company, db=None) -> Company:
    company.details_naf_code = company.details_naf_code or ""
    company.details_activity = company.details_activity or ""
    if company.details_capital is None:
        company.details_capital = 1000
    company.details_juridic_form = (
        company.details_juridic_form or "SAS, Société par actions simplifiée"
    )
    if db is not None:
        db.add(company)
    return company
