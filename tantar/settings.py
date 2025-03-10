import logfire
import os
import toml
import dotenv
from string import Template
from pydantic import BaseModel, model_validator, Field, AliasChoices
from typing_extensions import Self
from typing import Optional
import boto3

dotenv.load_dotenv()


class APPSettings(BaseModel):
    url: str
    secret: str


class OpenAI(BaseModel):
    api_key: str


class AWSConfig(BaseModel):
    service_name: str
    region: Optional[str] = 'eu-west-1'
    key: str
    secret: str

    @property
    def client(self) -> boto3.client:
        return boto3.client(
            self.service_name,
            region_name=self.region,
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
        )

    @model_validator(mode='after')
    def check_settings(self)  -> Self:
        assert self.key != "${AWS_ACCESS_KEY}", "key not provided"
        assert self.secret != "${AWS_SECRET_KEY}", "secret not provided"
        return self


class S3Config(AWSConfig):
    service_name: str = 's3'
    bucket: str

    @model_validator(mode='after')
    def check_settings(self)  -> Self:
        assert self.key != "${AWS_ACCESS_KEY}", "key not provided"
        assert self.secret != "${AWS_SECRET_KEY}", "secret not provided"
        assert self.bucket != ""
        return self


class LambdaConfig(AWSConfig):
    service_name: str = 'lambda'


class TextractConfig(AWSConfig):
    service_name: str = 'textract'


class LogFire(BaseModel):
    logfire_token: str

    def __init__(self, logfire_token, environment):
        super().__init__(logfire_token=logfire_token)
        logfire.configure(environment=environment, service_name='tantar')


class Pitantar(BaseModel):
    url: str


class Pappers(BaseModel):
    url: str
    key: str


class Settings(BaseModel):
    textract: TextractConfig
    lambda_: LambdaConfig = Field(validation_alias=AliasChoices('lambda'))
    s3: S3Config
    app: APPSettings
    openai: OpenAI
    logfire: LogFire
    pitantar: Pitantar
    pappers: Pappers


def load_settings(toml_path):
    with open(toml_path, 'r') as file:
        settings_content = file.read()
    template = Template(settings_content)
    substituted_content = template.safe_substitute(os.environ)
    config_data = toml.loads(substituted_content)
    return Settings(**config_data)


SETTINGS = load_settings('tantar.toml')

