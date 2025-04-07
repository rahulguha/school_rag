from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from school_chat import MemoryChatAgent
from vector_db_schools import *
from rerank import *
from llm_response import *

app = FastAPI()

class QueryRequest(BaseModel):
    query: str


# Assume qa_chain is already defined from the previous step

@app.post("/chat")
async def chat(query_request: QueryRequest):
    try:
        print (query_request.query)
        chat_agent = MemoryChatAgent()
        print("Chat Agent initialized")
        print(dir(chat_agent))
        if chat_agent.base_db.load_vector_db():
            print("Vector DB loaded successfully.")
        else:
            print("Failed to load Vector DB.")
            sys.exit(1)
        
        
        response = chat_agent.api_chat(query_request.query)
        return {
            "answer": response
        }
            # print("AI:", response)


        # # Get response from RAG pipeline
        # response = qa_chain({"query": query_request.query})
        # return {
        #     "answer": response["result"],
        #     "source_documents": [doc.page_content for doc in response["source_documents"]]
        # }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)