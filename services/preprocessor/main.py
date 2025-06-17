from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import pandas as pd
import re
import emoji
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class PreprocessRequest(BaseModel):
    data: List[Dict]

def clean_text(text: str) -> str:
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove emojis
    text = emoji.replace_emoji(text, '')
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@app.post("/preprocess")
async def preprocess_data(request: PreprocessRequest):
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Clean text
        df['cleaned_text'] = df['text'].apply(clean_text)
        
        # Remove empty messages
        df = df[df['cleaned_text'].str.len() > 0]
        
        # Save preprocessed data
        output_file = "data/preprocessed/processed_messages.json"
        df.to_json(output_file, orient='records', indent=2)
        
        return {
            "status": "success",
            "data": df.to_dict(orient='records')
        }
        
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 