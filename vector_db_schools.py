import os
import pickle
import json
import numpy as np
import voyageai
import anthropic
from typing import List, Dict, Any
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()


class VectorDB:
    def __init__(self, name: str, voyage_api_key = None, anthropic_api_key=None):

        if voyage_api_key is None:
            api_key = os.getenv("VOYAGE_API_KEY")
        if anthropic_api_key is None:
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.client = voyageai.Client(api_key=voyage_api_key)
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        # self.db_path = f"./data/{name}/vector_db.pkl"
        self.db_path = f"./data/{name}/schools_db.pkl"

    def load_vector_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data.get('embeddings', [])
                    self.metadata = data.get('metadata', [])
                    
                    # Ensure query_cache is a dictionary
                    self.query_cache = data.get('query_cache', {})
                    if not isinstance(self.query_cache, dict):
                        self.query_cache = {}
                
                return True
            except Exception as e:
                print(f"Error loading vector database: {e}")
                # Fallback to empty cache if loading fails
                self.query_cache = {}
                return False
        else:
            print(f"Vector database file not found at {self.db_path}")
            self.query_cache = {}  # Ensure it's a dictionary
            return False

    def load_data(self, dataset: List[Dict[str, Any]]):
        if self.embeddings and self.metadata:
            print("Vector database is already loaded. Skipping data loading.")
            return
        if os.path.exists(self.db_path):
            print("Loading vector database from disk.")
            self.load_db()
            return

        texts_to_embed = []
        metadata = []
        total_chunks = len(dataset) # sum(len(doc['chunks']) for doc in dataset)
        print(f"Total chunks to process: {total_chunks}")
        with tqdm(total=total_chunks, desc="Processing chunks") as pbar:
            # for doc in dataset:
                for chunk in dataset: #doc['chunks']
                    texts_to_embed.append(chunk['chunk_text'])
                    metadata.append({
                        'content': chunk['chunk_text'],
                        'context': chunk['context'],
                        'source_url': chunk['source_url'],
                    })
                pbar.update(1)

        self._embed_and_store(texts_to_embed, metadata)
        self.save_db()
        
        print(f"Vector database loaded and saved. Total chunks processed: {len(texts_to_embed)}")

    def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        batch_size = 128
        with tqdm(total=len(texts), desc="Embedding chunks") as pbar:
            result = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_result = self.client.embed(batch, model="voyage-3-large").embeddings
                result.extend(batch_result)
                pbar.update(len(batch))
        
        self.embeddings = result
        self.metadata = data

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            query_embedding = self.client.embed([query], model="voyage-3-large").embeddings[0]
            self.query_cache[query] = query_embedding

        if not self.embeddings:
            raise ValueError("No data loaded in the vector database.")

        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        top_results = []
        for idx in top_indices:
            result = {
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx]),
            }
            top_results.append(result)
        
        return top_results

    def save_db(self):
        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "query_cache": json.dumps(self.query_cache),
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)

    def load_db(self):
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        self.query_cache = json.loads(data["query_cache"])

    def validate_embedded_chunks(self):
        unique_contents = set()
        for meta in self.metadata:
            unique_contents.add(meta['content'])
    
        print(f"Validation results:")
        print(f"Total embedded chunks: {len(self.metadata)}")
        print(f"Unique embedded contents: {len(unique_contents)}")
    
        if len(self.metadata) != len(unique_contents):
            print("Warning: There may be duplicate chunks in the embedded data.")
        else:
            print("All embedded chunks are unique.")


    