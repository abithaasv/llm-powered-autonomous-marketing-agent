import streamlit as st
import requests

# Common title for the entire app
st.title('Prompt Engineering App')

# Function to display the Summarize page
def summarize_page(model, temperature, max_tokens):
    st.header('Summarization task')

    prompt = st.text_input("Prompt")
    context = st.text_input("Content to summarize (input)")

    # Initialize session state for response text if it doesn't exist
    if 'response_text' not in st.session_state:
        st.session_state.response_text = ""

    if st.button('Summarize'):

        # Make API call
        response = requests.post("http://localhost:8000/gen/", json={
            "context": context, 
            "prompt": prompt, 
            "model": model.lower().replace(" ", ""),
            "temperature":temperature,
            "max_tokens":max_tokens
            })
        
        if response.status_code == 200:

            # Update session state with the new result
            st.session_state.response_text = response.json()["result"]

        else:
            st.error("Error in API Call")
            st.text_area("Result", value="API Response", height=100)
    
    # Display result using session state
    st.text_area("Result", value=st.session_state.response_text, height=100)

    # Display the download button only if there is a result to download
    if st.session_state.response_text:
        st.download_button(
            label="Download response",
            data=st.session_state.response_text,
            file_name="response.txt",
            mime="text/plain"
        )


# Function to display the Semantic Comparison page
def semantic_comparison_page():
    st.header('Semantic Comparison task')

    article_summary = st.text_area("Text 1")
    pg_summary = st.text_area("Text 2")

    if st.button('Compare'):
        # Make API call
        response = requests.post("http://localhost:8000/compare/", json={
            # "baseline_text": baseline_text, 
            "summary1": pg_summary, 
            "summary2": article_summary, 
            })
        
        if response.status_code == 200:
            # Display result
            result = response.json()["result"]
            # st.text_area("Semantic similarity score", value=result, height=100)
            st.markdown(f"## Result \n\nSemantic similarity score : {result}")
        else:
            st.error("Error in API Call")

# Function to display the Postgen page
def postgen_page(model, temperature, max_tokens):
    st.header('Post Generation Task')

    prompt = st.text_input("Prompt")
    pg_summary = st.text_input("Company Summary (input)")
    article_summary = st.text_area("Article Summary (input)")

    context = f"""Prediction Guard Summary :
    {pg_summary}

    Article Summary : 
    {article_summary}
    """


    if st.button('Generate'):
        # Make API call
        response = requests.post("http://localhost:8000/gen/", json={
            "context": context, 
            "prompt": prompt, 
            "model": model.lower().replace(" ", ""),
            "temperature":temperature,
            "max_tokens":max_tokens
            })
        
        if response.status_code == 200:
            # Display result
            result = response.json()["result"]
            st.text_area("Generated post", value=result, height=100)
        else:
            st.error("Error in API Call")

# Sidebar navigation
page = st.sidebar.selectbox("Select Task", ["Summarize", "Semantic Comparison", "Postgen"])

model = st.sidebar.selectbox("Select Model", options=["Nous Hermes", "Neural Chat"], index=0)
temperature = st.sidebar.number_input("Global Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
max_tokens = st.sidebar.number_input("Max Tokens", min_value=0, max_value=10000, value=200, step=1)


if page == "Summarize":
    summarize_page(model, temperature, max_tokens)
elif page == "Semantic Comparison":
    semantic_comparison_page()
elif page == "Postgen":
    postgen_page(model, temperature, max_tokens)
