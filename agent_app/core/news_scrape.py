import pandas as pd
from datetime import datetime
import numpy as np
import os
from typing import List
import predictionguard as pg

from api.models import LLM_query
from db.database import push_to_db, setup_db
from core.llm_funs import embed, run_llm_query
from core.news_funs import scrape_aibusiness, scrape_techcrunch, scrape_tldr,scrape_techdirt, summarize_article
from constants import brand_personality

from dotenv import load_dotenv
load_dotenv()

import logging

# Get the logger for the current module
logger = logging.getLogger(__name__)

def extract_news(source, start_date, end_date, keyword = "AI"):
    if source == "techcrunch":
        articles_df = scrape_techcrunch(start_date, end_date)
    elif source == "tldr":
        articles_df = scrape_tldr(start_date, end_date)
    elif source == "techdirt":
        articles_df = scrape_techdirt(start_date, end_date)
    elif source == "all":
        df_techcrunch = scrape_techcrunch(start_date, end_date)
        df_tldr = scrape_tldr(start_date, end_date)
        df_aibusiness = scrape_techdirt(start_date, end_date)

        # Combine all DataFrames
        articles_df = pd.concat([df_techcrunch, df_tldr, df_aibusiness], ignore_index=True)
    
    # Generate an ID column
    articles_df['id'] = articles_df.apply(
        lambda row: f"{row['source'].replace(' ', '')}_{row['date'].replace('-', '')}_{np.random.randint(10000, 99999)}", axis=1
        )
    
    #### Summarize news
    articles_df['summary'] = articles_df['content'].apply(summarize_article)

    #### Embed and store to lancedb
    articles_df.rename(columns={"summary": "text"}, inplace=True)
    articles_df['vector'] = articles_df['text'].apply(embed)

    articles_df['overall_similarity'] = 2
    articles_df['is_relevant'] = 0
    articles_df['topics'] = ""
    articles_df['topics_context'] = ""

    # store in db
    db = setup_db()
    NEWS_TABLE = os.environ.get("NEWS_TABLE")

    push_to_db(db, NEWS_TABLE, data = articles_df)

    tldrnumber = 1

    logger.info(f"Extracted {tldrnumber} TLDR articles")

    return articles_df



def semantic_comparison(article_ids: List):

    #### semantic comparison
    db = setup_db()

    PG_TABLE = os.environ.get("PG_TABLE")
    company_table = db.open_table(PG_TABLE)
    summary_vector = (company_table.search()
                .where("detail = 'pg_summary'", prefilter=True)
                .limit(1)
                .to_pandas())["vector"].iloc[0]

    NEWS_TABLE = os.environ.get("NEWS_TABLE")
    news_table = db.open_table(NEWS_TABLE)
    query_tuple = ", ".join([f"'{id}'" for id in article_ids])
    query_tuple = f"({query_tuple})"
    semantic_df = (news_table.search(summary_vector)
                   .where(f"id IN {query_tuple}", prefilter=True)
                   .metric("cosine")
                   .to_pandas()
    )

    semantic_df['overall_similarity'] = semantic_df['_distance']
    semantic_df.drop(columns=['_distance'], inplace=True)

    SIMILARITY_THRESHOLD = 0.5
    semantic_df['is_relevant'] = (semantic_df['overall_similarity'] < SIMILARITY_THRESHOLD).astype(int)

    def topic_matching(vector):
        topics_df = (company_table.search(vector)
                    .where("detail != 'pg_summary'", prefilter=True)
                    .metric("cosine")
                    .limit(limit=5)
                    .to_pandas())
        return topics_df

    for index, row in semantic_df.iterrows():
        if row['is_relevant'] == 1:

            topics_df = topic_matching(row['vector'])

            topic_list = topics_df["detail"].tolist()
            topics = " ".join(topic_list)

            topic_summaries = topics_df['text'].tolist()
            topics_context = '\n'.join(topic_summaries)

            row["topics"] = topics
            row["topics_context"] = topics_context

            id = row["id"]
            is_relevant = row["is_relevant"]
            overall_similarity = row['overall_similarity'] 

            news_table = db.open_table(NEWS_TABLE)
            
            news_table.update(where=f"id = '{id}'", 
                              values={"overall_similarity": overall_similarity, 
                                                                 "is_relevant": is_relevant, 
                                                                 "topics": topics, 
                                                                 "topics_context":topics_context}
                                                                 )
            logger.info(f"Article {id}, is relevant. Updated the table record")

    return semantic_df

def generate_post(article_id, platforms):

    db = setup_db()

    # get article from the db
    NEWS_TABLE = os.environ.get("NEWS_TABLE")
    news_table = db.open_table(NEWS_TABLE)

    article_row = (news_table.search()
                   .where(f"id = '{article_id}'", prefilter=True)
                   .to_pandas()
                   )
    logger.info(article_row["topics_context"])
    
    topics_context = article_row["topics_context"].iloc[0]

    # perform narrative-generation
    prompt = "The summary for a start-up company called Prediction Guard is provided in the input. A summary of a news article that is relevant to Prediction Guard is also provided in the input. Act as a marketing expert and generate a professional post for how Prediction Guard can help based on this news article. Make sure it is less than 3000 characters and more than 500 characters."
    
    context = f"Summary of Prediction Guard :\n{topics_context}\nSummary of news article :\n{article_row['text']}"
    model = "noushermes"
    temperature = 0.3
    max_tokens = 350

    postgen_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)

    narrative = run_llm_query(postgen_query).llm_response

    logger.info(f"generated narrative : {narrative[:20]}...")

    # perform sanity checks
    sanity_checks = {}

    # Factual consistency check.
    factuality_result = pg.Factuality.check(
                reference=article_row['content'].values[0], 
                text=narrative
                )
    sanity_checks["factuality"] = factuality_result["checks"]

    # Toxicity check
    toxicity_result = pg.Toxicity.check(
                text=narrative
                )
    
    sanity_checks["toxicity"] = toxicity_result["checks"]

    # PII check
    pii_result = pg.PII.check(
        prompt=narrative,
        replace=False,
        replace_method="fake"
        )
    sanity_checks["pii"] = pii_result["checks"]

    logger.info(f"Sanity checks - {sanity_checks}")


    def inject_brand_voice(narrative, platform):
        # inject brand voice
        prompt = f"The narrative for a first draft of a post for a start-up company called Prediction Guard, and the brand personality of Prediction Guard is provided in the input. Act as a marketing expert and rewrite the existing narrative as a professional {platform} post, adhering to the brand personality of Prediction Guard. Make sure it is less than 3000 characters and more than 500 characters. Structure the post in a paragraph format. Include relevant emojis and hashtags."

        context = f"NARRATIVE:\n{narrative}\n{brand_personality}"
        model = "neuralchat"
        temperature = 0.3
        max_tokens = 350

        rebranding_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)

        post = run_llm_query(rebranding_query).llm_response

        logger.info(f"generated post for {platform} : {post[:20]}...")

        return post
    
    posts={}
    for platform in platforms:
        post = inject_brand_voice(narrative, platform)
        posts[platform] = post

    return posts