from datetime import date
from enum import Enum
from pydantic import BaseModel, validator
from typing import List

class SourceEnum(str, Enum):
    TLDR = "tldr"
    TECHCRUNCH = "techcrunch"
    TECHDIRT = "techdirt"
    ALL = "all"

class ExtractRequest(BaseModel):
    source: SourceEnum
    startdate: date
    enddate: date

    @validator("source")
    def validate_source(cls, value):
        if value not in SourceEnum:
            raise ValueError("Invalid source. Must be 'TLDR' or 'Techcrunch'.")
        return value

class RankRequest(BaseModel):
    id_list: List[str]

class CompanyInfoUpdateRequest(BaseModel):
    url: str = "https://docs.predictionguard.com"

class GetTableRequest(BaseModel):
    tablename : str = "pgmain"

class GeneratePostRequest(BaseModel):
    article_id: str
    platforms : List = ["LinkedIn", "Twitter"]

class LLM_query(BaseModel):
    prompt: str
    context: str
    model:str
    temperature:float
    max_tokens:int

class Comparison(BaseModel):
    summary1: str
    summary2: str

class LLM_response(BaseModel):
    prompt: str
    context: str
    model:str
    temperature:float
    max_tokens:int
    llm_response:str
    execution_time:float