import os
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter

# Paths
INPUT_FOLDER = "topics3"
OUTPUT_FOLDER = "topics4-styled"
LOGO_PATH = "logo.png"

# Load logo
logo = Image.open(LOGO_PATH).convert("RGBA")

# Settings
logo_scale = 0.15
logo_opacity = 0.6
text = "www.yooglee.com"
text_opacity = 230
text_font_size_ratio = 0.04
border_size = 12 

# Google color scheme (letters)
google_colors = [
    (66, 133, 244), (234, 67, 53), (251, 188, 5), (52, 168, 83),
    (66, 133, 244), (234, 67, 53), (251, 188, 5), (52, 168, 83),
]

ADD_OVERLAY = True
ADD_BLUR = False
ADD_BORDER = True
ADD_LOGO_GLOW = True
ADD_TEXT_SHADOW = True

try:
    FONT_PATH = "arial.ttf"
    font_default = ImageFont.truetype(FONT_PATH, size=40)
except:
    font_default = ImageFont.load_default()

# Validate image
def is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
            return img.width > 0 and img.height > 0
    except Exception:
        return False

def apply_logo_and_text(base_image):
    # Light blur
    if ADD_BLUR:
        base_image = base_image.filter(ImageFilter.GaussianBlur(radius=1))

    # Dark overlay
    if ADD_OVERLAY:
        overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 60))  # Darker
        base_image = Image.alpha_composite(base_image, overlay)

    # Add border
    if ADD_BORDER:
        new_size = (base_image.width + border_size * 2, base_image.height + border_size * 2)
        background = Image.new("RGBA", new_size, (25, 25, 25, 255))  # Even darker edge
        background.paste(base_image, (border_size, border_size))
        base_image = background

    width, height = base_image.size

    # Add Logo
    logo_width = int(width * logo_scale)
    aspect_ratio = logo.height / logo.width
    logo_resized = logo.resize((logo_width, int(logo_width * aspect_ratio)))

    alpha = logo_resized.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(logo_opacity)
    logo_resized.putalpha(alpha)

    logo_position = (width - logo_resized.width - 20 - border_size, height - logo_resized.height - 20 - border_size)

    # Logo glow
    if ADD_LOGO_GLOW:
        glow = logo_resized.filter(ImageFilter.GaussianBlur(radius=5))
        base_image.paste(glow, logo_position, glow)

    base_image.paste(logo_resized, logo_position, logo_resized)

    # Add Multicolor Text
    draw = ImageDraw.Draw(base_image)
    font_size = int(width * text_font_size_ratio)

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except:
        font = font_default

    text_position = (20 + border_size, height - font_size - 30 - border_size)
    x_offset = text_position[0]

    for idx, char in enumerate(text):
        color = google_colors[idx % len(google_colors)]
        rgba_color = color + (text_opacity,)
        bbox = draw.textbbox((x_offset, text_position[1]), char, font=font)

        if ADD_TEXT_SHADOW:
            shadow_color = (0, 0, 0, 140)
            draw.text((x_offset + 2, text_position[1] + 2), char, font=font, fill=shadow_color)

        if bbox[3] <= bbox[1]:
            continue
        draw.text((x_offset, text_position[1]), char, font=font, fill=rgba_color)
        x_offset += bbox[2] - bbox[0]

    return base_image

# Batch
def main():
    input_dir = Path(INPUT_FOLDER)
    output_dir = Path(OUTPUT_FOLDER)

    if not input_dir.exists():
        print(f"❌ Input folder not found: {INPUT_FOLDER}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for topic_folder in input_dir.iterdir():
        if topic_folder.is_dir():
            input_thumbnail = topic_folder / "thumbnail.webp"
            output_topic_folder = output_dir / topic_folder.name
            output_topic_folder.mkdir(parents=True, exist_ok=True)
            output_thumbnail = output_topic_folder / "thumbnail.webp"

            if input_thumbnail.exists():
                if is_valid_image(input_thumbnail):
                    try:
                        base_image = Image.open(input_thumbnail).convert("RGBA")
                        styled_image = apply_logo_and_text(base_image)
                        styled_image.convert("RGB").save(output_thumbnail, "WEBP", quality=90)
                        print(f"✅ Styled and saved: {output_thumbnail}")
                    except Exception as e:
                        print(f"❌ Error processing {input_thumbnail}: {e}")
                else:
                    print(f"⚠️ Skipped bad/corrupt image: {input_thumbnail}")
            else:
                print(f"⚠️ No thumbnail found in {topic_folder.name}, skipping.")

if __name__ == "__main__":
    main()
