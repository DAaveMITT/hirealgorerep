import pandas as pd
import re
import os
import json

# Paths
input_file = "combined_batches2.xlsx"
output_directory = "typescript_pages_output"
output_excel_file = "generated_content_backup.xlsx"
metadata_output_file = "title-metadata.json"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Load content from the generated output file
df = pd.read_excel(input_file)

# Template with hardcoded radio button layout for links
template = """
import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

const [[ComponentName]]: React.FC = () => {
    const [mounted, setMounted] = useState(false);
    const router = useRouter();

    useEffect(() => {
      setMounted(true);
    }, []);

    const canonicalUrl = mounted
      ? `${process.env.NEXT_PUBLIC_SITE_URL}${router.asPath}`
      : '';

    return (
      <>
        <Head>
          <title>[[meta_title]]</title>
          <meta name="description" content="[[meta_description]]" />
          <meta name="keywords" content="[[meta_keywords]]" />
          <meta name="robots" content="index, follow" />
          <meta property="og:description" content="[[meta_og_description]]" />
          <meta property="og:image" content="/assets/bg3.webp" />
          <meta property="og:url" content="https://www.reliancewebdevelopment.com/" />
          {mounted && <link rel="canonical" href={canonicalUrl} />}
        </Head>

        <section className="bg-gray-900 text-white py-10 sm:py-16">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-red-500 text-center p-6 rounded-lg shadow-lg mb-10">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white">
                [[meta_title]]
              </h1>
            </div>

            <div className="text-center mb-10 sm:mb-16">
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-red-400 mb-4 pt-10 sm:mb-6">
                [[h1]]
              </h2>
              <p className="text-base sm:text-lg lg:text-xl text-gray-300 max-w-xl sm:max-w-2xl mx-auto">
                [[h2]]
              </p>
            </div>

            <div className="space-y-10 mb-10 pt-10 sm:mb-16">
              <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-red-400 mb-2">Introduction</h3>
                <p className="text-gray-300 text-sm sm:text-base">
                  [[Content_Intro]]
                </p>
              </div>
              <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-red-400 mb-2">Main</h3>
                <p className="text-gray-300 text-sm sm:text-base">
                  [[Content_Main]]
                </p>
              </div>
              <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-red-400 mb-2">Benefits</h3>
                <div className="text-gray-300 text-sm sm:text-base space-y-4">
                  [[Content_Benefits]]
                </div>
              </div>
            </div>

            <div className="text-center mb-10 pt-10 sm:mb-16">
              <h3 className="text-2xl sm:text-3xl font-semibold text-red-400 mb-6">
                How-To Guide
              </h3>
              <div className="text-gray-300 max-w-xl mx-auto space-y-4">
                [[How-To]]
              </div>
            </div>

            <div className="p-6 pt-10 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-red-400 mb-2">Related Topics</h3>
                <p className="text-gray-300 text-sm sm:text-base">
                  [[h3]]
                </p>
              </div>

           <div className="text-center mb-10 pt-10 sm:mb-16">
              <h3 className="text-2xl sm:text-3xl font-semibold text-red-400 mb-6">
                Frequently Asked Questions
              </h3>
              <div className="text-gray-300 max-w-xl mx-auto space-y-4">
                [[FAQ]]
              </div>
            </div>
          </div>
        </section>
      </>
    );
};

export default [[ComponentName]];
"""

def clean_how_to(how_to):
    if pd.isna(how_to):
        return ''
    
    steps = re.split(r'\d+\.\s+', how_to)
    
    sanitized_steps = []
    for step in steps:
        # Remove characters
        sanitized_step = re.sub(r'[<>\[\]{}()*&^%$#@!~`]', '', step).strip()
        if sanitized_step:
            sanitized_steps.append(sanitized_step)
    
    
    return '\n'.join([
        f'<div className="bg-gray-800 p-4 sm:p-6 rounded-lg shadow-lg mb-4 text-gray-300 text-sm sm:text-base leading-relaxed">{sanitized_step}</div>'
        for sanitized_step in sanitized_steps
    ])
    
def remove_quotes(text):
    if pd.isna(text):
        return ''
    return text.replace('"', '').replace("'", "").strip()

def clean_output(text):
    if pd.isna(text):
        return ''
    return re.sub(r'\s+', ' ', text).strip()

