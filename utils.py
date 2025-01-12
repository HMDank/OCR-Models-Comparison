import easyocr
import io
import os
import time
import toml
import cloudinary
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

from io import BytesIO
import requests
from urllib.parse import urlparse
from google.cloud import vision
from google.cloud.vision_v1 import types

def load_selected_images():
    FOLDER_PATH = "selected_images"
    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
    image_list = [
        os.path.join(FOLDER_PATH, file)
        for file in os.listdir(FOLDER_PATH)
        if file.lower().endswith(IMAGE_EXTENSIONS)
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


def process_with_google(image):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "pacific-arcadia-445215-c0-084ebe89161e.json"
    client = vision.ImageAnnotatorClient()

    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    byte_array = io.BytesIO()
    image.save(byte_array, format=image.format if image.format else "PNG")
    byte_array = byte_array.getvalue()

    image = types.Image(content=byte_array)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Error in Vision API: {response.error.message}")

    texts = response.text_annotations
    result = texts[0].description.splitlines()

    return result


def process_image(method_list, inputs):
    def is_url(string):
        if isinstance(input, str):
            parsed = urlparse(string)
            return bool(parsed.scheme and parsed.netloc)
    
    results_df = pd.DataFrame() 
    
    if not inputs:
        return results_df
    
    for method in method_list:
        start_time = time.time()
        for input in inputs:
            if method == 'easyocr':
                reader = easyocr.Reader(['de', 'en'])
                if is_url(input):
                    response = requests.get(input)
                    input_image = image = Image.open(BytesIO(response.content))
                elif isinstance(input, str):
                    input_image = input
                    image = Image.open(input)
                elif isinstance(input, st.runtime.uploaded_file_manager.UploadedFile):
                    input_image = np.array(Image.open(input))
                    image = Image.open(input)
                result = reader.readtext(input_image, detail=0, paragraph=True)

            elif method == "google-cloud-api":
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'pacific-arcadia-445215-c0-084ebe89161e.json'
                if is_url(input):
                    response = requests.get(input)
                    input_image = image = Image.open(BytesIO(response.content))
                elif isinstance(input, str):
                    input_image = input
                    image = Image.open(input)
                elif isinstance(input, st.runtime.uploaded_file_manager.UploadedFile):
                    input_image = np.array(Image.open(input))
                    image = Image.fromarray(input_image)
                result = process_with_google(input_image)

        end_time = time.time()
        final_image = upload_image_to_cloudinary(image)
        temp_df = pd.DataFrame([{
            'Model': method,
            'Image': final_image,
            'Result': result,
            'Processing Time': round(end_time - start_time, 3)
        }])
        results_df = pd.concat([results_df, temp_df], ignore_index=True)
        
    return results_df
