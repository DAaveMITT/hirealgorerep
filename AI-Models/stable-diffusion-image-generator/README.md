# Stable Diffusion Image Generator

This script uses the Stable Diffusion XL pipeline to generate high-quality images based on keyword data provided in an Excel sheet. It's designed to help automate the creation of image assets for SEO pages, blogs, or other use cases where unique visual content is needed.

## How It Works

The script reads a list of topics from an Excel file, constructs a prompt for each based on a mix of primary and secondary keywords, and uses the Stable Diffusion model (via Hugging Face's diffusers library) to generate a realistic image. Each image is saved as a `.webp` file in a dedicated folder for its respective topic.

## Requirements

- Python 3.10+
- CUDA-compatible GPU
- The following Python packages:
  - `torch`
  - `diffusers`
  - `transformers`
  - `pandas`
  - `Pillow` (PIL)
  - `openpyxl` (if you're using `.xlsx`)
  - `logging`

## Folder Structure
├── again.xlsx # example data
├── templates/ # Optional folder for prompts or HTML/TSX templates
├── topics3/ # Output directory where generated images are saved
├── stable_diffusion_image_generator.py

## Excel File Format (`again.xlsx`)

This file should include at least these three columns:

- `slug` – used for naming folders
- `Keyword` – primary keyword or topic
- `meta_keywords` – secondary keywords (newline-separated)

## Model Setup

This assumes you have downloaded:

- `stable-diffusion-xl-base-1.0`  
- `sdxl-vae`

Update the `BASE_MODEL_PATH` and `VAE_MODEL_PATH` at the top of the script to match your local paths.

## Running the Script

1. Activate your virtual environment.
2. Install any missing dependencies with `pip install -r requirements.txt` (create one if needed).
3. Run the script:
   ```bash
   python stable_diffusion_image_generator.py