def clean_keywords(keywords):
    if pd.isna(keywords):
        return ''
    keywords_list = re.split(r'[\n\-]', str(keywords).strip())
    cleaned_keywords = [re.sub(r'^\d+\.\s*', '', kw).strip() for kw in keywords_list if kw.strip()]
    return ', '.join(cleaned_keywords)

def clean_benefits(content_benefits):
    if pd.isna(content_benefits):
        return ''
    benefits = re.split(r'\d+\.\s+', content_benefits)
    benefits = [benefit.strip() for benefit in benefits if benefit.strip()]
    return '\n'.join([f'<div className="bg-gray-800 p-4 sm:p-6 rounded-lg shadow-lg mb-4 text-gray-300 text-sm sm:text-base leading-relaxed">{benefit}</div>' for benefit in benefits])

def clean_faq(faq):
    if pd.isna(faq):
        return ''
    faqs = re.split(r'(Q\d+\.\s+)', faq)
    faq_pairs = [faqs[i] + faqs[i + 1] for i in range(1, len(faqs) - 1, 2)]
    faq_content = '\n'.join([f'<div className="bg-gray-800 p-4 sm:p-6 rounded-lg shadow-lg mb-4 text-gray-300 text-sm sm:text-base leading-relaxed">{item}</div>' for item in faq_pairs])
    print("FAQ Content Processed:", faq_content)  # Debugging
    return faq_content

def sanitize_text(text):
    if pd.isna(text):
        return ''
    return text.replace('"', "'").strip()

def to_camel_case(slug):
    words = slug.split(' ')
    return ''.join(word.capitalize() for word in words)

title_metadata = {}

excel_data = []
for idx, row in df.iterrows():
    content_dict = row.to_dict()
    meta_title = str(content_dict.get('Keyword', ''))
    raw_slug = str(content_dict.get('slug', ''))
    slug = to_camel_case(raw_slug)  # Camel case
    meta_title = str(content_dict.get('Keyword', ''))
    filename = '-'.join(word.capitalize() for word in raw_slug.split(' '))  
    placeholders = {
        'ComponentName': slug,
        'meta_title': meta_title,
        'meta_description': sanitize_text(content_dict.get('meta_description', '')),
        'meta_og_description': sanitize_text(content_dict.get('meta_og_description', '')),
        'meta_og_title': str(content_dict.get('meta_og_title', '')),
        'meta_keywords': clean_keywords(content_dict.get('meta_keywords', '')),
        'h1': str(content_dict.get('h1', '')),
        'h2': str(content_dict.get('h2', '')),
        'h3': str(content_dict.get('h3', '')),
        'Content_Intro': clean_output(content_dict.get('Content_Intro', '')),
        'Content_Main': clean_output(content_dict.get('Content_Main', '')),
        'Content_Benefits': clean_benefits(content_dict.get('Content_Benefits', '')),
        'How-To': clean_how_to(content_dict.get('How-To', '')),
        'FAQ': (content_dict.get('FAQ', '')),  # Process FAQ content
        'Conclusion': clean_output(content_dict.get('Conclusion', '')),
        'Related_Topics': clean_output(content_dict.get('Related_Topics', '')),
    }

    print(f"Generating file for {slug}: FAQ Content -> {placeholders['FAQ']}")

    # Replace
    typescript_code = template
    for placeholder, value in placeholders.items():
        typescript_code = typescript_code.replace(f"[[{placeholder}]]", value)

    # Save
    file_path = os.path.join(output_directory, f"{filename}.tsx")
    with open(file_path, 'w', encoding='utf-8') as tsx_file:
        tsx_file.write(typescript_code)

    title_metadata[slug] = meta_title

    excel_data.append({
        "Component Name": slug,
        "Keyword": meta_title,
        "Generated Code": typescript_code
    })

with open(metadata_output_file, 'w', encoding='utf-8') as json_file:
    json.dump(title_metadata, json_file, indent=4)

excel_df = pd.DataFrame(excel_data)
excel_df.to_excel(output_excel_file, index=False)

print(f"All .tsx files have been saved to {output_directory}")
print(f"Backup of generated content has been saved to {output_excel_file}")
print(f"Title metadata has been saved to {metadata_output_file}")
print(f"Title metadata has been saved to {metadata_output_file}")