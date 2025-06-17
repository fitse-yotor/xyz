from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import faiss
import numpy as np
from typing import List, Dict
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class StoreRequest(BaseModel):
    data: List[Dict]

# Initialize FAISS index
dimension = 384  # Dimension of the embeddings
index = faiss.IndexFlatL2(dimension)

@app.post("/store")
async def store_data(request: StoreRequest):
    try:
        # Extract embeddings
        embeddings = np.array([item['embedding'] for item in request.data])
        
        # Add vectors to FAISS index
        index.add(embeddings)
        
        # Save the index
        output_file = "data/storage/faiss_index.bin"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        faiss.write_index(index, output_file)
        
        # Save metadata
        metadata_file = "data/storage/metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(request.data, f)
        
        return {
            "status": "success",
            "response": "Data successfully stored and indexed"
        }
        
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_similar(query_embedding: List[float], k: int = 5):
    try:
        # Convert query embedding to numpy array
        query_vector = np.array([query_embedding])
        
        # Search in FAISS index
        distances, indices = index.search(query_vector, k)
        
        # Load metadata
        with open("data/storage/metadata.json", 'r') as f:
            metadata = json.load(f)
        
        # Get results
        results = [metadata[i] for i in indices[0]]
        
        return {
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error searching data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 