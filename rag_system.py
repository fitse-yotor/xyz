import faiss
import numpy as np
import pickle
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from typing import List, Dict, Tuple
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(
        self,
        faiss_index_path: str = "Embeddings/faiss_index.pkl",
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize the RAG system.
        
        Args:
            faiss_index_path: Path to the FAISS index file
            model_name: Name of the Mistral model to use
            device: Device to run the model on (cuda/cpu)
        """
        self.device = device
        self.load_faiss_index(faiss_index_path)
        self.load_mistral_model(model_name)
        
    def load_faiss_index(self, index_path: str):
        """Load the FAISS index and associated text chunks."""
        try:
            logger.info(f"Loading FAISS index from {index_path}")
            with open(index_path, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.text_chunks = data['text_chunks']
            logger.info(f"Loaded index with {len(self.text_chunks)} text chunks")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            raise
            
    def load_mistral_model(self, model_name: str):
        """Load the Mistral model and tokenizer."""
        try:
            logger.info(f"Loading Mistral model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto"
            )
            logger.info("Mistral model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Mistral model: {str(e)}")
            raise
            
    def get_query_embedding(self, query: str) -> np.ndarray:
        """Get embedding for the query using XLM-R."""
        try:
            from transformers import AutoTokenizer, AutoModel
            
            # Initialize XLM-R model
            model_name = "xlm-roberta-base"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Tokenize and get embedding
            inputs = tokenizer(
                query,
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
            
            # Convert to numpy and normalize
            query_embedding = mean_embeddings.numpy()
            faiss.normalize_L2(query_embedding)
            
            return query_embedding
            
        except Exception as e:
            logger.error(f"Error getting query embedding: {str(e)}")
            raise
            
    def retrieve_relevant_chunks(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant text chunks for the query."""
        try:
            # Get query embedding
            query_embedding = self.get_query_embedding(query)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, k)
            
            # Get relevant chunks
            relevant_chunks = [self.text_chunks[i] for i in indices[0]]
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise
            
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using Mistral model."""
        try:
            # Prepare prompt
            context_text = "\n".join(context)
            prompt = f"""<s>[INST] You are a helpful AI assistant. Use the following context to answer the question.
            
Context:
{context_text}

Question: {query}

Answer: [/INST]"""
            
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                do_sample=True
            )
            
            # Decode and clean response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.split("Answer:")[-1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
            
    def query(self, query: str, k: int = 3) -> Tuple[str, List[str]]:
        """
        Process a query through the RAG system.
        
        Args:
            query: The user's question
            k: Number of relevant chunks to retrieve
            
        Returns:
            Tuple of (response, relevant_chunks)
        """
        try:
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(query, k)
            
            # Generate response
            response = self.generate_response(query, relevant_chunks)
            
            return response, relevant_chunks
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

def main():
    # Initialize RAG system
    rag = RAGSystem()
    
    # Example query
    query = "What are the main topics discussed in the chat?"
    response, chunks = rag.query(query)
    
    print("\nQuery:", query)
    print("\nResponse:", response)
    print("\nRelevant chunks used:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n{i}. {chunk}")

if __name__ == "__main__":
    main() 