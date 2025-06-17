import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import logging

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
            metadata_path (str): Path to the metadata file (.pkl)
            output_dir (str): Directory to store all embedding-related files
        """
        self.embeddings_path = embeddings_path
        self.metadata_path = metadata_path
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load embeddings and metadata
        self.embeddings = np.load(embeddings_path)
        self.metadata = pd.read_pickle(metadata_path)
        
        # Reshape embeddings from (n, 1, 768) to (n, 768)
        if len(self.embeddings.shape) == 3:
            self.embeddings = self.embeddings.squeeze(axis=1)
        
        logger.info(f"Loaded embeddings of shape: {self.embeddings.shape}")
        logger.info(f"Loaded metadata with {len(self.metadata)} entries")
    
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
    # Initialize storage
    storage = EmbeddingStorage(
        embeddings_path='data/embeddings/xlmr_embeddings.npy',
        metadata_path='data/embeddings/xlmr_embeddings_metadata.pkl',
        output_dir='data/embeddings/visualizations'
    )
    
    # Save vector embeddings
    storage.save_vector_embeddings()
    
    # Create visualizations
    storage.create_visualization()
    storage.create_similarity_graph()
    storage.create_heatmap()

if __name__ == "__main__":
    main() 