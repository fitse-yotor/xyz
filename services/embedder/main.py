from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class EmbedRequest(BaseModel):
    data: List[Dict]

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.post("/embed")
async def create_embeddings(request: EmbedRequest):
    try:
        # Extract cleaned texts
        texts = [item['cleaned_text'] for item in request.data]
        
        # Generate embeddings
        embeddings = model.encode(texts)
        
        # Add embeddings to the data
        for item, embedding in zip(request.data, embeddings):
            item['embedding'] = embedding.tolist()
        
        # Save embeddings
        output_file = "data/embeddings/message_embeddings.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(request.data, f)
        
        return {
            "status": "success",
            "data": request.data
        }
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 