import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import logging
from tqdm import tqdm
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XLMREmbedder:
    def __init__(self, model_name="xlm-roberta-base", device=None):
        """
        Initialize the XLM-R embedder.
        
        Args:
            model_name (str): Name of the XLM-R model to use
            device (str): Device to use for computation ('cuda' or 'cpu')
        """
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()  # Set model to evaluation mode
        
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text using XLM-R.
        
        Args:
            text (str): Input text to embed
            
        Returns:
            np.ndarray: Embedding vector
        """
        try:
            # Tokenize text
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Get model outputs
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Mean pooling over the last hidden state
            last_hidden_state = outputs.last_hidden_state
            attention_mask = inputs['attention_mask']
            
            # Manual mean pooling
            token_embeddings = last_hidden_state * attention_mask.unsqueeze(-1)
            sum_embeddings = torch.sum(token_embeddings, dim=1)
            sum_mask = torch.sum(attention_mask, dim=1, keepdim=True)
            mean_embeddings = sum_embeddings / sum_mask
            
            return mean_embeddings.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return np.zeros(self.model.config.hidden_size)
    
    def process_csv(self, csv_path: str, text_column: str, output_path: str, batch_size: int = 32):
        """
        Process a CSV file and generate embeddings for all texts.
        
        Args:
            csv_path (str): Path to the CSV file
            text_column (str): Name of the column containing text
            output_path (str): Path to save the embeddings
            batch_size (int): Number of texts to process at once
        """
        try:
            # Load CSV file
            logger.info(f"Loading CSV file from {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Initialize list to store embeddings
            all_embeddings = []
            
            # Process texts in batches
            for i in tqdm(range(0, len(df), batch_size), desc="Generating embeddings"):
                batch_texts = df[text_column].iloc[i:i+batch_size].tolist()
                
                # Generate embeddings for batch
                batch_embeddings = []
                for text in batch_texts:
                    embedding = self.get_embedding(str(text))
                    batch_embeddings.append(embedding)
                
                all_embeddings.extend(batch_embeddings)
            
            # Convert to numpy array
            embeddings_array = np.array(all_embeddings)
            
            # Save embeddings
            np.save(output_path, embeddings_array)
            logger.info(f"Saved embeddings to {output_path}")
            
            # Save metadata
            metadata_path = output_path.replace('.npy', '_metadata.pkl')
            df.to_pickle(metadata_path)
            logger.info(f"Saved metadata to {metadata_path}")
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise

def main():
    # Initialize embedder
    embedder = XLMREmbedder(model_name="xlm-roberta-base")
    
    # Process CSV file
    csv_path = "data/preprocessed/all_messages_20250612_130550_processed.csv"
    output_path = "data/embeddings/xlmr_embeddings.npy"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate embeddings
    embedder.process_csv(
        csv_path=csv_path,
        text_column="processed_text",
        output_path=output_path,
        batch_size=32
    )

if __name__ == "__main__":
    main() 