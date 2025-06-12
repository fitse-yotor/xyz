import pandas as pd
import numpy as np
from datetime import datetime
import re
import emoji
from typing import Optional, List, Dict, Union, Iterator
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import unicodedata
from pathlib import Path
import os

# Ensure required NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, csv_file: str, chunk_size: int = 1000):
        """
        Initialize the DataPreprocessor with a CSV file path.
        
        Args:
            csv_file (str): Path to the CSV file to preprocess
            chunk_size (int): Number of rows to process at once
        """
        self.csv_file = csv_file
        self.chunk_size = chunk_size
        self.df = None
        self.stop_words = set(stopwords.words('english'))
        self.processed_chunks = []
        self.load_data()
    
    def load_data(self) -> None:
        """Load the CSV data into a pandas DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_file)
            logger.info(f"Successfully loaded data from {self.csv_file}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase and handling special characters.
        
        Args:
            text (str): Input text to normalize
            
        Returns:
            str: Normalized text
        """
        try:
            # Convert to string if not already
            text = str(text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Normalize unicode characters
            text = unicodedata.normalize('NFKD', text)
            
            # Remove accents
            text = ''.join([c for c in text if not unicodedata.combining(c)])
            
            return text
        except Exception as e:
            logger.error(f"Error normalizing text: {str(e)}")
            return str(text)  # Return string representation even if error occurs

    def remove_punctuation_and_noise(self, text: str) -> str:
        """
        Remove punctuation and noise from text.
        
        Args:
            text (str): Input text to clean
            
        Returns:
            str: Cleaned text
        """
        try:
            # Convert to string if not already
            text = str(text)
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Remove special characters and numbers
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.error(f"Error removing punctuation and noise: {str(e)}")
            return str(text)  # Return string representation even if error occurs

    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words using simple whitespace splitting.
        
        Args:
            text (str): Input text to tokenize
            
        Returns:
            List[str]: List of tokens
        """
        try:
            # Convert to string if not already
            text = str(text)
            
            # Simple tokenization by splitting on whitespace
            tokens = text.split()
            return tokens
        except Exception as e:
            logger.error(f"Error tokenizing text: {str(e)}")
            return [str(text)]  # Return single token with string representation if error occurs

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from tokens.
        
        Args:
            tokens (List[str]): List of tokens
            
        Returns:
            List[str]: List of tokens without stopwords
        """
        try:
            # Remove stopwords
            filtered_tokens = [token for token in tokens if token not in self.stop_words]
            return filtered_tokens
        except Exception as e:
            logger.error(f"Error removing stopwords: {str(e)}")
            return tokens

    def process_in_chunks(self, func: callable, *args, **kwargs) -> None:
        """
        Process data in chunks using the specified function.
        
        Args:
            func (callable): Function to apply to each chunk
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        try:
            # Read CSV in chunks
            chunk_iterator = pd.read_csv(self.csv_file, chunksize=self.chunk_size)
            
            for i, chunk in enumerate(chunk_iterator):
                logger.info(f"Processing chunk {i+1}")
                
                # Apply the function to the chunk
                processed_chunk = func(chunk, *args, **kwargs)
                self.processed_chunks.append(processed_chunk)
                
            # Combine all processed chunks
            self.df = pd.concat(self.processed_chunks, ignore_index=True)
            logger.info("All chunks processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing chunks: {str(e)}")
            raise

    def clean_text_chunk(self, chunk: pd.DataFrame, text_column: str = 'Message') -> pd.DataFrame:
        """
        Clean text data in a chunk.
        
        Args:
            chunk (pd.DataFrame): Data chunk to process
            text_column (str): Name of the column containing text to clean
            
        Returns:
            pd.DataFrame: Processed chunk
        """
        try:
            # Create a copy to avoid modifying the original
            processed_chunk = chunk.copy()
            
            # Remove emojis
            processed_chunk[text_column] = processed_chunk[text_column].apply(
                lambda x: emoji.replace_emoji(str(x), '')
            )
            
            # Remove special characters and extra whitespace
            processed_chunk[text_column] = processed_chunk[text_column].apply(
                lambda x: re.sub(r'[^\w\s]', '', str(x)).strip()
            )
            
            return processed_chunk
            
        except Exception as e:
            logger.error(f"Error cleaning text chunk: {str(e)}")
            raise

    def advanced_text_cleaning_chunk(self, chunk: pd.DataFrame, text_column: str = 'Message') -> pd.DataFrame:
        """
        Perform advanced text cleaning on a chunk and keep all processed columns.
        
        Args:
            chunk (pd.DataFrame): Data chunk to process
            text_column (str): Name of the column containing text to clean
            
        Returns:
            pd.DataFrame: Processed chunk with all columns
        """
        try:
            # Create a copy to avoid modifying the original
            processed_chunk = chunk.copy()
            
            # Apply text preprocessing steps
            processed_chunk['normalized_text'] = processed_chunk[text_column].apply(self.normalize_text)
            processed_chunk['cleaned_text'] = processed_chunk['normalized_text'].apply(self.remove_punctuation_and_noise)
            processed_chunk['tokens'] = processed_chunk['cleaned_text'].apply(self.tokenize_text)
            processed_chunk['filtered_tokens'] = processed_chunk['tokens'].apply(self.remove_stopwords)
            processed_chunk['processed_text'] = processed_chunk['filtered_tokens'].apply(lambda x: ' '.join(x))
            
            # Keep all columns including the original ones
            return processed_chunk
            
        except Exception as e:
            logger.error(f"Error in advanced text cleaning chunk: {str(e)}")
            raise

    def extract_date_features_chunk(self, chunk: pd.DataFrame, date_column: str = 'Date') -> pd.DataFrame:
        """
        Extract date features from a chunk.
        
        Args:
            chunk (pd.DataFrame): Data chunk to process
            date_column (str): Name of the column containing dates
            
        Returns:
            pd.DataFrame: Processed chunk
        """
        try:
            # Create a copy to avoid modifying the original
            processed_chunk = chunk.copy()
            
            # Convert to datetime
            processed_chunk[date_column] = pd.to_datetime(processed_chunk[date_column])
            
            # Extract features
            processed_chunk['year'] = processed_chunk[date_column].dt.year
            processed_chunk['month'] = processed_chunk[date_column].dt.month
            processed_chunk['day'] = processed_chunk[date_column].dt.day
            processed_chunk['hour'] = processed_chunk[date_column].dt.hour
            processed_chunk['day_of_week'] = processed_chunk[date_column].dt.dayofweek
            
            return processed_chunk
            
        except Exception as e:
            logger.error(f"Error extracting date features from chunk: {str(e)}")
            raise

    def save_processed_data(self, output_file: Optional[str] = None) -> None:
        """
        Save the processed data to a new CSV file with only essential columns.
        
        Args:
            output_file (str, optional): Path to save the processed data. If None, 
                                       will append '_processed' to the original filename
        """
        try:
            # Create preprocessed directory if it doesn't exist
            preprocessed_dir = os.path.join('data', 'preprocessed')
            os.makedirs(preprocessed_dir, exist_ok=True)
            
            if output_file is None:
                base_name = Path(self.csv_file).stem
                output_file = os.path.join(preprocessed_dir, f"{base_name}_processed.csv")
            else:
                # Ensure output file is in preprocessed directory
                output_file = os.path.join(preprocessed_dir, os.path.basename(output_file))
            
            # Keep only essential columns
            essential_columns = ['Message', 'processed_text', 'tokens', 'filtered_tokens']
            if all(col in self.df.columns for col in essential_columns):
                self.df = self.df[essential_columns]
            
            # Save in chunks to handle large files
            chunk_size = 1000
            for i, chunk in enumerate(pd.read_csv(self.csv_file, chunksize=chunk_size)):
                # Process the chunk
                processed_chunk = self.advanced_text_cleaning_chunk(chunk)
                
                # Save with appropriate mode and header
                mode = 'w' if i == 0 else 'a'
                header = i == 0
                processed_chunk.to_csv(output_file, mode=mode, header=header, index=False)
            
            logger.info(f"Processed data saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")
            raise
    
    def extract_date_features(self, date_column: str = 'Date') -> None:
        """
        Extract date features from the date column.
        
        Args:
            date_column (str): Name of the column containing dates
        """
        try:
            # Convert to datetime
            self.df[date_column] = pd.to_datetime(self.df[date_column])
            
            # Extract features
            self.df['year'] = self.df[date_column].dt.year
            self.df['month'] = self.df[date_column].dt.month
            self.df['day'] = self.df[date_column].dt.day
            self.df['hour'] = self.df[date_column].dt.hour
            self.df['day_of_week'] = self.df[date_column].dt.dayofweek
            
            logger.info("Date features extracted successfully")
        except Exception as e:
            logger.error(f"Error extracting date features: {str(e)}")
            raise
    
    def calculate_message_stats(self, text_column: str = 'Message') -> Dict:
        """
        Calculate basic statistics about the messages.
        
        Args:
            text_column (str): Name of the column containing messages
            
        Returns:
            Dict: Dictionary containing message statistics
        """
        try:
            stats = {
                'total_messages': len(self.df),
                'avg_message_length': self.df[text_column].str.len().mean(),
                'max_message_length': self.df[text_column].str.len().max(),
                'min_message_length': self.df[text_column].str.len().min(),
                'avg_tokens_per_message': self.df['tokens'].apply(len).mean() if 'tokens' in self.df.columns else None,
                'unique_tokens': len(set([token for tokens in self.df['tokens'] for token in tokens])) if 'tokens' in self.df.columns else None,
                'unique_senders': self.df['Sender'].nunique() if 'Sender' in self.df.columns else None
            }
            
            logger.info("Message statistics calculated successfully")
            return stats
        except Exception as e:
            logger.error(f"Error calculating message stats: {str(e)}")
            raise
    
    def group_by_time_period(self, period: str = 'D') -> pd.DataFrame:
        """
        Group messages by time period.
        
        Args:
            period (str): Time period to group by ('D' for daily, 'M' for monthly, etc.)
            
        Returns:
            pd.DataFrame: Grouped data
        """
        try:
            # Ensure Date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(self.df['Date']):
                self.df['Date'] = pd.to_datetime(self.df['Date'])
            
            grouped = self.df.groupby(pd.Grouper(key='Date', freq=period)).size()
            logger.info(f"Data grouped by {period} successfully")
            return grouped
        except Exception as e:
            logger.error(f"Error grouping by time period: {str(e)}")
            raise
    
    def get_sender_activity(self) -> pd.DataFrame:
        """
        Calculate sender activity statistics.
        
        Returns:
            pd.DataFrame: DataFrame containing sender activity statistics
        """
        try:
            # Ensure Date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(self.df['Date']):
                self.df['Date'] = pd.to_datetime(self.df['Date'])
            
            activity = self.df.groupby('Sender').agg({
                'Message': 'count',
                'Date': ['min', 'max']
            }).reset_index()
            
            activity.columns = ['Sender', 'Message_Count', 'First_Message', 'Last_Message']
            
            # Calculate duration in days
            activity['Activity_Duration'] = (activity['Last_Message'] - activity['First_Message']).dt.total_seconds() / (24 * 3600)
            
            logger.info("Sender activity statistics calculated successfully")
            return activity
        except Exception as e:
            logger.error(f"Error calculating sender activity: {str(e)}")
            raise

    def process_file(self, file_info, preprocessed_dir):
        """Process a single CSV file"""
        try:
            input_path = file_info['path']
            folder = file_info['folder']
            filename = file_info['filename']
            
            # Create timestamp for the processed file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create output filename
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_preprocessed_{timestamp}.csv"
            output_path = os.path.join(preprocessed_dir, output_filename)
            
            logger.info(f"Processing file: {input_path}")
            print(f"\nProcessing file: {input_path}")
            
            # Initialize preprocessor with chunking
            preprocessor = DataPreprocessor(input_path, chunk_size=1000)
            
            # Process text cleaning in chunks
            print("Performing advanced text cleaning...")
            preprocessor.process_in_chunks(preprocessor.advanced_text_cleaning_chunk)
            
            # Calculate statistics
            stats = preprocessor.calculate_message_stats()
            logger.info(f"Statistics for {filename}: {stats}")
            
            # Save processed data
            preprocessor.save_processed_data(output_path)
            
            # Create a summary file
            summary_path = os.path.join(preprocessed_dir, f"{base_name}_summary_{timestamp}.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Processing Summary for {filename}\n")
                f.write(f"Original Location: {input_path}\n")
                f.write(f"Processed Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Messages: {stats['total_messages']}\n")
                f.write(f"Average Message Length: {stats['avg_message_length']:.2f}\n")
                f.write(f"Average Tokens per Message: {stats['avg_tokens_per_message']:.2f}\n")
                f.write(f"Unique Tokens: {stats['unique_tokens']}\n")
            
            logger.info(f"Successfully processed {filename}")
            print(f"Successfully processed {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_info['filename']}: {str(e)}")
            print(f"Error processing {file_info['filename']}: {str(e)}")
            return False

    def clean_and_chunk_text(self, text_column: str = 'Message', max_tokens: int = 300) -> List[str]:
        """
        Clean the text by removing emojis, links, and normalizing punctuation.
        Then chunk the cleaned messages into segments of approximately 100–300 tokens
        using sentence splitting based on the Amharic period '።'.
        
        Args:
            text_column (str): Name of the column containing text to clean and chunk.
            max_tokens (int): Maximum number of tokens per chunk.
            
        Returns:
            List[str]: List of cleaned, chunked texts.
        """
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded. Call load_data() first.")
            
            # Clean the text
            self.df['cleaned_text'] = self.df[text_column].apply(self.remove_punctuation_and_noise)
            self.df['cleaned_text'] = self.df['cleaned_text'].apply(self.normalize_text)
            
            # Split into sentences based on Amharic period '።'
            self.df['sentences'] = self.df['cleaned_text'].apply(lambda x: x.split('።'))
            
            # Flatten sentences and chunk into segments of max_tokens
            all_sentences = []
            for sentences in self.df['sentences']:
                all_sentences.extend(sentences)
            
            chunks = []
            current_chunk = []
            current_token_count = 0
            
            for sentence in all_sentences:
                tokens = self.tokenize_text(sentence)
                if current_token_count + len(tokens) > max_tokens:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = tokens
                    current_token_count = len(tokens)
                else:
                    current_chunk.extend(tokens)
                    current_token_count += len(tokens)
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        except Exception as e:
            logger.error(f"Error in clean_and_chunk_text: {str(e)}")
            return []

    def get_afroxlmr_embedding(self, text: str) -> np.ndarray:
        """
        Use the transformers library to load 'Davlan/afro-xlmr-large', tokenize Amharic text,
        and use mean pooling over the last hidden state to get 1024-dim embeddings.
        
        Args:
            text (str): Input Amharic text to embed.
            
        Returns:
            np.ndarray: 1024-dimensional embedding vector.
        """
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
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
 