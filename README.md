# Telegram Chat Analysis Microservices

## Project Structure

```
telegram-chat-analysis/
├── src/
│   ├── scraper/                 # Telegram message scraping service
│   │   ├── telegram_scraper.py  # Main scraper implementation
│   │   └── utils/              # Scraper utilities
│   │
│   ├── preprocessor/           # Data preprocessing service
│   │   ├── preprocessor.py     # Main preprocessing logic
│   │   └── utils/             # Preprocessing utilities
│   │
│   ├── embedder/              # Text embedding service
│   │   ├── embedder.py        # Main embedding logic
│   │   └── utils/            # Embedding utilities
│   │
│   ├── storage/              # Data storage service
│   │   ├── storage.py        # Main storage logic
│   │   └── utils/           # Storage utilities
│   │
│   └── bot/                 # Telegram bot service
│       ├── bot.py           # Main bot implementation
│       └── utils/          # Bot utilities
│
├── data/                    # Data directory
│   ├── raw/                # Raw scraped data
│   ├── preprocessed/       # Cleaned data
│   ├── embeddings/         # Generated embeddings
│   └── storage/           # FAISS indices
│
├── docker/                 # Docker configuration
│   ├── scraper/
│   ├── preprocessor/
│   ├── embedder/
│   ├── storage/
│   └── bot/
│
├── tests/                 # Test directory
│   ├── scraper/
│   ├── preprocessor/
│   ├── embedder/
│   ├── storage/
│   └── bot/
│
├── requirements.txt       # Project dependencies
├── docker-compose.yml    # Docker compose configuration
└── README.md            # Project documentation
```

## Services Overview

### 1. Scraper Service (`src/scraper/`)
- Handles Telegram message scraping
- Manages session and authentication
- Implements rate limiting and error handling
- Stores raw messages in JSON format

### 2. Preprocessor Service (`src/preprocessor/`)
- Cleans and normalizes text data
- Removes noise and irrelevant content
- Implements text preprocessing pipeline
- Handles multiple languages

### 3. Embedder Service (`src/embedder/`)
- Generates text embeddings using XLM-RoBERTa
- Manages embedding models and versions
- Implements batch processing
- Handles model caching

### 4. Storage Service (`src/storage/`)
- Manages FAISS indices
- Handles data persistence
- Implements search functionality
- Manages data versioning

### 5. Bot Service (`src/bot/`)
- Provides Telegram bot interface
- Handles user commands
- Implements search functionality
- Manages user sessions

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd telegram-chat-analysis
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

## Development

1. **Service Development**
   - Each service is independent and can be developed separately
   - Follow the service-specific README in each directory
   - Use the provided Docker configurations for testing

2. **Testing**
   ```bash
   # Run all tests
   pytest

   # Run specific service tests
   pytest tests/[service_name]
   ```

3. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Document all functions and classes

## Deployment

1. **Docker Deployment**
   ```bash
   # Build and start all services
   docker-compose up --build

   # Start specific service
   docker-compose up [service_name]
   ```

2. **Kubernetes Deployment**
   ```bash
   # Apply Kubernetes configurations
   kubectl apply -f k8s/
   ```

## Monitoring

1. **Service Health**
   - Each service exposes a `/health` endpoint
   - Monitor using Prometheus and Grafana
   - Check service logs in Docker

2. **Performance Metrics**
   - Message processing rate
   - Embedding generation time
   - Search response time
   - Resource utilization

## Contributing

1. **Development Workflow**
   - Create feature branch
   - Write tests
   - Submit pull request
   - Code review

2. **Code Standards**
   - Follow PEP 8
   - Write unit tests
   - Update documentation
   - Add type hints

## License

This project is licensed under the MIT License - see the LICENSE file for details. 