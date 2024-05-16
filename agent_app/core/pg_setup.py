import os
from core.llm_funs import embed
from core.pg_funs import content_scraper, get_company_summary, get_doclinks, summarize
from db.database import push_to_db, setup_db

def scrape_info(base_url):

    urls_df = get_doclinks(base_url)
    print(f"length of the doclinks dataframe : {len(urls_df)}")

    docs_df = content_scraper(urls_df, base_url)
    processed_df = summarize(docs_df)

    company_summary = get_company_summary(processed_df)

    processed_df['vector'] = processed_df['summary'].apply(embed)

    data = [
        {
            "chunk": 0,
            "detail": row.title,  
            "text": row.summary,  
            "vector": row.vector  
        }
        for index, row in processed_df.iterrows()
    ]

    data.append(
        {
            "chunk": 0,
            "detail": "pg_summary",  
            "text": company_summary,  
            "vector": embed(company_summary)
        }
    )

    # store in db
    db = setup_db()
    PG_TABLE = os.environ.get("PG_TABLE")
    push_to_db(db, PG_TABLE, data)

    return PG_TABLE, db.table_names
