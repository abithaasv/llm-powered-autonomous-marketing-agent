import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from core.llm_funs import run_llm_query
import newspaper
from newspaper import Article
from api.models import LLM_query

import logging

# Get the logger for the current module
logger = logging.getLogger(__name__)

def is_date_in_range(article_date, start_date, end_date):
    return start_date <= article_date <= end_date

def summarize_article(article):
    prompt = f"Summarize the article provided in the input. Create a concise yet insightful summary under 250 words to ensure focus on essential information."
    context = article
    model = "noushermes"
    temperature = 0.1
    max_tokens = 300

    summary_query = LLM_query(prompt = prompt, context = context, model = model, temperature=temperature, max_tokens=max_tokens)
    summary = run_llm_query(summary_query).llm_response
    return summary

def scrape_techdirt(start_date, end_date):
    articles_data = []
    # Loop through each day in the date range
    delta = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        # Format the URL for the current date
        date_str = current_date.strftime('%Y/%m/%d/')
        url = f'https://www.techdirt.com/{date_str}'

        # Fetch the content of the page
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find all articles using the class 'storywrap'
            articles = soup.find_all('div', class_='storywrap')

            for article in articles:
                # Extract the title, date, and text content from each article
                title = article.find('h1', class_='posttitle').get_text(strip=True)
                date = article.find('span', class_='pub_date').get_text(strip=True)
                text = ' '.join(p.get_text(strip=True) for p in article.find_all('p'))
                author_url = article.find('div', class_='byline').find('a')['href']
                articles_data.append({
                    'date': date,
                    'content': text,
                    'link': author_url,
                    'source': 'Tech Dirt'
                })

        # Move to the next day
        current_date += delta

    # Convert the list of articles to a DataFrame
    return pd.DataFrame(articles_data)

def scrape_techcrunch(start_date, end_date):
    # Define the URL of the website to scrape
    url = 'https://techcrunch.com/category/artificial-intelligence/'
    # Build the source to fetch articles
    ai_category = newspaper.build(url, memoize_articles=False)
    articles_data = []

    # Filter and print articles published within the date range
    for article in ai_category.articles:
        try:
            article.download()
            article.parse()
        except:
            # If there's an issue with downloading/parsing, skip this article
            continue  

        # convert publish_date datetime object to date object
        if article.publish_date:
            article_date = article.publish_date.date()
        else:
            # If publish_date is not available, we skip the article
            continue

        # Check if the article's date is within the start and end date
        if start_date <= article_date <= end_date:
            if article.url:
                articles_data.append({
                    'date': article_date.strftime('%Y-%m-%d'),
                    'content': article.text,
                    'link': article.url,
                    'source': 'Tech Crunch'
                })    
            break         
    return pd.DataFrame(articles_data)

def scrape_tldr(start_date, end_date):
    base_url = "https://tldr.tech"
    articles_data = []

    current_date = start_date
    while current_date <= end_date:
        # TLDR's structure appears to organize content by date, making this approach feasible
        if current_date.weekday() < 5:  # we only want to scrape weekdays
            date_str = current_date.strftime("%Y-%m-%d")
            daily_url = f"{base_url}/ai/{date_str}"
            try:
                response = requests.get(daily_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Assuming the divs with class 'mt-3' hold the articles; this may need adjustment
                    divs = soup.find_all('div', class_='mt-3')
                    for div in divs:
                        article_link = div.find('a')['href'] if div.find('a') else None
                        title = div.find('h3').text.strip() if div.find('h3') else "No title"
                        text = div.get_text(strip=True)  # Simplistic text extraction
                        if article_link and title:
                            articles_data.append({
                                'date':date_str,
                                'content': text,
                                'link': urljoin(base_url, article_link),  # Ensure full link
                                'source': 'TLDR'
                            })
            except Exception as e:
                logger.exception(f"Error scraping TLDR content for date {date_str}: {e}")

        current_date += timedelta(days=1)
    return pd.DataFrame(articles_data)

def scrape_aibusiness(start_date, end_date):
    # Define the URL of the website to scrape
    url = 'https://aibusiness.com/latest-news'
    articles_data = []

    # Build the source to fetch articles
    ai_category = newspaper.build(url, memoize_articles=False)

    # Filter and print articles published within the date range
    for article in ai_category.articles:
        # Download the article
        try:
            article.download()
            article.parse()
        except:
            continue  # If there's an issue with downloading/parsing, skip this article

        # Convert article publish date to datetime
        if article.publish_date:
            article_date = article.publish_date.date()
        else:
            # If publish_date is not available, we skip the article
            continue

        # Check if the article's date is within the start and end date
        if start_date <= article_date <= end_date:
            if article.url:
                articles_data.append({
                        'date': article_date.strftime('%Y-%m-%d'),
                        'content': article.text,
                        'link': article.url,
                        'source': 'AI Business'
                    })    
            break
    return pd.DataFrame(articles_data)