#!/bin/bash

BUCKET_NAME="busconnectstaticpages"
FILES_DIR="./staticFiles" 

# Check if the directory exists
if [ ! -d "$FILES_DIR" ]; then
  echo "Directory $FILES_DIR does not exist. Please provide the correct path."
  exit 1
fi

# Loop through all state directories
for state_dir in "$FILES_DIR"/*; do
  if [ -d "$state_dir" ]; then
    state_name=$(basename "$state_dir") 

    # Loop through all town files in each state directory
    for file in "$state_dir"/*; do
      if [ -f "$file" ]; then
        town_name=$(basename "$file" .js)  # Extract town name from file
        echo "Uploading $file to R2 bucket under states/$state_name/towns/$town_name.js..."

        # Upload the file to the correct R2 prefix (folder-like structure)
        wrangler r2 object put "$BUCKET_NAME/states/$state_name/towns/$town_name.js" --file "$file"

        # Check if the upload succeeded
        if [ $? -eq 0 ]; then
          echo "$file uploaded successfully."
        else
          echo "Failed to upload $file."
        fi
      fi
    done
  fi
done

echo "Batch upload completed."
