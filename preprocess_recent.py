import os
from data_preprocessor import DataPreprocessor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Get the most recent CSV file from the exports directory
        exports_dir = os.path.join('data', 'bulk_exports')
        csv_files = [f for f in os.listdir(exports_dir) if f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in exports directory")
        
        # Sort by modification time and get the most recent
        latest_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(exports_dir, x)))
        csv_path = os.path.join(exports_dir, latest_file)
        
        print(f"Processing file: {csv_path}")
        
        # Initialize preprocessor with chunking
        preprocessor = DataPreprocessor(csv_path, chunk_size=1000)
        
        print("\nPerforming advanced text cleaning...")
        # Process text cleaning in chunks
        preprocessor.process_in_chunks(preprocessor.advanced_text_cleaning_chunk)
        
        # Display example of text preprocessing
        if len(preprocessor.df) > 0:
            print("\nText Preprocessing Example:")
            sample_text = preprocessor.df['Message'].iloc[0]
            print(f"Original text: {sample_text}")
            print(f"Normalized text: {preprocessor.df['normalized_text'].iloc[0]}")
            print(f"Cleaned text: {preprocessor.df['cleaned_text'].iloc[0]}")
            print(f"Tokens: {preprocessor.df['tokens'].iloc[0]}")
            print(f"Filtered tokens: {preprocessor.df['filtered_tokens'].iloc[0]}")
            print(f"Final processed text: {preprocessor.df['processed_text'].iloc[0]}")
        
        print("\nCalculating message statistics...")
        stats = preprocessor.calculate_message_stats()
        
        print("\nMessage Statistics:")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"Average Message Length: {stats['avg_message_length']:.2f} characters")
        print(f"Unique Senders: {stats['unique_senders']}")
        print(f"Average Tokens per Message: {stats['avg_tokens_per_message']:.2f}")
        print(f"Unique Tokens: {stats['unique_tokens']}")
        
        print("\nCalculating sender activity...")
        sender_activity = preprocessor.get_sender_activity()
        
        print("\nTop 5 Most Active Senders:")
        print(sender_activity.head())
        
        print("\nGrouping messages by time period...")
        daily_messages = preprocessor.group_by_time_period(period='D')
        
        print("\nMessages per day (last 5 days):")
        print(daily_messages.tail())
        
        print("\nSaving processed data...")
        preprocessor.save_processed_data()
        
        print("\nData preprocessing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during preprocessing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 