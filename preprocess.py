from dotenv import load_dotenv
load_dotenv()
import os
# from chunking import *
from chunking import *
from vector_db_schools import *
from rerank import *
from llm_response import *
from load_chunks import *
import sys
import pprint

import anthropic

client = anthropic.Anthropic(
    # This is the default and can be omitted
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
def extract_filename_and_path(file_path):
    """
    Extracts the filename (including extension) and the path before the filename from a given file path.

    Args:
        file_path (str): The full path to the file.

    Returns:
        tuple: A tuple containing (path_before_filename, filename), or (None, None) if the path is invalid.
    """
    if not isinstance(file_path, str) or not file_path:
        return None, None

    try:
        filename = os.path.basename(file_path)
        path_before_filename = os.path.dirname(file_path)
        return path_before_filename, filename
    except Exception:
        return None, None
def save_jsonl(data: list, filename: str):
    """
    Saves a list of dictionaries to a JSONL (JSON Lines) file.

    :param data: List of dictionaries to save.
    :param filename: Name of the JSONL file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for entry in data:
                json.dump(entry, f)
                f.write("\n")  # Each entry is on a new line
        print(f"Saved {len(data)} records to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")
def split_path_filename(full_path):
    """
    Split a full path into directory path and filename.
    
    Args:
        full_path (str): The full path (e.g., "website_content/TAMU/tuition.tamu.edu_undergraduate.json")
        
    Returns:
        tuple: (directory_path, filename) where directory_path is the path without the filename,
               and filename is the last component (file name with extension)
    """
    # Get the directory path (everything except the filename)
    directory_path = os.path.dirname(full_path)
    
    # Get the filename (last component of the path)
    filename = os.path.basename(full_path)
    
    return directory_path, filename
# Initialize the VectorDB
base_db = VectorDB("school_db")

# if base_db.load_vector_db():
#      print("db loaded")
#      q = "what is GAN?"
#      reranked_chunks = retrieve_rerank(q,base_db,5)
#      chat = LLMResponse(client)
#      print( chat.generate_response(q, reranked_chunks) ) 
# else:
print("db not loaded")
# file_path = "data/local/birthright_citizenship.txt"
file_path_list=[]
folder_path = "website_content/"
schools = []
all_chunks = []

# check if files are present with chunks ?
for school_name in os.listdir(folder_path):
    schools.append(f"{folder_path}{school_name}/")
    school_folder= f"{folder_path}{school_name}/"
    school_folder= f"{folder_path}{school_name}/"
    if os.path.isdir(school_folder):
        for school_file in os.listdir(school_folder):
            if school_file.endswith(".json"):
                file_path = os.path.join(school_folder, school_file)
                file_path_list.append(file_path)
                print(file_path)    


chunk_file_path = ""
chunk_file_name = ""
# # chunk
for f in file_path_list:
    # find out if the file is processed or not
    chunk_file_path, chunk_file_name = extract_filename_and_path( f) #+ "_chunk.jsonl"
    chunk_file_name = f"{chunk_file_path}/chunks/{chunk_file_name}_chunk.jsonl"
    # print(chunk_file_name)
    if not os.path.exists(chunk_file_name):
        print ("file needs to be chunked")

        # create chunks
        chunks = create_chunks_from_file(
            file_path= f,
            chunk_size=500,
            chunk_overlap=50
            )
        chunk_file_path, chunk_file_name = extract_filename_and_path( f) #+ "_chunk.jsonl"
        print(chunk_file_path)
        os.makedirs(f"{chunk_file_path}/chunks", exist_ok=True)
        chunk_file_path = chunk_file_path + "/chunks"
        chunk_file_name = chunk_file_name + "_chunk.jsonl"
        print(f"{chunk_file_path}/{chunk_file_name}")
        save_jsonl(chunks, chunk_file_path + "/" + chunk_file_name)
        # all_chunks.extend(chunks)
    else:
        print ("file already chunked")
        # load chunks
        chunks = load_jsonl(chunk_file_name)
        all_chunks.extend(chunks)

    print (f"{chunk_file_name} - {len (all_chunks)}")
# # # # Load and process the data
base_db.load_data(all_chunks)
