import streamlit as st
import pandas as pd
import os
from utils import process_image, load_selected_images

st.set_page_config(
    page_title="Testing OCR Models",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('OCR Test', anchor=False)

@st.cache_data
def get_selected_images():
    return load_selected_images()

results_df = pd.DataFrame(columns=['Model', 'Preview Image', 'Result', 'Processing Time'])
if 'links' not in st.session_state:
    st.session_state["links"] = []

column1, column2, column3 = st.columns(3)
with column1:
    uploaded_images = st.file_uploader("Input image(s)", accept_multiple_files=True, type=['png', 'jpg'])
with column2:
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
with column3:
    checked = st.checkbox("Use selected Data (Pictures taken by Dank himself :>)")
    image_list = get_selected_images() if checked else []
choices = st.multiselect('Select Models:', ['easyocr', 'google-cloud-api'])
if (uploaded_images or st.session_state["links"] or checked) and choices :
    if st.button('Start Analysis', use_container_width=True):
        images_df = process_image(choices, uploaded_images)
        links_df = process_image(choices, st.session_state["links"])
        selected_df = process_image(choices, image_list)
        results_df = pd.concat([images_df, links_df, selected_df], ignore_index=True)
        
        st.dataframe(
            results_df,
            column_order=("Model", "Image", "Result", "Processing Time"  ),
            column_config={
                "Model": st.column_config.Column(
                    "Model", width='small'
                ),
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
