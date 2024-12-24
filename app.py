import streamlit as st
import pandas as pd
from utils import process_image

st.set_page_config(
    page_title="Testing OCR Models",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('OCR Test', anchor=False)

results_df = pd.DataFrame(columns=['Preview Image', 'Result', 'Processing Time'])
if 'links' not in st.session_state:
    st.session_state["links"] = []

column1, column2, column3 = st.columns(3)
with column1:
    uploaded_images = st.file_uploader("Input image(s)", accept_multiple_files=True, type=['png', 'jpg'])
with column2:
    st.header("AND/OR", anchor=False)
with column3:
    link = st.text_input("URL of Image")
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        if st.button('Append Link', use_container_width=True):
            st.session_state["links"].append(link)
    with subcol2:
        if st.button('Clear', use_container_width=True):
            st.session_state["links"] = []
    if st.session_state["links"]:
        st.write(st.session_state["links"])
choices = st.multiselect('Select Models:', ['easyocr'])
if (uploaded_images or st.session_state["links"]) and choices :
    if st.button('Start Analysis', use_container_width=True):
        images_df = process_image(choices, uploaded_images)
        links_df = process_image(choices, st.session_state["links"])
        
        results_df = pd.concat([images_df, links_df], ignore_index=True)
        
        st.dataframe(
            results_df,
            column_order=("Image", "Result", "Processing Time"  ),
            column_config={
                "Image": st.column_config.ImageColumn(
                    "Preview Image", width='small'
                ),
                "Result": st.column_config.Column(
                    "Results",
                ),
                "Processing Time": st.column_config.NumberColumn(
                    "Processing Time",
                ),
            },
            hide_index=True,
            use_container_width=True
        )
