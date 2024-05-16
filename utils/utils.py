import os
import json
import predictionguard as pg

from langchain import PromptTemplate
import pandas as pd
import urllib.request
import html2text

from dotenv import load_dotenv
load_dotenv()

def get_page_content(url):
    # Let's get the html off of a website.
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    fp.close()
    
    # And convert it to text.
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(html)

    return text

def clean_content(text, k_start, k_end):
    # Clean things up just a bit.
    text = text.split(k_start)[1]
    text = text.split(k_end)[0]

    return text

def get_summary(content_to_summarize, prompt_template, max_tokens = 200, temperature = 0.1):

    summary_prompt = PromptTemplate(template=prompt_template,
    input_variables=["context"],
    )

    result=pg.Completion.create(
            model="Nous-Hermes-Llama2-13B",
            prompt=summary_prompt.format(
                content=content_to_summarize
            ),
            max_tokens=max_tokens,
            temperature=temperature
        )
    summary = result['choices'][0]['text']

    return summary

def get_summary(content_to_summarize, prompt_template, model="Nous-Hermes-Llama2-13B", max_tokens = 200, temperature = 0.1):

    summary_prompt = PromptTemplate(template=prompt_template,
    input_variables=["context"],
    )

    result=pg.Completion.create(
            model=model,
            prompt=summary_prompt.format(
                content=content_to_summarize
            ),
            max_tokens=max_tokens,
            temperature=temperature
        )
    summary = result['choices'][0]['text']

    return summary


def get_character_limit(content):

    upper_limit = 900
    lower_limit = 200

    onethird = len(content)/3

    character_limit = int( onethird - (onethird % 50) )

    return max(lower_limit, min(character_limit, upper_limit))


def get_summary_with_limit(content_to_summarize, character_limit, prompt_template, model="Nous-Hermes-Llama2-13B", max_tokens = 200, temperature = 0.1):

    summary_prompt = PromptTemplate(template=prompt_template,
    input_variables=["character_limit", "context"],
    )

    result=pg.Completion.create(
            model=model,
            prompt=summary_prompt.format(
                character_limit=character_limit,
                content=content_to_summarize
            ),
            max_tokens=max_tokens,
            temperature=temperature
        )
    summary = result['choices'][0]['text']

    return summary

def get_keywords(content, prompt_template, model="Nous-Hermes-Llama2-13B", max_tokens = 200, temperature = 0.1):

    summary_prompt = PromptTemplate(template=prompt_template,
    input_variables=["context"],
    )

    result=pg.Completion.create(
            model=model,
            prompt=summary_prompt.format(
                content=content
            ),
            max_tokens=max_tokens,
            temperature=temperature
        )
    keywords = result['choices'][0]['text']

    return keywords