# Telegram Data Preprocessing and Embedding Project

## Overview

This project is designed to preprocess Telegram chat data, generate word embeddings using the AfroXLMR model, and store these embeddings in a FAISS index for efficient retrieval. The project includes scripts for data preprocessing, embedding generation, and FAISS indexing.

## Model Used for Word Embedding

The project uses the `Davlan/afro-xlmr-large` model from the Hugging Face Transformers library for generating word embeddings. This model is specifically designed for African languages, including Amharic, and provides high-quality embeddings for text data.

## Project Structure

- **data_preprocessor.py**: Contains the `DataPreprocessor` class for cleaning and preprocessing text data.
- **afroxlmr_embedding.py**: Provides a function to generate embeddings using the AfroXLMR model.
- **embed_preprocessed_data.py**: Script to embed preprocessed data and save embeddings.
- **faiss_indexing.py**: Script to create a FAISS index and store embeddings along with their corresponding text chunks.
- **preprocess_recent.py**: Example script to preprocess the most recent CSV file.
- **process_all_data.py**: Script to process all CSV files in specific directories.
- **process_specific_file.py**: Script to process a specific CSV file interactively.

## Setup Instructions

1. **Install Dependencies**: Ensure you have the required Python packages installed. You can install them using the following command:

   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Data**: Place your Telegram chat data in CSV format in the appropriate directories under `data/`.

3. **Run Preprocessing**: Use the `preprocess_recent.py` or `process_all_data.py` scripts to preprocess your data.

4. **Generate Embeddings**: Use the `embed_preprocessed_data.py` script to generate embeddings for your preprocessed data.

5. **Create FAISS Index**: Use the `faiss_indexing.py` script to create a FAISS index and store the embeddings.

## Usage Examples

### Preprocessing Data

```bash
python preprocess_recent.py
```

### Generating Embeddings

```bash
python embed_preprocessed_data.py
```

### Creating FAISS Index

```bash
python faiss_indexing.py
```

## Interactive README

You can interact with this README by running the following command in your terminal:

```bash
python -m http.server
```

Then, open your web browser and navigate to `http://localhost:8000` to view the README interactively.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 