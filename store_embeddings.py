import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import logging
import faiss
import pickle
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingStorage:
    def __init__(self, embeddings_path, metadata_path, output_dir="data/embeddings"):
        """
        Initialize the EmbeddingStorage class.
        
        Args:
            embeddings_path (str): Path to the embeddings file (.npy)
            metadata_path (str): Path to the metadata file (.csv or .pkl)
            output_dir (str): Directory to store all embedding-related files
        """
        self.embeddings_path = embeddings_path
        self.metadata_path = metadata_path
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load metadata first
        logger.info(f"Loading metadata from {metadata_path}")
        if metadata_path.endswith('.csv'):
            self.metadata = pd.read_csv(metadata_path)
        else:
            self.metadata = pd.read_pickle(metadata_path)
        logger.info(f"Loaded metadata with {len(self.metadata)} entries")
        
        # Load or create embeddings
        if os.path.exists(embeddings_path):
            logger.info(f"Loading existing embeddings from {embeddings_path}")
            self.embeddings = np.load(embeddings_path)
            logger.info(f"Loaded embeddings of shape: {self.embeddings.shape}")
        else:
            logger.info("Embeddings file not found. Creating new embeddings...")
            self.create_embeddings()
        
        # Reshape embeddings from (n, 1, 768) to (n, 768)
        if len(self.embeddings.shape) == 3:
            self.embeddings = self.embeddings.squeeze(axis=1)
            logger.info(f"Reshaped embeddings to: {self.embeddings.shape}")
    
    def create_embeddings(self):
        """Create embeddings from the metadata file using XLM-R."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            # Initialize XLM-R model
            logger.info("Initializing XLM-R model...")
            model_name = "xlm-roberta-base"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Get text column
            text_column = 'processed_text' if 'processed_text' in self.metadata.columns else 'text'
            texts = self.metadata[text_column].tolist()
            
            # Create embeddings
            embeddings = []
            batch_size = 32
            
            logger.info(f"Creating embeddings for {len(texts)} texts...")
            for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
                batch_texts = texts[i:i+batch_size]
                
                # Tokenize
                inputs = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                # Get embeddings
                with torch.no_grad():
                    outputs = model(**inputs)
                
                # Mean pooling
                token_embeddings = outputs.last_hidden_state
                attention_mask = inputs['attention_mask']
                token_embeddings = token_embeddings * attention_mask.unsqueeze(-1)
                sum_embeddings = torch.sum(token_embeddings, dim=1)
                sum_mask = torch.sum(attention_mask, dim=1, keepdim=True)
                mean_embeddings = sum_embeddings / sum_mask
                
                embeddings.append(mean_embeddings.numpy())
            
            # Combine all embeddings
            self.embeddings = np.vstack(embeddings)
            
            # Save embeddings
            os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
            np.save(self.embeddings_path, self.embeddings)
            
            logger.info(f"Created and saved embeddings of shape: {self.embeddings.shape}")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def create_faiss_index(self, index_type="flat", nlist=100):
        """
        Create a FAISS index from embeddings.
        
        Args:
            index_type (str): Type of FAISS index to create ('flat' or 'ivf')
            nlist (int): Number of clusters for IVF index
        
        Returns:
            faiss.Index: Created FAISS index
        """
        try:
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.embeddings)
            
            # Convert embeddings to float32
            embeddings_float32 = self.embeddings.astype('float32')
            
            if index_type == "flat":
                # Create a simple flat index
                index = faiss.IndexFlatIP(self.embeddings.shape[1])
            elif index_type == "ivf":
                # Create an IVF index for faster search
                quantizer = faiss.IndexFlatIP(self.embeddings.shape[1])
                index = faiss.IndexIVFFlat(quantizer, self.embeddings.shape[1], nlist)
                # Train the index
                index.train(embeddings_float32)
            else:
                raise ValueError(f"Unsupported index type: {index_type}")
            
            # Add vectors to the index
            index.add(embeddings_float32)
            
            logger.info(f"Created FAISS index of type {index_type} with {index.ntotal} vectors")
            return index
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise
    
    def save_faiss_index(self, index, output_path=None):
        """
        Save FAISS index and associated metadata.
        
        Args:
            index: FAISS index to save
            output_path: Path to save the index (optional)
        """
        try:
            if output_path is None:
                output_path = os.path.join(self.output_dir, 'faiss_index.pkl')
            
            # Prepare data to save
            index_data = {
                'index': index,
                'text_chunks': self.metadata['processed_text'].tolist() if 'processed_text' in self.metadata.columns else self.metadata['text'].tolist()
            }
            
            # Save index and metadata
            with open(output_path, 'wb') as f:
                pickle.dump(index_data, f, protocol=4)
            
            logger.info(f"Saved FAISS index to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    def save_vector_embeddings(self):
        """Save embeddings in various vector formats."""
        try:
            # Save as numpy array
            np.save(os.path.join(self.output_dir, 'embeddings_vector.npy'), self.embeddings)
            
            # Save as CSV
            pd.DataFrame(self.embeddings).to_csv(
                os.path.join(self.output_dir, 'embeddings_vector.csv'),
                index=False
            )
            
            # Save as binary format
            np.savez_compressed(
                os.path.join(self.output_dir, 'embeddings_vector_compressed.npz'),
                embeddings=self.embeddings
            )
            
            logger.info("Saved vector embeddings in multiple formats")
            
        except Exception as e:
            logger.error(f"Error saving vector embeddings: {str(e)}")
    
    def create_visualization(self, n_samples=1000):
        """Create t-SNE visualization of embeddings."""
        try:
            # Sample data if too large
            if len(self.embeddings) > n_samples:
                indices = np.random.choice(len(self.embeddings), n_samples, replace=False)
                sample_embeddings = self.embeddings[indices]
                sample_metadata = self.metadata.iloc[indices]
            else:
                sample_embeddings = self.embeddings
                sample_metadata = self.metadata
            
            # Apply t-SNE
            tsne = TSNE(n_components=2, random_state=42)
            embeddings_2d = tsne.fit_transform(sample_embeddings)
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], alpha=0.5)
            plt.title('t-SNE Visualization of Embeddings')
            plt.savefig(os.path.join(self.output_dir, 'embeddings_tsne.png'))
            plt.close()
            
            logger.info("Created t-SNE visualization")
            
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
    
    def create_similarity_graph(self, threshold=0.8, max_edges=1000):
        """Create a similarity graph of embeddings."""
        try:
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(self.embeddings)
            
            # Create graph
            G = nx.Graph()
            
            # Add edges based on similarity threshold
            edge_count = 0
            for i in range(len(similarity_matrix)):
                for j in range(i+1, len(similarity_matrix)):
                    if similarity_matrix[i,j] > threshold and edge_count < max_edges:
                        G.add_edge(i, j, weight=similarity_matrix[i,j])
                        edge_count += 1
            
            # Draw graph
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=False, node_size=50, alpha=0.6)
            plt.title('Similarity Graph of Embeddings')
            plt.savefig(os.path.join(self.output_dir, 'embeddings_graph.png'))
            plt.close()
            
            # Save graph data
            nx.write_graphml(G, os.path.join(self.output_dir, 'embeddings_graph.graphml'))
            
            logger.info("Created similarity graph")
            
        except Exception as e:
            logger.error(f"Error creating similarity graph: {str(e)}")
    
    def create_heatmap(self, n_samples=100):
        """Create a heatmap of similarity scores."""
        try:
            # Sample data if too large
            if len(self.embeddings) > n_samples:
                indices = np.random.choice(len(self.embeddings), n_samples, replace=False)
                sample_embeddings = self.embeddings[indices]
            else:
                sample_embeddings = self.embeddings
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(sample_embeddings)
            
            # Create heatmap
            plt.figure(figsize=(12, 8))
            sns.heatmap(similarity_matrix, cmap='viridis')
            plt.title('Similarity Heatmap of Embeddings')
            plt.savefig(os.path.join(self.output_dir, 'embeddings_heatmap.png'))
            plt.close()
            
            logger.info("Created similarity heatmap")
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")

def main():
    # Create necessary directories
    os.makedirs('data/embeddings', exist_ok=True)
    os.makedirs('Embeddings', exist_ok=True)
    
    # Define paths
    embeddings_dir = 'data/embeddings'
    processed_file = 'data/preprocessed/all_messages_20250612_130550_processed.csv'
    
    # Initialize storage with correct paths
    storage = EmbeddingStorage(
        embeddings_path=os.path.join(embeddings_dir, 'xlmr_embeddings.npy'),
        metadata_path=processed_file,
        output_dir='Embeddings'
    )
    
    # Save vector embeddings
    storage.save_vector_embeddings()
    
    # Create and save FAISS index
    index = storage.create_faiss_index(index_type="flat")  # or "ivf" for faster search
    storage.save_faiss_index(index)
    
    # Create visualizations
    storage.create_visualization()
    storage.create_similarity_graph()
    storage.create_heatmap()

if __name__ == "__main__":
    main() 