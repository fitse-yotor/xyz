from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from telethon import TelegramClient
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ScrapeRequest(BaseModel):
    text: str
    chat_id: int

@app.post("/scrape")
async def scrape_messages(request: ScrapeRequest):
    try:
        # Initialize Telegram client
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        
        client = TelegramClient('scraper_session', api_id, api_hash)
        await client.start()
        
        # Scrape messages from the specified chat
        messages = []
        async for message in client.iter_messages(request.chat_id, limit=100):
            if message.text:
                messages.append({
                    "text": message.text,
                    "date": message.date.isoformat(),
                    "id": message.id
                })
        
        await client.disconnect()
        
        # Save scraped data
        output_file = f"data/raw/messages_{request.chat_id}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "data": messages}
        
    except Exception as e:
        logger.error(f"Error scraping messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 