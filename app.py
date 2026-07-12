import streamlit as st
from summarizer import research_company


st.title("Company Research Assistant")
company_url = st.text_input("Enter a company URL to get started:")


if st.button("Research this company"):
    if not company_url:
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("Researching..."):
            company_info = research_company(company_url)
        st.markdown(company_info)
