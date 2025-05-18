import os
import pandas as pd
import re
import openai
import random


openai.api_key = "openai-api-key"


excel_path = r"C:\Users\15162\Desktop\pipseo\OpenAi\lottery\lottery_data.xlsx"
df = pd.read_excel(excel_path, usecols=["Numbers"])

# Split the Numbers for Powerball Number
def split_numbers(numbers_str):
    numbers = [int(num) for num in re.findall(r'\d+', numbers_str)]
    if len(numbers) == 6:
        return numbers  # Ensure there are exactly 6 numbers
    else:
        print(f"Invalid row skipped: {numbers}")
        return [None] * 6

# create new columns
df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Powerball']] = pd.DataFrame(
    df['Numbers'].apply(split_numbers).tolist(), index=df.index
)

# Drop rows with invalid data
df = df.dropna()

# Save
split_output_path = r"C:\Users\15162\Desktop\pipseo\OpenAi\lottery\split_lottery_data.xlsx"
df.to_excel(split_output_path, index=False)
print(f"Split numbers saved to {split_output_path}")

# generate a prompt for column analysis
def generate_prompt_for_column(column, col_name, min_value, max_value):
    data_str = ", ".join(map(str, column))
    prompt = (
        f"Analyze the following historical lottery data for the column '{col_name}':\n\n{data_str}\n\n"
        f"Based on historical trends, generate 35 new unique numbers for the column '{col_name}'. "
        f"The numbers must be between {min_value} and {max_value}, inclusive. Avoid sequential patterns and ensure randomness."
    )
    return prompt

def query_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,  # Increased temperature for more variation
            max_tokens=1500
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return ""

# Parse
def parse_response(response, min_value, max_value):
    numbers = [int(num) for num in re.findall(r'\d+', response)]
    valid_numbers = [num for num in numbers if min_value <= num <= max_value]

    # Shuffle
    random.shuffle(valid_numbers)
    return valid_numbers[:5]  # Limit to 5 unique numbers

# Analyze each column and generate new numbers
generated_numbers = {}
for col_name in ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']:
    column_data = df[col_name].tolist()
    prompt = generate_prompt_for_column(column_data, col_name, 1, 69)
    response = query_openai(prompt)
    generated_numbers[col_name] = parse_response(response, 1, 69)

# Analyze the Powerball column (Num6) with the unique range rule
powerball_data = df['Powerball'].tolist()
powerball_prompt = generate_prompt_for_column(powerball_data, 'Powerball', 1, 26)
powerball_response = query_openai(powerball_prompt)
generated_numbers['Powerball'] = parse_response(powerball_response, 1, 26)

# Convert generated numbers to a DataFrame
generated_df = pd.DataFrame(generated_numbers)

# Save the generated numbers to a new Excel file
generated_output_path = r"C:\Users\15162\Desktop\pipseo\OpenAi\lottery\generated_lottery_numbers.xlsx"
generated_df.to_excel(generated_output_path, index=False)

print(f"Generated lottery numbers saved to {generated_output_path}.")