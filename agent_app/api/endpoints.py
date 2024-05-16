from fastapi import FastAPI, Query, HTTPException, Request
from db.database import delete_table, get_all_table_records, get_table_record
from api.models import GeneratePostRequest,  CompanyInfoUpdateRequest, ExtractRequest, RankRequest
from core.news_scrape import extract_news, generate_post, semantic_comparison
from core.pg_setup import scrape_info

import logging
from logs.logger_config import setup_logging

setup_logging()

app = FastAPI()

logger = logging.getLogger(__name__)

# Middleware for logging requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

@app.get("/")
async def read_root():
    logger.info("Processing root endpoint")
    return {"Hello": "World"}

@app.get("/table")
async def get_table(tablename: str = Query(default="pgmain")):
    try:
        df = get_all_table_records(tablename)
        df.drop(columns=["vector"], inplace=True)
        df_dict = df.to_dict(orient="records")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return df_dict

@app.get("/record")
async def get_table(tablename: str = Query(default="news"), record_id: "str" = Query(default="")):
    try:
        df = get_table_record(tablename, record_id)
        df.drop(columns=["vector"], inplace=True)
        df_dict = df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return df_dict

@app.delete("/clear")
async def clear_table(tablename: str = Query(default="news")):
    try:
        df = delete_table(tablename)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return "success"

@app.post("/update_company_info/")
async def update_company_info(request: CompanyInfoUpdateRequest):

    url = request.url

    # # URL of company docs page
    # base_url = 'https://docs.predictionguard.com'

    _, _ = scrape_info(url)
    
    return "success"


@app.post("/extract/")
async def extract(request: ExtractRequest):

    keyword = 'AI'

    # Extract the input parameters
    source = request.source
    startdate = request.startdate
    enddate = request.enddate

    # Call the main function
    articles_df = extract_news(source, startdate, enddate, keyword)

    articles_df.drop(columns=["vector"], inplace=True)

    articles_dict_list = articles_df.to_dict(orient="records")

    logger.info(f"ready to return extracted articles")

    return articles_dict_list



@app.post("/rank/")
async def rank(request: RankRequest):

    id_list = request.id_list

    df = semantic_comparison(id_list)
    df.sort_values(by='overall_similarity', ascending=True, inplace=True)

    df['rank'] = df['overall_similarity'].rank(method='min')
    df['score'] = 1 - df['overall_similarity']

    df.drop(columns=["vector"], inplace=True)
    df_dict = df.to_dict(orient="records")

    return df_dict


@app.post("/generate_post/")
async def generate_response(request : GeneratePostRequest):

    article_id = request.article_id
    platforms=request.platforms

    posts = generate_post(article_id, platforms)

    return posts