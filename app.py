import streamlit as st
import pandas as pd
import io
from utils import process_image, upload_image_to_cloudinary
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Testing OCR Models",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('OCR Test', anchor=False)

results_df = pd.DataFrame(columns=['Preview Image', 'Result', 'Processing Time'])

column1, column2 = st.columns(2)
with column1:
    uploaded_images = st.file_uploader("Input image(s)", accept_multiple_files=True, type=['png', 'jpg'])
with column2:
    link = st.text_input("URL of Image")
choices = st.multiselect('Select Models:', ['easyocr'])
if uploaded_images and choices:
    if st.button('Start Analysis'):
        for image in uploaded_images:
            np_image = np.array(Image.open(image))
            result, time = process_image('easyocr', np_image)
            final_image = upload_image_to_cloudinary(Image.open(image))
            temp_df = pd.DataFrame([{
                'Image': final_image,
                'Result': result,
                'Processing Time': time
            }])
            results_df = pd.concat([results_df, temp_df], ignore_index=True)

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

# folder = input_folder_path
# image_files = glob.glob(os.path.join(folder, '*.jpg'))
# for image_file in image_files:
#     run_tests("input", "output.txt")