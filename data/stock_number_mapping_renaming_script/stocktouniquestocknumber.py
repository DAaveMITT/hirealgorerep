#this worked for swapping the Carpenter Bus stock numbers to my new stock numbers

import os
import pandas as pd
import shutil

df = pd.read_excel('please.xlsx')  # Correctly reference your Excel file

image_directory = r'C:vehicle_images'
output_directory = r'C:/output_vehicle_images3'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

stock_to_stocknumber = {str(row['Stock']): str(int(row['StockNumber'])) for index, row in df.iterrows()}

for foldername in os.listdir(image_directory):
    folder_path = os.path.join(image_directory, foldername)
    
    print(f"\nProcessing folder: {folder_path}")

    if os.path.isdir(folder_path):
        # Look up the corresponding StockNumber
        if foldername in stock_to_stocknumber:
            stock_number = stock_to_stocknumber[foldername]

            # Create the new folder path for the StockNumber in the output directory
            stock_folder_path = os.path.join(output_directory, stock_number)

            print(f"Creating stock folder at: {stock_folder_path}")

            # Ensure the stock folder exists, if not, create it
            if not os.path.exists(stock_folder_path):
                os.makedirs(stock_folder_path)
                print(f"Created stock folder: {stock_folder_path}")
            else:
                print(f"Stock folder already exists: {stock_folder_path}")

            # Iterate through the images inside the folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.avif'):
                    old_file_path = os.path.join(folder_path, filename)

                    # Create the new filename by replacing the stock number in the filename with the StockNumber
                    new_filename = filename.replace(foldername, stock_number)

                    # Define the new file path
                    new_file_path = os.path.join(stock_folder_path, new_filename)

                    # Copy the file to the new location with the new filename
                    shutil.copy2(old_file_path, new_file_path)  # `copy2` preserves file metadata
                    print(f'Copied and renamed {old_file_path} to {new_file_path}')
                else:
                    print(f'Skipped non-image file: {filename}')
        else:
            print(f'Stock number {foldername} not found in the mapping.')
    else:
        print(f'Skipped non-folder item: {foldername}')
