from fastapi import FastAPI, HTTPException
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import httpx
import os
import logging
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
TOKEN = "8160834321:AAE30b17ZbcA2LIzJqUcZ4PkBaOh5_oG2KY"

# Service URLs
SCRAPER_URL = os.getenv("SCRAPER_SERVICE_URL", "http://scraper:8001")
PREPROCESSOR_URL = os.getenv("PREPROCESSOR_SERVICE_URL", "http://preprocessor:8002")
EMBEDDER_URL = os.getenv("EMBEDDER_SERVICE_URL", "http://embedder:8003")
STORAGE_URL = os.getenv("STORAGE_SERVICE_URL", "http://storage:8004")

class Message(BaseModel):
    text: str
    chat_id: int

async def start_command(update: Update, context):
    await update.message.reply_text('Hello! I am your question-answer bot. Send me any question and I will try to answer it.')

async def handle_message(update: Update, context):
    try:
        # Forward message to scraper service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SCRAPER_URL}/scrape",
                json={"text": update.message.text, "chat_id": update.message.chat_id}
            )
            
            if response.status_code == 200:
                # Process the scraped data
                preprocess_response = await client.post(
                    f"{PREPROCESSOR_URL}/preprocess",
                    json=response.json()
                )
                
                if preprocess_response.status_code == 200:
                    # Generate embeddings
                    embed_response = await client.post(
                        f"{EMBEDDER_URL}/embed",
                        json=preprocess_response.json()
                    )
                    
                    if embed_response.status_code == 200:
                        # Store results
                        store_response = await client.post(
                            f"{STORAGE_URL}/store",
                            json=embed_response.json()
                        )
                        
                        if store_response.status_code == 200:
                            await update.message.reply_text(store_response.json()["response"])
                        else:
                            raise HTTPException(status_code=store_response.status_code)
                    else:
                        raise HTTPException(status_code=embed_response.status_code)
                else:
                    raise HTTPException(status_code=preprocess_response.status_code)
            else:
                raise HTTPException(status_code=response.status_code)
                
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text("Sorry, I encountered an error processing your message.")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main() 