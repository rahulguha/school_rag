import anthropic
import typing
import pprint

class LLMResponse:
    def __init__(self, anthropic_client):
        # self.vector_db = vector_db
        self.anthropic_client = anthropic_client
    
    def generate_response(
        self, 
        query: str,
        retrieved_context_chunks,
        max_context_tokens: int = 3500  # Prevent context overflow
    ) -> str:
        """
        Generate a contextual response using retrieved chunks
        
        Args:
            query (str): User's original query
            k (int): Number of top similar chunks to retrieve
            max_context_tokens (int): Maximum tokens for context
        
        Returns:
            str: Generated response from LLM
        """
        
        # 2. Prepare context from chunks
        context_chunks =[]
        source = ""
        for chunk in retrieved_context_chunks:
            source = f"Source: {chunk["chunk"]['context']}\n{chunk["chunk"]['content']}" 
            context_chunks.append(source) 
        # context_chunks = [
        #     f"[Source: {chunk['context']}]\n{chunk['content']}" 
        #     for chunk in retrieved_context_chunks[0]["chunk"]
        # ]
        
        # 3. Truncate context to prevent token overflow
        
        context = "\n\n".join(context_chunks)
        # print(context)
        context_tokens = self.count_tokens(context)
        # pprint.pprint(f"{context_tokens} - {max_context_tokens}")
        if float(context_tokens) > float(max_context_tokens):
            context = self.truncate_context(context, max_context_tokens)
        
        # 4. Construct prompt with retrieved context
        system_prompt = f"""You are an expert research assistant. 
        Use the following contextual information to provide a comprehensive and precise answer to the user's query.
        
        Contextual Information:
        {context}
        
        If the context does not directly answer the query, acknowledge this and provide the most relevant information available."""
        
        # 5. Generate final response
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                system=system_prompt,
                max_tokens=500,
                messages=[
                    {
                        "role": "user", 
                        "content": query
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for a given text
        
        Args:
            text (str): Input text
        
        Returns:
            int: Estimated token count
        """
        # Very basic token estimation
        return len(text.split()) * 1.3  # Rough estimate
    
    def truncate_context(self, context: str, max_tokens: int) -> str:
        """
        Truncate context to fit within token limit
        
        Args:
            context (str): Full context
            max_tokens (int): Maximum allowed tokens
        
        Returns:
            str: Truncated context
        """
        chunks = context.split("\n\n")
        print(chunks)
        truncated_context = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = self.count_tokens(chunk)
            
            if current_tokens + chunk_tokens <= max_tokens:
                truncated_context.append(chunk)
                current_tokens += chunk_tokens
            else:
                break
        
        return "\n\n".join(truncated_context)

