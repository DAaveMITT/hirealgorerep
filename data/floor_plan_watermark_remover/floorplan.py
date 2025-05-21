#Modify and remove/replace image (floorplan) watermark

from PIL import Image, ImageDraw, ImageFont

def modify_image(image_path, output_path, new_text):
    try:
        img = Image.open(image_path)

        if img.mode != 'RGB':
            img = img.convert('RGB')
        print(f"Opened and converted image (if necessary): {image_path}")

        draw = ImageDraw.Draw(img)

        # Define the area to remove the old logo and website (refined coordinates)
        img_width, img_height = img.size
        print(f"Image size: {img_width}x{img_height}")

        # Adjust coordinates based on the size of the image
        rect_x1 = 0
        rect_y1 = img_height - 180
        rect_x2 = img_width
        rect_y2 = img_height
        draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill="white")
        print(f"Covered the bottom of the image: {[rect_x1, rect_y1, rect_x2, rect_y2]}")

        # Add new text in the area where the old logo was
        text_position = (rect_x1 + 50, rect_y1 + 40)
        font_path = "arial.ttf" 
        font = ImageFont.truetype(font_path, 36)
        draw.text(text_position, new_text, fill="black", font=font)
        print(f"Added new text: {new_text} at {text_position}")

        # Save the modified image
        img.save(output_path)
        print(f"Image saved to {output_path}")

    except Exception as e:
        print(f"Error processing image: {e}")

# Example usage
input_image = "floor2.jpg"
output_image = "modified_floor3.png"
new_text = "BusConnect Direct | www.BusConnectDirect.com"

modify_image(input_image, output_image, new_text)
