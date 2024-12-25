import easyocr
import glob
import io
import os
import time
import toml
import cloudinary
from cloudinary.uploader import upload
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from io import BytesIO
import requests
from urllib.parse import urlparse

def load_selected_images():
    folder_path = "selected_images"
    image_extensions = (".jpg", ".jpeg", ".png")
    image_list = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.lower().endswith(image_extensions)
    ]


    return image_list


def upload_image_to_cloudinary(pil_image):
    # Configure Cloudinary
    secrets = toml.load("secrets.toml")
    cloudinary_secrets = secrets["cloudinary"]

    cloudinary.config(
        cloud_name=cloudinary_secrets["cloud_name"],
        api_key=cloudinary_secrets["api_key"],
        api_secret=cloudinary_secrets["api_secret"]
    )
    
    # Convert PIL Image to Bytes
    image_bytes = io.BytesIO()
    pil_image.save(image_bytes, format="PNG")  # Save in PNG format (or specify another format)
    image_bytes.seek(0)

    # Upload to Cloudinary
    response = cloudinary.uploader.upload(
        image_bytes,
    )

    return response.get("secure_url")


def process_image(method_list, inputs):
    results_df = pd.DataFrame() 
    if not inputs:
        return results_df
    for method in method_list:
        start_time = time.time()
        
        if method == 'easyocr':
            reader = easyocr.Reader(['de', 'en'])
            def is_url(string):
                if isinstance(input, str):
                    parsed = urlparse(string)
                    return bool(parsed.scheme and parsed.netloc)
            for input in inputs:
                if is_url(input):
                    response = requests.get(input)
                    input_image = image = Image.open(BytesIO(response.content))
                elif isinstance(input, str):
                    input_image = input
                    image = Image.open(input)
                elif isinstance(input, st.runtime.uploaded_file_manager.UploadedFile):
                    input_image = np.array(Image.open(input))
                    image = Image.open(input)

                final_image = upload_image_to_cloudinary(image)
                result = reader.readtext(input_image, detail=0, paragraph=True)
                end_time = time.time()
                temp_df = pd.DataFrame([{
                    'Model': method,
                    'Image': final_image,
                    'Result': result,
                    'Processing Time': round(end_time - start_time, 3)
                }])
                results_df = pd.concat([results_df, temp_df], ignore_index=True)
        
        # if method == 
    return results_df