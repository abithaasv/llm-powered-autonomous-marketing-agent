import time
import predictionguard as pg
# from langchain import PromptTemplate
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
import predictionguard as pg
from constants import models, neuralchat_template, noushermes_template
from api.models import LLM_query, LLM_response

from dotenv import load_dotenv
load_dotenv()

import logging

# Get the logger for the current module
logger = logging.getLogger(__name__)


name="all-MiniLM-L12-v2"
model = SentenceTransformer(name)

def embed_batch(batch):
    return [model.encode(sentence) for sentence in batch]

def embed(sentence):
    return model.encode(sentence)

#### LLM FUNCTIONS ####

def run_llm_query(query_obj:LLM_query):

    model = query_obj.model

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
    response = result['choices'][0]['text']

    # Stop measuring the execution time
    end_time = time.time()

    # Calculate the elapsed time
    execution_time = end_time - start_time

    logger.info(f"Ran LLM query with {model}, in {execution_time:.2f} seconds")

    llm_response = LLM_response(
        **query_obj.dict(),
        llm_response=response,
        execution_time=execution_time
    )

    return llm_response