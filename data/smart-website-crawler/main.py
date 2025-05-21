import json
import os
import time
import torch
import logging
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from diffusers import StableDiffusionXLPipeline
from tqdm import tqdm

# Configure Logging
logging.basicConfig(filename="text_generate.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Model Paths
TEXT_MODEL_PATH = r"C:\Users\15162\Desktop\HuggingFace_MAIN\falcon-7b-instruct"
IMAGE_MODEL_PATH = r"C:\Users\15162\Desktop\HuggingFace_MAIN\stable-diffusion-xl-base-1.0"

# Directories
DATA_DIR = "data"
ARCHIVE_DIR = "data/archive"
ARTICLE_OUTPUT_DIR = "RegeneratedArticles"
IMAGE_OUTPUT_DIR = "GeneratedImages"

os.makedirs(ARTICLE_OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

print(f"📂 Output directories confirmed.")
logging.info(f"📂 Output directories confirmed.")

# Load Models
try:
    if not torch.cuda.is_available():
        raise RuntimeError("❌ CUDA not available. Check GPU setup!")
    device = "cuda"
    print("✅ CUDA detected.")

    # Verify CUDA version and PyTorch compatibility
    print(f"PyTorch CUDA version: {torch.version.cuda}")
    print(f"Current CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"Number of CUDA devices: {torch.cuda.device_count()}")

    # Check initial VRAM state
    print(f"Initial VRAM allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB")
    print(f"Initial VRAM reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MiB")

    # Text Model
    tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL_PATH)
    tokenizer.pad_token = tokenizer.eos_token  # Fix padding

    # Use "auto" for device_map to handle VRAM limits (12GB on RTX 4070Ti may not fit Falcon-7B fully)
    text_model = AutoModelForCausalLM.from_pretrained(
     TEXT_MODEL_PATH, 
        torch_dtype=torch.float16,  # Use float16 for lower VRAM
        device_map="auto"
)
    # No .to(device) here—device_map handles placement
    print(f"Text model device map: {text_model.hf_device_map}")  # Use hf_device_map for transformers

    # Check VRAM after loading text model
    print(f"VRAM allocated after text model: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB")
    print(f"VRAM reserved after text model: {torch.cuda.memory_reserved() / 1024**2:.2f} MiB")

    # Clear GPU memory before loading image pipeline to free up VRAM
    torch.cuda.empty_cache()
    print(f"VRAM allocated after clearing cache before image model: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB")

    # Image Model
    print("Loading Stable Diffusion XL pipeline...")
    image_pipe = StableDiffusionXLPipeline.from_pretrained(
    IMAGE_MODEL_PATH, 
    torch_dtype=torch.float16,
)
    image_pipe.to(device)
    image_pipe.enable_attention_slicing()  # Slice attention layers to reduce VRAM
    image_pipe.enable_model_cpu_offload()  # Offload non-GPU components

    # Check VRAM after loading both models
    print(f"VRAM allocated after image model: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB")
    print(f"VRAM reserved after image model: {torch.cuda.memory_reserved() / 1024**2:.2f} MiB")

    # Clear any cached memory to ensure accurate usage
    torch.cuda.empty_cache()
    print(f"VRAM allocated after clearing cache: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB")

    # Reduce memory usage for SDXL if necessary
    image_pipe.enable_model_cpu_offload()  # Offload non-GPU components to CPU to save VRAM

except Exception as e:
    logging.error(f"❌ Model loading failed: {e}")
    print(f"❌ Model loading error: {e}")
    raise

def generate_unique_article(article):
    if "headline" not in article or "content" not in article:
        logging.error(f"❌ Missing 'headline' or 'content' in article: {article}")
        return None, None

    prompt = f"""
    You're a professional journalist. Rewrite the article below to be unique:
    
    **Original Article:**
    Headline: {article["headline"]}
    Content: {article["content"][:500]}  # Further reduce content to 500 chars

    **Rewrite:**
    """

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256).to(device)  # Reduce max_length further
        print("🔧 Rewriting article...")
        logging.info(f"Starting text generation with input length: {len(prompt)} chars")

        max_new_tokens = 150
        with tqdm(total=max_new_tokens, desc="Generating text", unit="token") as pbar:
            output = text_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.25,
                top_p=0.85,
                repetition_penalty=1.25,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,  # Ensure end-of-sequence token is set
            )

            # Update progress incrementally based on output length
            generated_tokens = output.shape[-1] - inputs["input_ids"].shape[-1]
            if generated_tokens > 0:
                pbar.update(generated_tokens)
            else:
                logging.warning("⚠️ No new tokens generated.")

        generated_text = tokenizer.decode(output[0], skip_special_tokens=True).strip()
        if "**Rewrite:**" in generated_text:
            generated_text = generated_text.split("**Rewrite:**")[-1].strip()
        else:
            logging.warning("⚠️ Rewrite section not found in output. Full output: " + generated_text)
            generated_text = generated_text  # Fallback to full output if rewrite section not found
       
        image_prompt = f"""
        Highly detailed, futuristic artwork depicting '{article["headline"]}'. 
        Featuring elements of blockchain, cryptocurrency, financial leaders, and AI.
        Hyper-realistic, cinematic lighting, ultra-detailed, 4K resolution.
        """
        return generated_text, image_prompt
    except Exception as e:
        logging.error(f"❌ Text generation failed: {e}")
        print(f"❌ Text generation error: {e}")
        return None, None

