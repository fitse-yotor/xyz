import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_afroxlmr_embedding(text: str) -> np.ndarray:
    """
    Use the transformers library to load 'Davlan/afro-xlmr-large', tokenize Amharic text,
    and use mean pooling over the last hidden state to get 1024-dim embeddings.
    
    Args:
        text (str): Input Amharic text to embed.
        
    Returns:
        np.ndarray: 1024-dimensional embedding vector.
    """
    try:
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained('Davlan/afro-xlmr-large')
        model = AutoModel.from_pretrained('Davlan/afro-xlmr-large')
        
        # Tokenize text
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        
        # Get model outputs
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Mean pooling over the last hidden state
        last_hidden_state = outputs.last_hidden_state
        attention_mask = inputs['attention_mask']
        token_embeddings = last_hidden_state * attention_mask.unsqueeze(-1)
        sum_embeddings = torch.sum(token_embeddings, dim=1)
        sum_mask = torch.sum(attention_mask, dim=1, keepdim=True)
        mean_embeddings = sum_embeddings / sum_mask
        
        return mean_embeddings.numpy()
    except Exception as e:
        logger.error(f"Error in get_afroxlmr_embedding: {str(e)}")
        return np.zeros(1024)  # Return zero vector in case of error

if __name__ == "__main__":
    # Example usage
    sample_text = "Your Amharic text here"
    embedding = get_afroxlmr_embedding(sample_text)
    print(f"Generated embedding shape: {embedding.shape}") 