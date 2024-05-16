import pandas as pd
import requests
from bs4 import BeautifulSoup

from api.models import LLM_query
from core.llm_funs import run_llm_query

from dotenv import load_dotenv
load_dotenv()

import logging

# Get the logger for the current module
logger = logging.getLogger(__name__)

def get_doclinks(url):
    
    # Make a request to fetch the page content
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if there's an error

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class 'open'
    open_elements = soup.find_all(class_='open')

    # Initialize a list to hold all the hrefs
    titles = ["Getting Started"]
    urls = ["/"]

    mydict = {}

    fern_sidebar_link_elements = soup.find_all(class_="fern-sidebar-link")

    for element in fern_sidebar_link_elements:

        text = element.find('span', class_='fern-sidebar-link-text').get_text()
        url = element['href']

        urls.append(url)
        titles.append(text)

        mydict[text] = url

    df = pd.DataFrame({"title" : titles, "url" : urls})
    
    return df
    
def page_scraper(url):

    response = requests.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors

    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming there's a main container that holds the content you're interested in.
    main_content = soup.select_one('main')

    # Remove or ignore elements that typically contain code snippets
    for code_snippet in main_content.find_all(['code']):  # Adjust tags as necessary
        code_snippet.decompose()

    # Initialize a list to hold all the content in order
    content_in_order = []

    # Iterate through the main content's children or specific selections to maintain order
    # This example fetches paragraphs and headings, maintaining their order on the page
    for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        content_in_order.append(element.get_text(strip=True))

    # Combine all extracted texts into a single string
    full_text = '\n'.join(content_in_order)

    return full_text

def content_scraper(urldf, base_url):

    scraped_contents = []
    for idx, row in urldf.iterrows():
        url = base_url + row["url"]
        content = page_scraper(url)
        scraped_contents.append(content)
        logger.info(f"Extracted data from {row['url']}")

    urldf.insert(2, "Scraped Content", scraped_contents)
    return urldf

def get_character_limit(content):

    upper_limit = 900
    lower_limit = 200

    onethird = len(content)/3

    character_limit = int( onethird - (onethird % 50) )

    return max(lower_limit, min(character_limit, upper_limit))

def summarize(urls_df):
    summaries = []
    extracted_keywords = []

    for idx, row in urls_df.iterrows():
        
        page_content = row["Scraped Content"]

        character_limit = get_character_limit(page_content)

        try :
            prompt = f"You are a marketing expert who is trying to understand a new company and determine the brand identity. The input below is an article from the developer documents of this company. From this input, extract the most important information that might be relevant for this brand. Your response should be less than {character_limit} characters."
            context = page_content
            model = "neuralchat"
            temperature = 0.1
            max_tokens = 150

            summary_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)

            summary = run_llm_query(summary_query).llm_response
            summaries.append(summary)
        except Exception as e:
            logger.exception(f"index {idx} - {row['url']}, failed to summarize with exception {e}")

        try:
            prompt = "The input below is an article from the developer documents of company. From this input, extract the most important keywords that may be relevant for this company."
            context = page_content
            model = "noushermes"
            temperature = 0.1
            max_tokens = 25

            keywords_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)

            keywords = run_llm_query(keywords_query).llm_response
            extracted_keywords.append(keywords)
        except Exception as e:
            logger.exception(f"index {idx} - {row['url']}, failed to extract keywords with exception {e}")


    new_df = urls_df.assign(extracted_keywords=extracted_keywords, summary=summaries)

    return new_df



def get_company_summary(processed_df):
    # Convert the column to a list of strings
    list_of_strings = processed_df['summary'].tolist()

    # Join all the strings in the list with a newline character as the separator
    full_text = '\n'.join(list_of_strings)

    prompt = "You are a marketing expert who is trying to understand a new company and determine the brand identity. The input below is a thorough but preliminary article about this company provided by a researcher. From this input, extract the most important information that might be relevant for this brand and create a short marketing document with technical details, which can be presented to the enterprise customers as well as enterprise investors of this company."
    context = full_text
    model = "neuralchat"
    temperature = 0.3
    max_tokens = 400

    summary_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)

    company_summary = run_llm_query(summary_query).llm_response

    return company_summary
