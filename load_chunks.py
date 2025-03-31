import os
import json

def load_jsonl_files(folder_path):
    """
    Load all JSONL files from a specified folder.
    
    Args:
        folder_path (str): Path to the folder containing JSONL files
        
    Returns:
        dict: Dictionary with filenames as keys and lists of JSON objects as values
    """
    jsonl_files = {}
    
    try:
        # Check if folder exists
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The folder {folder_path} does not exist")
        
        # Iterate through all files in the folder
        for filename in os.listdir(folder_path):
            # Check if file has .jsonl extension
            if filename.endswith('.jsonl'):
                file_path = os.path.join(folder_path, filename)
                json_objects = []
                
                # Read the file line by line
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        # Remove whitespace and newlines
                        line = line.strip()
                        if line:  # Ensure line is not empty
                            try:
                                json_obj = json.loads(line)
                                json_objects.append(json_obj)
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON in {filename}: {str(e)}")
                                continue
                
                if json_objects:  # Only add to dictionary if we have valid objects
                    jsonl_files[filename] = json_objects
                    
        return jsonl_files
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}

def main():
    # Specify the folder path where your JSONL files are located
    folder_path = "website_content/TAMU//chunks/"  # Replace with your folder path
    
    # Load the JSONL files
    files_content = load_jsonl_files(folder_path)
    print(files_content.items)
    # Print the contents
    if files_content:
        print("Found JSONL files:")
        for filename, json_objects in files_content.items():
            print(f"\nFile: {filename}")
            print(f"Number of JSON objects: {len(json_objects)}")
            
            if json_objects:  # If there are any objects
                print(f"Number of chunks: {len(json_objects)}")
                for chunk in json_objects:
                    print(len(chunk["chunk_text"]))
                    
                # print(json.dumps(json_objects[0], indent=2))
    else:
        print("No JSONL files were loaded.")

if __name__ == "__main__":
    main()