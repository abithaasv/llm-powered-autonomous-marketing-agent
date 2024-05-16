import streamlit as st
from datetime import datetime
import requests
import pandas as pd

# Set page configuration
st.set_page_config(page_title="LLM Marketing Agent App", layout="wide")
st.title('LLM Marketing Agent App')

PREDEFINED_URL = "https://docs.predictionguard.com"

def update_company_info():
    response = requests.post("http://localhost:8000/update_company_info/", json={"url": PREDEFINED_URL})
    return response.ok

def extract_articles(source, from_date, to_date):
    payload = {
        "source": source,
        "startdate": from_date.strftime('%Y-%m-%d'),  # Ensure date is in the correct format
        "enddate": to_date.strftime('%Y-%m-%d')
    }
    response = requests.post("http://localhost:8000/extract/", json=payload)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def rank_articles(id_list):
    payload = {"id_list": id_list}
    response = requests.post("http://localhost:8000/rank/", json=payload)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def generate_post_for_article(article_id):
    response = requests.post("http://localhost:8000/generate_post/", json={"article_id": article_id})
    if response.status_code == 200:
        return True, response.text
    else:
        return False, response.text

with st.sidebar:
    if st.button('Update PG Info'):
        if update_company_info():
            st.success("PG info successfully updated.")
        else:
            st.error("Failed to update company info.")
    # Display the specified text below the "Update PG Info" button
    st.write("This updates the brand voice and the latest company documents, ensuring that content generation aligns closely with Prediction Guard's evolving knowledge database and brand voice, enabling the creation of posts that resonate with their latest messaging and insights.")
with st.form(key='date_range_form'):
    from_date = st.date_input("From Date", datetime.today())
    to_date = st.date_input("To Date", datetime.today())
    source = st.selectbox("Select Source", ["TLDR", "Techcrunch", "All"])
    submitted = st.form_submit_button("Extract Articles")

if submitted:
    success, result = extract_articles(source.lower(), from_date, to_date)
    if success:
        articles_df = pd.DataFrame(result)
        st.session_state['articles_df'] = articles_df  # Save articles to session state
        st.write("Extracted Articles:", articles_df)
    else:
        st.error(f"Failed to extract articles: {result}")

if 'articles_df' in st.session_state:
    if st.button('Rank Articles'):
        id_list = st.session_state['articles_df']['id'].tolist()  # Use saved articles from session state
        rank_success, ranked_result = rank_articles(id_list)
        if rank_success:
            ranked_articles_df = pd.DataFrame(ranked_result)
            st.session_state['ranked_articles_df'] = ranked_articles_df  # Save ranked articles to session state
            # if "overall_similarity" in ranked_articles_df.columns:
            #     ranked_articles_df = ranked_articles_df.drop(columns=["overall_similarity"])
            ranked_articles_df = ranked_articles_df[['rank','score','is_relevant','date','content','text','source','link']]
            st.write("Ranked Articles:", ranked_articles_df)
        else:
            st.error(f"Failed to rank articles: {ranked_result}")
            
if 'articles_df' in st.session_state and 'ranked_articles_df' in st.session_state:
    ranked_articles_df = st.session_state['ranked_articles_df']  # Retrieve the ranked dataframe from the session state

    # Filter ranked_articles_df for articles where is_relevant is 1
    relevant_articles_df = st.session_state['ranked_articles_df'][st.session_state['ranked_articles_df']['is_relevant'] == 1]

    # Display a header for our pseudo-table and add a top border using markdown
    st.markdown("""
    ---
    #### Generate posts for relevant articles
    """, unsafe_allow_html=True)

    # Define consistent column widths for both headings and content rows
    column_widths = [1, 5, 5, 2]

    # Headings for the pseudo-table with HTML for center alignment and bold
    heading_cols = st.columns(column_widths)
    headings = ["Rank", "Article ID", "Content Snippet", "Action"]
    for heading_col, heading_text in zip(heading_cols, headings):
        heading_col.markdown(f"<p style='text-align: center; font-weight: bold;'>{heading_text}</p>", unsafe_allow_html=True)

    # Iterate through relevant_articles_df to create rows for our pseudo-table
    for i, row in relevant_articles_df.iterrows():
        article_id = row['id']
        rank = row['rank']
        content = row['content']
        
        # Create a set of columns for each row in our pseudo-table with consistent widths
        col1, col2, col3, col4 = st.columns(column_widths)
        
        # Display the rank, article ID, and content snippet
        col1.markdown(f"<p style='text-align: center;'>{int(rank)}</p>", unsafe_allow_html=True)
        col2.markdown(f"<p style='text-align: center;'>{article_id}</p>", unsafe_allow_html=True)
        col3.markdown(f"<p style='text-align: center;'>{content[:50]}...</p>", unsafe_allow_html=True)
        
        # Add a "Generate Post" button in the fourth column and handle its action
        if col4.button("Generate Post", key=f"gen_post_{article_id}"):
            success, generated_post = generate_post_for_article(article_id)
            if success:
                st.text_area(f"Generated Post for Article ID {article_id}", value=generated_post, height=300, key=f"post_{article_id}")
            else:
                st.error(f"Failed to generate post for Article ID {article_id}: {generated_post}")

    # Add a space after the ranked table
    st.markdown("---", unsafe_allow_html=True)