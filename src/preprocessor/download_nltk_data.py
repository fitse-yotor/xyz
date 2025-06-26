#!/usr/bin/env python3
"""
Download NLTK Data
Download required NLTK data for the preprocessor
"""

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_data():
    """Download required NLTK data"""
    print("📥 Downloading NLTK data...")
    
    try:
        # Download punkt tokenizer
        print("Downloading punkt tokenizer...")
        nltk.download('punkt')
        
        # Download stopwords
        print("Downloading stopwords...")
        nltk.download('stopwords')
        
        # Download averaged_perceptron_tagger (for better tokenization)
        print("Downloading averaged_perceptron_tagger...")
        nltk.download('averaged_perceptron_tagger')
        
        # Download maxent_ne_chunker (for named entity recognition)
        print("Downloading maxent_ne_chunker...")
        nltk.download('maxent_ne_chunker')
        
        # Download words corpus
        print("Downloading words corpus...")
        nltk.download('words')
        
        print("✅ All NLTK data downloaded successfully!")
        
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        print("Trying alternative download method...")
        
        try:
            # Try downloading to a specific directory
            import os
            nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
            os.makedirs(nltk_data_dir, exist_ok=True)
            
            nltk.download('punkt', download_dir=nltk_data_dir)
            nltk.download('stopwords', download_dir=nltk_data_dir)
            nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
            nltk.download('maxent_ne_chunker', download_dir=nltk_data_dir)
            nltk.download('words', download_dir=nltk_data_dir)
            
            print("✅ NLTK data downloaded to user directory!")
            
        except Exception as e2:
            print(f"❌ Alternative download also failed: {e2}")
            print("Please try running the preprocessor again.")

def main():
    """Main function"""
    print("=" * 50)
    print("NLTK Data Downloader")
    print("=" * 50)
    
    download_nltk_data()
    
    print("\n" + "=" * 50)
    print("Download completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 