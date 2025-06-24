import streamlit as st

from session.state_manager import init_session_state

st.set_page_config(
    page_title="DSF Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()


st.title("Welcome to the Differential Scanning Fluorimetry (DSF) Analysis Tool")
st.markdown("""
This application helps you analyze Differential Scanning Fluorimetry (DSF) data.

Please navigate through the pages using the sidebar:
1. 📊 Upload Data - Select file format and upload your data
2. 🎯 Control Analysis - Select and analyze control wells
3. 📐 Detect Atypical Wells - Detect wells that differ in shape from the control wells 
(e.g. empty wells)
4. 🔍 Well Analysis - Analyze samples and calculate ΔTm values
5. 🗺️ Summary and Data Download - Visualize ΔTm values on a heatmap and download your data
""")
# 5. 👀 Well Review - Review the results of the well analysis
st.markdown("---")

st.markdown("""
For bug reports or feature requests, please navigate to:  
* [bada (backend)](https://github.com/willigott/biophysical-assay-data-analysis) or
* [dsf-viewer (frontend, this app)](https://github.com/willigott/dsf-viewer)  

and create an issue.
""")
