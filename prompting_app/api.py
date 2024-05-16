from fastapi import FastAPI
from fun import run_llm_query, get_semantic_similarity
from models import Item, Comparison

app = FastAPI()


@app.post("/gen/")
async def generate_response(item: Item):

    response = run_llm_query(item)
    
    return {"result": response.llm_response}

@app.post("/compare/")
async def generate_response(item: Comparison):

    similarity = get_semantic_similarity(item)
    similarity_score = round(float(similarity), 4)

    return {"result": similarity_score}
