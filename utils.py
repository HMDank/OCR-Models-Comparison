import easyocr
import glob
import io
import os
import time
import toml
import cloudinary
from cloudinary.uploader import upload

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


def process_image(method, image_file):
    start_time = time.time()
    if method == 'easyocr':
        reader = easyocr.Reader(['de'])
        result = reader.readtext(image_file, detail=0)
        text = ' '.join(result)
        words = text.split()
        chunks = [' '.join(words[i:i+5]) for i in range(0, len(words), 5)]
        result = '\n'.join(chunks) + '\n\n'

    end_time = time.time()
    total_time = round(end_time - start_time, 3)
    return result, total_time