import pandas as pd
import numpy as np
from afroxlmr_embedding import get_afroxlmr_embedding
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def embed_preprocessed_data(csv_file: str, text_column: str = 'processed_text', output_file: str = 'embeddings.npy'):
    """
    Load preprocessed data from a CSV file, generate embeddings for each text chunk,
    and save the embeddings to a file.
    
    Args:
        csv_file (str): Path to the preprocessed CSV file.
        text_column (str): Name of the column containing the text to embed.
        output_file (str): Path to save the embeddings.
    """
    try:
        # Load preprocessed data
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded preprocessed data from {csv_file}")
        
        # Generate embeddings for each text chunk
        embeddings = []
        for text in df[text_column]:
            embedding = get_afroxlmr_embedding(text)
            embeddings.append(embedding)
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings)
        
        # Save embeddings to file
        np.save(output_file, embeddings_array)
        logger.info(f"Saved embeddings to {output_file}")
        
    except Exception as e:
        logger.error(f"Error embedding preprocessed data: {str(e)}")

if __name__ == "__main__":
    # Example usage with the correct file path
    embed_preprocessed_data('data/preprocessed/all_messages_20250612_130550_processed.csv', text_column='processed_text', output_file='embeddings.npy') 