import pandas as pd
import json
import numpy as np

# Load the data from the Excel file
df = pd.read_excel('merged_outputMAIN.xlsx')

# Function to clean up tab characters
def clean_string(value):
    if isinstance(value, str):
        return value.replace('\t', '').strip()
    return value

# Create a function to consolidate group titles and features for each stock
def consolidate_features(group):
    features = []
    
    for idx, row in group.iterrows():
        group_title = clean_string(row['GroupTitle'])  # Clean up tabs
        feature = clean_string(row['Feature'])  # Clean up tabs
        
        if pd.notna(group_title) and pd.notna(feature):
            features.append({
                "GroupTitle": group_title,
                "Feature": feature
            })
    
    # Drop the GroupTitle and Feature columns and keep unique values for the stock
    group = group.iloc[0].drop(['GroupTitle', 'Feature'])
    
    # Apply cleaning to other string fields
    group = group.apply(clean_string)
    
    # Add consolidated features to the row
    group['Features'] = features
    
    return group

# Group by Stock and apply the consolidation function
consolidated_df = df.groupby('Stock').apply(consolidate_features)

# Reset the index for proper format
consolidated_df.reset_index(drop=True, inplace=True)

# Convert NaN values to None (null in JSON)
consolidated_df = consolidated_df.replace({np.nan: None})

# Convert the DataFrame to a dictionary
result_dict = consolidated_df.to_dict(orient='records')

# Write the dictionary to a JSON file
with open('consolidated_output.json', 'w') as json_file:
    json.dump(result_dict, json_file, indent=4)

print("Consolidation complete and saved to 'consolidated_output.json'")
