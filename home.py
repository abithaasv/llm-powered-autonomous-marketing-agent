import streamlit as st

# Streamlit Styling
#-------------------
# Set the gradient background color
gradient_bg = "linear-gradient(135deg, #009959, #000000)"  # Gradient from light blue to dark blue

# Define the green color for the hyperlink
green_color = "#009959"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: #000000;
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #FFFFFF;  /* White text color for better contrast */
        }}
        .sidebar .sidebar-content {{
           background-image: {gradient_bg} !important;  /* Semi-transparent dark blue for the sidebar */
        }}
        
        footer {{visibility: hidden;}} /* Hide the footer */
        h1 {{
            color: #009959;  /* Gold color for the main title */
        }}
        a {{
            color: {green_color} !important;
            text-decoration: none !important;
        }}
        a:hover {{
            color: {green_color} !important;
            text-decoration: underline !important;
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Page Content
#-------------------

st.title("LLM Marketing Agent")
st.markdown("""
Welcome to the LLM Marketing Agent app, your go-to solution for leveraging AI in your marketing efforts. 
Explore, generate, and rank compelling content effortlessly.

[Explore Prediction Guard →](https://www.predictionguard.com/)
""", unsafe_allow_html=True)

# Using columns to add visual elements or additional info
col1, col2 = st.columns(2)

# Define the columns
col1, col2 = st.columns(2)

# Column for the image
with col1:
    st.image("/Users/abithaashreevenkatesh/Desktop/aiimage.png", width=300)

# Column for the markdown text
with col2:
    st.markdown("""
    ## Why LLM Marketing Agent?
    - **Enhance your content** with AI-driven insights.
    - **Save time** by automating content generation and ranking.
    - **Stay ahead** of the marketing curve by leveraging the latest in AI technology.
    """)

# Footer
st.markdown("""
---
Developed by Team 8.
""", unsafe_allow_html=True)