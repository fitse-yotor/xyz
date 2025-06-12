from data_preprocessor import DataPreprocessor
import os

def process_file(csv_filename):
    try:
        # Get the data directory path
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'exports')
        csv_path = os.path.join(data_dir, csv_filename)
        
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            return
        
        print(f"Processing file: {csv_path}")
        
        # Initialize the preprocessor
        preprocessor = DataPreprocessor(csv_path)
        
        # Perform advanced text cleaning
        print("\nPerforming advanced text cleaning...")
        preprocessor.advanced_text_cleaning()
        
        # Show example of text preprocessing
        print("\nText Preprocessing Example:")
        print("Original text:", preprocessor.df['Message'].iloc[0])
        print("Normalized text:", preprocessor.df['normalized_text'].iloc[0])
        print("Cleaned text:", preprocessor.df['cleaned_text'].iloc[0])
        print("Tokens:", preprocessor.df['tokens'].iloc[0])
        print("Filtered tokens (without stopwords):", preprocessor.df['filtered_tokens'].iloc[0])
        print("Final processed text:", preprocessor.df['processed_text'].iloc[0])
        
        # Extract date features
        print("\nExtracting date features...")
        preprocessor.extract_date_features()
        
        # Calculate message statistics
        print("\nCalculating message statistics...")
        stats = preprocessor.calculate_message_stats()
        print("\nMessage Statistics:")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"Average Message Length: {stats['avg_message_length']:.2f} characters")
        print(f"Unique Senders: {stats['unique_senders']}")
        print(f"Average Tokens per Message: {stats['avg_tokens_per_message']:.2f}")
        print(f"Unique Tokens: {stats['unique_tokens']}")
        
        # Save processed data
        print("\nSaving processed data...")
        preprocessor.save_processed_data()
        
        print("\nData preprocessing completed successfully!")
        
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")

if __name__ == "__main__":
    # List available files
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'exports')
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and not f.endswith('_processed.csv')]
    
    print("Available files to process:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")
    
    # Get user input
    choice = input("\nEnter the number of the file to process (or 'q' to quit): ")
    
    if choice.lower() == 'q':
        print("Exiting...")
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(csv_files):
                process_file(csv_files[index])
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!") 