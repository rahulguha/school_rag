import os
import sys
from anthropic import Anthropic
import json
from vector_db_schools import *
from rerank import *
from llm_response import *

from dotenv import load_dotenv
load_dotenv()

class MemoryChatAgent:
    def __init__(self,  max_memory_length:int=10):
        """
        Initialize the chat agent with API key and memory management.
        
        :param api_key: Anthropic API key
        :param max_memory_length: Maximum number of previous interactions to remember
        """
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.conversation_history = []
        self.max_memory_length = 10
        self.base_db = VectorDB("school_db")
        print(self.client)

    
    def _add_to_memory(self, user_message, ai_response):
        """
        Add interaction to conversation memory, maintaining max length.
        
        :param user_message: Message from the user
        :param ai_response: Response from the AI
        """
        
        # Add the interaction to memory
        self.conversation_history.append({
            'user': user_message,
            'ai': ai_response
        })

        # Trim memory if it exceeds max length
        if len(self.conversation_history) > self.max_memory_length:
            self.conversation_history.pop(0)
    
    def _prepare_context(self):
        """
        Prepare context from conversation history for API call.
        
        :return: List of message dictionaries for API context
        """
        context = []
        for interaction in self.conversation_history:
            context.append({"role": "user", "content": interaction['user']})
            context.append({"role": "assistant", "content": interaction['ai']})
        return context
    
    
    def dicts_to_string(self, messages):
        """
        Converts a list of dictionaries, each with 'role' and 'content' keys, to a string.

        Args:
            data_list: A list of dictionaries.

        Returns:
            A formatted string representation of the list of dictionaries, or None if the input is invalid.
        """
        if not isinstance(messages, list):
            return None  # Return None if input is not a list

        result_strings = []
        for data_dict in messages:
            if 'role' in data_dict and 'content' in data_dict:
                result_strings.append(f"Role: {data_dict['role']}, Content: {data_dict['content']}")
            else:
                return None #Return None if any dictionary is invalid.

        return "\n".join(result_strings) #Join the strings with newlines.
    def get_source_urls(self,retreived_chunks):
        source_urls = []
        source = "Source URLs: "
        for chunk in retreived_chunks:
            source_urls.append(chunk['chunk']['source_url'])
        unique_urls = set(source_urls)
        for u in unique_urls:
            source += f"\n{u}" 
        return source

    def api_chat(self, user_message):
        """
        Generate a response using the Anthropic API with conversation context.
        
        :param user_message: Message from the user
        :return: AI's response
        """
        try:

            llm = LLMResponse(self.client)
            
            
            # Prepare the full context including conversation history
            messages = self._prepare_context() + [
                {"role": "user", "content": user_message}
            ]
            query = self.dicts_to_string(messages)
            print("API" + query)
            reranked_chunks = retrieve_rerank(user_message,self.base_db,5)
            
            ai_response = f"{llm.generate_response(query , reranked_chunks)}\n\n{self.get_source_urls(reranked_chunks)}"  
            # pprint.pprint(self.get_source_urls(reranked_chunks))

            self._add_to_memory(user_message, ai_response)
            
            return ai_response
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
    

    def chat(self, user_message, chat_client):
        """
        Generate a response using the Anthropic API with conversation context.
        
        :param user_message: Message from the user
        :return: AI's response
        """
        try:

            # Prepare the full context including conversation history
            messages = self._prepare_context() + [
                {"role": "user", "content": user_message}
            ]
            query = self.dicts_to_string(messages)
            
            reranked_chunks = retrieve_rerank(user_message,self.base_db,5)
            ai_response = f"{chat_client.generate_response(query , reranked_chunks)}\n\n{self.get_source_urls(reranked_chunks)}"  
            # pprint.pprint(self.get_source_urls(reranked_chunks))

            self._add_to_memory(user_message, ai_response)
            
            return ai_response
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def save_memory(self, filename='conversation_memory.json'):
        """
        Save conversation memory to a JSON file.
        
        :param filename: Name of the file to save memory
        """
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
    
    def load_memory(self, filename='conversation_memory.json'):
        """
        Load conversation memory from a JSON file.
        
        :param filename: Name of the file to load memory from
        """
        try:
            with open(filename, 'r') as f:
                self.conversation_history = json.load(f)
        except FileNotFoundError:
            print(f"No memory file found at {filename}")

# Example usage
def main():
    # Replace with your actual Anthropic API key
    API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Initialize the chat agent
    chat_agent = MemoryChatAgent(API_KEY)
    if chat_agent.base_db.load_vector_db():
            print("Vector DB loaded successfully.")
    else:
        print("Failed to load Vector DB.")
        sys.exit(1)
    
    # Simulate a conversation
    print("Chat Agent initialized. Start chatting!")
    chat_client = LLMResponse(chat_agent.client)
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        
        # Save memory before each response (optional)
        chat_agent.save_memory()
        
        # Get AI response
        response = chat_agent.chat(user_input, chat_client)
        print("AI:", response)

if __name__ == "__main__":
    main()