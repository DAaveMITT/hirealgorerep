import os
import pandas as pd
from datetime import datetime
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
from PIL import Image
import logging
import random
import re

# Logging
logging.basicConfig(
    filename="image_generation_yooglee.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

EXCEL_FILE = "again.xlsx"
OUTPUT_BASE = "topics3"
BASE_MODEL_PATH = r"C:\HuggingFace_MAIN\stable-diffusion-xl-base-1.0"
VAE_MODEL_PATH = r"C:\HuggingFace_MAIN\sdxl-vae"

if not torch.cuda.is_available():
    raise EnvironmentError("CUDA is not available.")

device = "cuda"

vae = AutoencoderKL.from_pretrained(VAE_MODEL_PATH, torch_dtype=torch.float16)

image_pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.float16,
    vae=vae
).to(device)
image_pipe.enable_attention_slicing()

# Prompts
def build_prompt(keyword, keywords):
    templates = [
        f"Editorial photo for an article about {keyword}. Concepts: {', '.join(keywords)}. "
        "Sharp focus, realistic lighting, high resolution, professional photojournalism.",

        f"Professional web article image showing the topic of {keyword}. Key ideas: {', '.join(keywords)}. "
        "Clean composition, high detail, 4k editorial photography.",

        f"Realistic digital photo illustration for the topic: {keyword}. Featuring: {', '.join(keywords)}. "
        "Modern, news-style, sharp focus, ambient light."
    ]
    return random.choice(templates)

def safe_slug(slug, max_length=100):
    slug = re.sub(r'[<>:"/\\|?*]', '', slug)  # Remove invalid characters
    return slug[:max_length]  # Truncate to max length

# Image Generation
def generate_topic_image(prompt, output_path):
    try:
        logging.info(f"🎨 Generating image for prompt: {prompt}")
        negative_prompt = (
            "blurry, low quality, cartoon, surreal, ugly, distorted, extra fingers, text, watermark"
        )

        image = image_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=8.0,
            width=1280,
            height=720
        ).images[0]

        image.save(output_path, "WEBP")
        logging.info(f"✅ Saved image: {output_path}")
    except Exception as e:
        logging.error(f"❌ Image generation failed for prompt [{prompt}]: {e}")

# Load Spreadsheet
df = pd.read_excel(EXCEL_FILE)
df = df.dropna(subset=["slug", "Keyword", "meta_keywords"])

# Generate Images
for _, row in df.iterrows():
    original_slug = str(row["slug"]).strip()
    slug = safe_slug(original_slug)

    keyword = str(row["Keyword"]).strip()
    keywords = [k.strip() for k in str(row["meta_keywords"]).split("\n") if k.strip()]
    prompt = build_prompt(keyword, keywords)

    output_dir = os.path.join(OUTPUT_BASE, slug)

    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        logging.warning(f"⚠️ Skipping slug '{slug}' due to folder creation error: {e}")
        print(f"⚠️ Skipping slug '{slug}' due to folder creation error: {e}")
        continue

    output_path = os.path.join(output_dir, "thumbnail.webp")
    generate_topic_image(prompt, output_path)

print("✅ All topic images generated and saved.")