def generate_image(image_prompt, image_filename):
    """Generates an AI image with a progress bar."""
    print(f"🎨 Generating image: {image_filename}")
    logging.info(f"🎨 Generating image: {image_filename}")
    try:
        with tqdm(total=50, desc="Generating image", unit="step") as pbar:
            def update_progress_bar(pipeline, step, timestep, callback_kwargs):
                pbar.update(1)
                return callback_kwargs
            image = image_pipe(
                image_prompt,
                num_inference_steps=20,
                callback_on_step_end=update_progress_bar
            ).images[0]
        
        image_path = os.path.join(IMAGE_OUTPUT_DIR, image_filename)
        image.save(image_path)
        print(f"✅ Image saved: {image_path}")
        logging.info(f"✅ Image saved: {image_path}")
    except Exception as e:
        logging.error(f"❌ Image generation failed: {e}")
        print(f"❌ Image generation error: {e}")

def process_new_files():
    """Continuously watches for new scraped articles and processes them."""
    while True:
        try:
            files = [f for f in os.listdir(DATA_DIR) if f.startswith("scraped_") and f.endswith(".json")]
            if not files:
                print("🔍 No new files found. Checking again in 10 seconds...")
                time.sleep(10)
                continue

            for file in files:
                input_path = os.path.join(DATA_DIR, file)
                archive_path = os.path.join(ARCHIVE_DIR, file)

                print(f"✍️ Processing {file}...")
                logging.info(f"✍️ Processing {file}...")

                # Read and validate JSON file
                try:
                    with open(input_path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    
                    # Handle different possible structures
                    if isinstance(content, dict):
                        articles = [content]  # Single article as a dict
                    elif isinstance(content, list):
                        articles = content  # List of articles
                    else:
                        logging.error(f"❌ Invalid JSON structure in {file}: expected dict or list, got {type(content)}")
                        continue  # Skip this file

                except json.JSONDecodeError as e:
                    logging.error(f"❌ Failed to parse JSON in {file}: {e}")
                    continue  # Skip malformed JSON

                # Process valid articles
                for index, article in enumerate(articles, start=1):
                    if not isinstance(article, dict):
                        logging.warning(f"⚠️ Skipping invalid article in {file} (index {index}): expected dict, got {type(article)}")
                        continue
                    
                    print(f"🔄 Rewriting article {index}/{len(articles)}: {article.get('headline', 'Unknown')}")
                    rewritten_text, ai_prompt = generate_unique_article(article)
                    
                    if not rewritten_text or len(rewritten_text) < 100:
                        logging.warning(f"⚠️ Skipping article: Insufficient rewrite length.")
                        continue
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"generated_{timestamp}_{index}.png"
                    article_filename = f"reworded_{timestamp}_{index}.json"
                    article_path = os.path.join(ARTICLE_OUTPUT_DIR, article_filename)

                    with open(article_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "headline": rewritten_text.split("\n")[0],
                            "url": article.get("url", "N/A"),
                            "source": article.get("source", "N/A"),
                            "content": rewritten_text,
                            "image_prompt": ai_prompt,
                            "image_filename": image_filename
                        }, f, indent=4)
                    
                    print(f"✅ Article saved: {article_path}")
                    
                    print(f"Would you like to generate an image for '{article.get('headline', 'Unknown')}'? (y/n)")
                    if input().lower() == 'y':
                        generate_image(ai_prompt, image_filename)
                
                os.rename(input_path, archive_path)
                print(f"📂 Moved to archive: {archive_path}")
        
        except Exception as e:
            logging.error(f"❌ Error in main loop: {e}")
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    process_new_files()