import faiss
import numpy as np
import pickle
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_faiss_index(embeddings: np.ndarray, texts: list, index_file: str = 'faiss_index.bin', metadata_file: str = 'metadata.pkl'):
    """
    Create a FAISS index using IndexFlatL2(1024) for storing embeddings.
    Add chunk embeddings into the index along with their corresponding text.
    Save the FAISS index and metadata.
    
    Args:
        embeddings (np.ndarray): Array of embeddings to index.
        texts (list): List of corresponding text chunks.
        index_file (str): Path to save the FAISS index.
        metadata_file (str): Path to save the metadata.
    """
    try:
        # Create a FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to the index
        index.add(embeddings)
        logger.info(f"Added {len(embeddings)} embeddings to the FAISS index")
        
        # Save the FAISS index
        faiss.write_index(index, index_file)
        logger.info(f"Saved FAISS index to {index_file}")
        
        # Save metadata (texts)
        with open(metadata_file, 'wb') as f:
            pickle.dump(texts, f)
        logger.info(f"Saved metadata to {metadata_file}")
        
    except Exception as e:
        logger.error(f"Error creating FAISS index: {str(e)}")

if __name__ == "__main__":
    # Example usage
    # Load embeddings and texts
    embeddings = np.load('embeddings.npy')
    texts = ['Text chunk 1', 'Text chunk 2', 'Text chunk 3']  # Replace with actual text chunks
    
    # Create FAISS index
    create_faiss_index(embeddings, texts) 