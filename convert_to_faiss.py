import numpy as np
import faiss
import pickle
import os
import logging
import pandas as pd
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingToFAISS:
    def __init__(self, embedding_dim: int = 768):  # Changed to 768 for XLM-R base
        """
        Initialize the converter.
        
        Args:
            embedding_dim: Dimension of the embeddings (default: 768 for XLM-R base)
        """
        self.embedding_dim = embedding_dim
        
    def load_embeddings(self, embedding_path: str) -> np.ndarray:
        """
        Load embeddings from a numpy file.
        
        Args:
            embedding_path: Path to the .npy file containing embeddings
            
        Returns:
            np.ndarray: Loaded embeddings
        """
        try:
            embeddings = np.load(embedding_path)
            # Reshape if needed (remove extra dimension)
            if len(embeddings.shape) == 3:
                embeddings = embeddings.squeeze(1)
            logger.info(f"Loaded embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            raise Exception(f"Error loading embeddings: {str(e)}")
    
    def load_text_chunks(self, metadata_path: str) -> List[str]:
        """
        Load text chunks from metadata file.
        
        Args:
            metadata_path: Path to the metadata file
            
        Returns:
            List[str]: List of text chunks
        """
        try:
            # Try different methods to load the metadata
            try:
                # First try: direct pandas read
                df = pd.read_csv(metadata_path.replace('_metadata.pkl', '.csv'))
                text_column = 'processed_text' if 'processed_text' in df.columns else 'text'
                text_chunks = df[text_column].tolist()
            except:
                try:
                    # Second try: read pickle with protocol 4
                    with open(metadata_path, 'rb') as f:
                        df = pd.read_pickle(f, compression=None)
                    text_column = 'processed_text' if 'processed_text' in df.columns else 'text'
                    text_chunks = df[text_column].tolist()
                except:
                    # Third try: read the original CSV file
                    csv_path = metadata_path.replace('_metadata.pkl', '.csv')
                    if os.path.exists(csv_path):
                        df = pd.read_csv(csv_path)
                        text_column = 'processed_text' if 'processed_text' in df.columns else 'text'
                        text_chunks = df[text_column].tolist()
                    else:
                        raise Exception("Could not find text data in any format")
            
            logger.info(f"Loaded {len(text_chunks)} text chunks")
            return text_chunks
        except Exception as e:
            raise Exception(f"Error loading text chunks: {str(e)}")
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Create a FAISS index from embeddings.
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            faiss.Index: FAISS index
        """
        try:
            # Normalize embeddings
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index
            index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            index.add(embeddings.astype('float32'))
            
            logger.info(f"Created FAISS index with {index.ntotal} vectors")
            return index
        except Exception as e:
            raise Exception(f"Error creating FAISS index: {str(e)}")
    
    def save_faiss_index(self, index: faiss.Index, text_chunks: List[str], output_path: str):
        """
        Save FAISS index and text chunks.
        
        Args:
            index: FAISS index
            text_chunks: List of text chunks
            output_path: Path to save the index
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save index and text chunks
            index_data = {
                'index': index,
                'text_chunks': text_chunks
            }
            
            with open(output_path, 'wb') as f:
                pickle.dump(index_data, f, protocol=4)  # Use protocol 4 for better compatibility
            
            logger.info(f"Saved FAISS index to {output_path}")
        except Exception as e:
            raise Exception(f"Error saving FAISS index: {str(e)}")
    
    def convert(self, 
                embedding_path: str, 
                metadata_path: str, 
                output_path: str = "embeddings/faiss_index.pkl"):
        """
        Convert embeddings to FAISS index.
        
        Args:
            embedding_path: Path to the .npy file containing embeddings
            metadata_path: Path to the metadata file
            output_path: Path to save the FAISS index
        """
        try:
            # Load embeddings and text chunks
            embeddings = self.load_embeddings(embedding_path)
            text_chunks = self.load_text_chunks(metadata_path)
            
            # Verify lengths match
            if len(embeddings) != len(text_chunks):
                raise Exception(f"Number of embeddings ({len(embeddings)}) does not match number of text chunks ({len(text_chunks)})")
            
            # Create FAISS index
            index = self.create_faiss_index(embeddings)
            
            # Save index and text chunks
            self.save_faiss_index(index, text_chunks, output_path)
            
            logger.info("Conversion completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}")
            raise

def main():
    # Initialize converter
    converter = EmbeddingToFAISS()
    
    # Define paths - updated to use Embeddings folder
    embedding_path = "Embeddings/xlmr_embeddings.npy"
    metadata_path = "Embeddings/xlmr_embeddings_metadata.pkl"
    output_path = "Embeddings/faiss_index.pkl"
    
    # Convert embeddings to FAISS index
    converter.convert(embedding_path, metadata_path, output_path)

if __name__ == "__main__":
    main() 