import subprocess
subprocess.run(["playwright", "install", "chromium"])
import streamlit as st
from summarizer import research_company

st.title("Company Research Assistant")
company_url = st.text_input("Enter a company URL to get started:")


@st.cache_data(show_spinner=False)
def cached_research(url):
    return research_company(url)


if st.button("Research this company"):
    if not company_url:
        st.warning("Please enter a URL first.")
    else:
        cleaned_url = company_url.strip()
        with st.spinner("Researching..."):
            company_info = cached_research(cleaned_url)
        st.markdown(company_info)