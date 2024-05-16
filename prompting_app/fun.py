import time
import predictionguard as pg
import numpy as np

from langchain import PromptTemplate
from sentence_transformers import SentenceTransformer

from constants import models, neuralchat_template, noushermes_template
from models import Llm_response

from dotenv import load_dotenv
load_dotenv()


def run_llm_query(query_obj):

    model = query_obj.model
    print(model)

    if model == "noushermes":
        prompt_template = noushermes_template
    elif model == "neuralchat":
        prompt_template = neuralchat_template
    else:
        raise Exception(f"Unrecognized model <{model}> was provided")

    final_prompt = PromptTemplate(template=prompt_template,
    input_variables=["prompt","context"],
    )

    start_time = time.time()

    result=pg.Completion.create(
            model=models[model],
            prompt=final_prompt.format(
                prompt = query_obj.prompt,
                context = query_obj.context
            ),
            max_tokens=query_obj.max_tokens,
            temperature=query_obj.temperature
        )
    print(result)
    response = result['choices'][0]['text']

    print(response)

    # Stop measuring the execution time
    end_time = time.time()

    # Calculate the elapsed time
    execution_time = end_time - start_time

    llm_response = Llm_response(
        **query_obj.dict(),
        llm_response=response,
        execution_time=execution_time
    )

    return llm_response

def embed(sentence):
    name = "all-MiniLM-L12-v2"
    model = SentenceTransformer(name)
    return model.encode(sentence)

def cosine_similarity(vec1, vec2):
    """Compute the cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def get_semantic_similarity(comparison_obj):

    pg_embedding = embed(comparison_obj.summary1)
    article_embedding = embed(comparison_obj.summary2)

    similarity = cosine_similarity(pg_embedding, article_embedding)
    
    return similarity