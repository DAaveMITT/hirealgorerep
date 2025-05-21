
import openai
import pandas as pd
import os
import time

api_tokens = [
    "openai-api-key", 
    "openai-api-key",
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
    "openai-api-key", 
]

api_key_index = 0


def update_api_key():
    global api_key_index
    openai.api_key = api_tokens[api_key_index]
    api_key_index = (api_key_index + 1) % len(api_tokens)
update_api_key()


input_file = "run2.xlsx"
output_folder = "batches"
combined_output_file = "structured_content_output_combined.xlsx" 

# Create the batches folder
os.makedirs(output_folder, exist_ok=True)

# Load keywords and parent keywords from the provided Excel file
df = pd.read_excel(input_file)

# Define the prompts for each content field
prompts = {
    "meta_title": "Generate a meta title for the topic '{keyword}'.",
    "meta_description": "Generate a meta description for the topic '{keyword}'.",
    "meta_keywords": "Generate a list of SEO keywords for the topic '{keyword}'.",
    "meta_og_title": "Generate a meta Open Graph title for the topic '{keyword}'.",
    "meta_og_description": "Generate a meta Open Graph description for the topic '{keyword}'.",
    "h1": "Provide a heading (H1) for the topic '{keyword}'.",
    "h2": "Provide a subheading (H2) for the topic '{keyword}'.",
    "h3": "Provide an H3 subheading for the topic '{keyword}'.",
    "Content_Intro": "Write an introductory paragraph for the topic '{keyword}'.",
    "Content_Main": "Write the main content section for the topic '{keyword}'.",
    "Content_Benefits": "List some benefits related to the topic '{keyword}'.",
    "How-To": "Provide a how-to guide for the topic '{keyword}'.",
    "FAQ": "List one frequently asked question about '{keyword}' and provide an answer.",
    "Related_Topics": "Suggest some related topics to '{keyword}'.",
    "Conclusion": "Write a conclusion paragraph for the topic '{keyword}'."
}

# Helper function
def generate_content(keyword, prompt_template):
    prompt = prompt_template.format(keyword=keyword)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)  # Wait before retrying
        update_api_key()  # Rotate API key on error
        return generate_content(keyword, prompt_template)  # Retry

# Initialize a list to hold the generated content data
structured_data = []

# Batch size and start row for resuming (set to 0 to start from the beginning)
batch_size = 100
start_row = 0

# Process each row in the input DataFrame
for idx, row in df.iterrows():
    if idx < start_row:
        continue  # Skip rows until start_row

    keyword = row["Keyword"]
    parent_keyword = row["Parent Keyword"]
    content = {"Keyword": keyword, "Parent Keyword": parent_keyword}
    
    # Generate content
    for field, prompt_template in prompts.items():
        content[field] = generate_content(keyword, prompt_template)
    
    structured_data.append(content)
    
    # Save progress in batches
    if (idx + 1) % batch_size == 0:
        # Convert to DataFrame and save to a batch file
        batch_df = pd.DataFrame(structured_data)
        batch_file = os.path.join(output_folder, f"batch_{idx + 1}.xlsx")
        batch_df.to_excel(batch_file, index=False)
        print(f"Saved batch up to row {idx + 1} to {batch_file}")
        structured_data = []  # Clear structured data after saving

# Save any remaining data in the last batch
if structured_data:
    batch_df = pd.DataFrame(structured_data)
    batch_file = os.path.join(output_folder, f"batch_final.xlsx")
    batch_df.to_excel(batch_file, index=False)
    print(f"Final batch saved to {batch_file}")

# Combine all batch files into one final output
all_batches = [pd.read_excel(os.path.join(output_folder, f)) for f in os.listdir(output_folder) if f.endswith('.xlsx')]
combined_df = pd.concat(all_batches, ignore_index=True)
combined_df.to_excel(combined_output_file, index=False)

print(f"All batches have been combined into {combined_output_file}")
