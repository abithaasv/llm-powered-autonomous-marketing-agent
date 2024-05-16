from pydantic import BaseModel

class Item(BaseModel):
    prompt: str
    context: str
    model:str
    temperature:float
    max_tokens:int

class Comparison(BaseModel):
    summary1: str
    summary2: str

class Llm_response(BaseModel):
    prompt: str
    context: str
    model:str
    temperature:float
    max_tokens:int
    llm_response:str
    execution_time:float