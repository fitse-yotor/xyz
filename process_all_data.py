import os
import pandas as pd
from data_preprocessor import DataPreprocessor
import logging
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data_preprocessing.log'
)
logger = logging.getLogger(__name__)

def create_preprocessed_dir():
    """Create the preprocessed directory if it doesn't exist"""
    preprocessed_dir = os.path.join('data', 'preprocessed')
    if not os.path.exists(preprocessed_dir):
        os.makedirs(preprocessed_dir)
        logger.info(f"Created preprocessed directory at {preprocessed_dir}")
    return preprocessed_dir

def get_all_csv_files():
    """Get all CSV files from exports, realtime, and search_results folders"""
    csv_files = []
    folders = ['exports', 'realtime', 'search_results']
    
    for folder in folders:
        folder_path = os.path.join('data', folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('.csv'):
                    csv_files.append({
                        'path': os.path.join(folder_path, file),
                        'folder': folder,
                        'filename': file
                    })
    
    return csv_files

def process_file(file_info, preprocessed_dir):
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
            f.write(f"Unique Senders: {stats['unique_senders']}\n")
            f.write(f"Average Tokens per Message: {stats['avg_tokens_per_message']:.2f}\n")
            f.write(f"Unique Tokens: {stats['unique_tokens']}\n")
        
        logger.info(f"Successfully processed {filename}")
        print(f"Successfully processed {filename}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing {file_info['filename']}: {str(e)}")
        print(f"Error processing {file_info['filename']}: {str(e)}")
        return False

def main():
    try:
        # Create preprocessed directory
        preprocessed_dir = create_preprocessed_dir()
        
        # Get all CSV files
        csv_files = get_all_csv_files()
        
        if not csv_files:
            logger.warning("No CSV files found to process")
            print("No CSV files found to process")
            return
        
        # Process files and track results
        summary_report = []
        total_files = len(csv_files)
        successful_files = 0
        
        print(f"\nFound {total_files} CSV files to process")
        logger.info(f"Found {total_files} CSV files to process")
        
        for file_info in csv_files:
            success = process_file(file_info, preprocessed_dir)
            if success:
                successful_files += 1
            summary_report.append({
                'filename': file_info['filename'],
                'folder': file_info['folder'],
                'status': 'Success' if success else 'Failed'
            })
        
        # Save summary report
        summary_df = pd.DataFrame(summary_report)
        summary_path = os.path.join(preprocessed_dir, f"processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        summary_df.to_csv(summary_path, index=False)
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed {successful_files} out of {total_files} files")
        print(f"Results saved in: {preprocessed_dir}")
        print(f"Summary report: {summary_path}")
        
        logger.info(f"Processing complete. Successfully processed {successful_files} out of {total_files} files")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 