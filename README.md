# Telegram Chat Analysis Microservices

This project is a microservices-based system for analyzing Telegram chat data, using Apache Kafka for message queuing and optimized Docker builds for better performance.

## Architecture Overview

### Services

1. **Telegram Bot Service (Port 8000)**
   - Acts as the API Gateway
   - Handles user interactions
   - Routes requests to appropriate services
   - Manages the Telegram bot interface

2. **Scraper Service (Port 8001)**
   - Handles Telegram message scraping
   - Uses Telethon library for API access
   - Saves raw message data

3. **Preprocessor Service (Port 8002)**
   - Cleans and preprocesses message data
   - Removes URLs, emojis, and special characters
   - Prepares data for embedding generation

4. **Embedder Service (Port 8003)**
   - Generates embeddings using Sentence Transformers
   - Uses the all-MiniLM-L6-v2 model
   - Processes cleaned text into vector representations

5. **Storage Service (Port 8004)**
   - Manages data storage and retrieval
   - Uses FAISS for efficient similarity search
   - Stores embeddings and metadata

### Message Queue (Apache Kafka)
- Handles asynchronous communication between services
- Provides message persistence and fault tolerance
- Enables scalable message processing
- Topics:
  - `scrape-topic`: Raw message data
  - `preprocess-topic`: Cleaned message data
  - `embed-topic`: Message embeddings
  - `store-topic`: Storage operations

## Directory Structure

```
project/
├── services/
│   ├── telegram_bot/          # Telegram Bot Service
│   │   ├── main.py           # Bot implementation
│   │   └── Dockerfile        # Bot service container
│   ├── scraper/              # Scraping Service
│   │   ├── main.py          # Scraping implementation
│   │   └── Dockerfile       # Scraper container
│   ├── preprocessor/         # Preprocessing Service
│   │   ├── main.py          # Text preprocessing
│   │   └── Dockerfile       # Preprocessor container
│   ├── embedder/            # Embedding Service
│   │   ├── main.py          # Embedding generation
│   │   └── Dockerfile       # Embedder container
│   ├── storage/             # Storage Service
│   │   ├── main.py          # Data storage and retrieval
│   │   └── Dockerfile       # Storage container
│   └── common/              # Shared Components
│       └── kafka_utils.py   # Kafka utilities
├── data/                    # Data Storage
│   ├── raw/                # Raw scraped data
│   ├── preprocessed/       # Cleaned data
│   ├── embeddings/         # Generated embeddings
│   └── storage/            # FAISS indices
└── docker-compose.yml      # Service orchestration
```

## Prerequisites

1. **Docker and Docker Compose**
   - Docker Desktop for Windows
   - Docker Compose v2.0 or higher

2. **Python 3.9+**
   - Required for local development

3. **Telegram API Credentials**
   - API ID
   - API Hash
   - Bot Token

## Setup and Running

### 1. Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Set environment variables**:
   ```bash
   # Windows PowerShell
   $env:TELEGRAM_API_ID="your_api_id"
   $env:TELEGRAM_API_HASH="your_api_hash"
   $env:TELEGRAM_BOT_TOKEN="your_bot_token"
   ```

### 2. Build and Run

#### Option 1: Standard Build
```bash
docker-compose up --build
```

#### Option 2: Optimized Build (Recommended)
```bash
# Enable BuildKit
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

# Build and run
docker-compose up --build
```

#### Option 3: Parallel Build
```bash
# Build services in parallel
docker-compose build --parallel telegram_bot scraper preprocessor embedder storage

# Start services
docker-compose up
```

### 3. Monitoring

1. **View service logs**:
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f [service_name]
   ```

2. **Monitor resource usage**:
   ```bash
   docker stats
   ```

3. **Check service status**:
   ```bash
   docker-compose ps
   ```

## Resource Management

Each service has resource limits configured:
- **Kafka**: 1 CPU, 1GB RAM
- **Zookeeper**: 0.5 CPU, 512MB RAM
- **Other services**: 0.5 CPU, 512MB RAM each

## API Endpoints

### Telegram Bot Service
- `/start` - Start the bot
- `/help` - Get help information

### Scraper Service
- POST `/scrape` - Scrape messages from a chat

### Preprocessor Service
- POST `/preprocess` - Preprocess scraped messages

### Embedder Service
- POST `/embed` - Generate embeddings for preprocessed messages

### Storage Service
- POST `/store` - Store embeddings and metadata
- GET `/search` - Search for similar messages

## Data Flow

1. User sends a message to the Telegram bot
2. Bot service publishes message to `scrape-topic`
3. Scraper service processes message and publishes to `preprocess-topic`
4. Preprocessor cleans data and publishes to `embed-topic`
5. Embedder generates embeddings and publishes to `store-topic`
6. Storage service indexes the data and returns results
7. Results are sent back to the user through the bot

## Troubleshooting

1. **Build Issues**:
   ```bash
   # Clean build cache
   docker-compose build --no-cache

   # Remove all containers and volumes
   docker-compose down -v
   ```

2. **Service Issues**:
   ```bash
   # Restart specific service
   docker-compose restart [service_name]

   # View service logs
   docker-compose logs -f [service_name]
   ```

3. **Kafka Issues**:
   ```bash
   # Check Kafka status
   docker-compose logs -f kafka

   # Check Zookeeper status
   docker-compose logs -f zookeeper
   ```

## Performance Optimization

1. **Build Optimizations**:
   - Using BuildKit for faster builds
   - Multi-stage builds
   - Proper layer caching
   - Excluded unnecessary files with .dockerignore

2. **Runtime Optimizations**:
   - Resource limits for each service
   - Optimized Kafka settings
   - Efficient message processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Docker Configuration

### Docker Architecture

1. **Base Image**
   - Uses `python:3.9-slim` as base image
   - Optimized for size and performance
   - Includes essential build tools

2. **Multi-stage Builds**
   ```dockerfile
   # Build stage
   FROM python:3.9-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Runtime stage
   FROM python:3.9-slim
   COPY --from=builder /app /app
   ```

3. **Volume Management**
   - Persistent data storage
   - Shared volumes between services
   - Data directory structure:
     ```
     data/
     ├── raw/          # Raw scraped data
     ├── preprocessed/ # Cleaned data
     ├── embeddings/   # Generated embeddings
     └── storage/      # FAISS indices
     ```

### Docker Commands

1. **Basic Commands**
   ```bash
   # Build all services
   docker-compose build

   # Start all services
   docker-compose up

   # Start in detached mode
   docker-compose up -d

   # Stop all services
   docker-compose down

   # View logs
   docker-compose logs -f
   ```

2. **Service Management**
   ```bash
   # Start specific service
   docker-compose up [service_name]

   # Restart service
   docker-compose restart [service_name]

   # Remove service
   docker-compose rm [service_name]

   # Scale service
   docker-compose up --scale [service_name]=3
   ```

3. **Container Management**
   ```bash
   # List running containers
   docker ps

   # List all containers
   docker ps -a

   # View container logs
   docker logs [container_id]

   # Execute command in container
   docker exec -it [container_id] bash
   ```

4. **Image Management**
   ```bash
   # List images
   docker images

   # Remove image
   docker rmi [image_id]

   # Remove unused images
   docker image prune
   ```

### Docker Networking

1. **Network Configuration**
   ```yaml
   networks:
     default:
       driver: bridge
   ```

2. **Service Communication**
   - Internal network: `kafka:29092`
   - External access: `localhost:9092`
   - Service discovery via Docker DNS

3. **Port Mapping**
   ```yaml
   ports:
     - "8000:8000"  # Telegram Bot
     - "8001:8001"  # Scraper
     - "8002:8002"  # Preprocessor
     - "8003:8003"  # Embedder
     - "8004:8004"  # Storage
     - "9092:9092"  # Kafka
     - "2181:2181"  # Zookeeper
   ```

### Docker Optimization

1. **Build Optimization**
   ```bash
   # Enable BuildKit
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1

   # Build with cache
   docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
   ```

2. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

3. **Health Checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

### Docker Security

1. **Security Best Practices**
   - Use non-root users
   - Scan images for vulnerabilities
   - Keep base images updated
   - Use secrets for sensitive data

2. **Environment Variables**
   ```bash
   # Set sensitive data
   docker-compose --env-file .env up
   ```

3. **Network Security**
   - Internal network isolation
   - Limited port exposure
   - Service-specific access control

### Docker Monitoring

1. **Container Monitoring**
   ```bash
   # Resource usage
   docker stats

   # Container events
   docker events

   # Container inspection
   docker inspect [container_id]
   ```

2. **Log Management**
   ```bash
   # View all logs
   docker-compose logs

   # Follow specific service
   docker-compose logs -f [service_name]

   # View last 100 lines
   docker-compose logs --tail=100
   ```

3. **Performance Monitoring**
   ```bash
   # CPU and memory usage
   docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

   # Disk usage
   docker system df
   ```

### Docker Troubleshooting

1. **Common Issues**
   ```bash
   # Clean up resources
   docker system prune

   # Reset Docker
   docker-compose down -v
   docker system prune -a

   # Check disk space
   docker system df
   ```

2. **Debug Commands**
   ```bash
   # Check container logs
   docker logs [container_id]

   # Inspect container
   docker inspect [container_id]

   # Check network
   docker network inspect [network_name]
   ```

3. **Recovery Steps**
   ```bash
   # Stop all containers
   docker-compose down

   # Remove volumes
   docker-compose down -v

   # Rebuild and start
   docker-compose up --build
   ```

## Project Structure and Components

### Core Processes

1. **Scraping Process**
   - **Purpose**: Extract messages from Telegram chats
   - **Components**:
     - `telegram_bot/main.py`: Handles user interactions
     - `scraper/main.py`: Implements message scraping
   - **Libraries Used**:
     - `python-telegram-bot`: Telegram API integration
     - `telethon`: Advanced Telegram client
     - `asyncio`: Asynchronous operations
   - **Output**: Raw message data in JSON format

2. **Preprocessing Process**
   - **Purpose**: Clean and prepare text data
   - **Components**:
     - `preprocessor/main.py`: Text cleaning and normalization
   - **Libraries Used**:
     - `pandas`: Data manipulation
     - `nltk`: Natural language processing
     - `emoji`: Emoji handling
     - `re`: Regular expressions
   - **Output**: Cleaned and structured text data

3. **Embedding and Storage Process**
   - **Purpose**: Generate and store embeddings
   - **Components**:
     - `embedder/main.py`: Embedding generation
     - `storage/main.py`: Data storage and retrieval
   - **Libraries Used**:
     - `sentence-transformers`: Text embeddings
     - `faiss`: Vector similarity search
     - `numpy`: Numerical operations
     - `torch`: Deep learning operations
   - **Output**: Vector embeddings and searchable indices

### Key Libraries and Their Roles

1. **Message Processing**
   - `python-telegram-bot`: Telegram bot framework
   - `telethon`: Telegram client library
   - `pandas`: Data manipulation and analysis
   - `nltk`: Natural language processing
   - `emoji`: Emoji handling and processing

2. **Machine Learning**
   - `sentence-transformers`: Text embedding generation
   - `torch`: Deep learning framework
   - `numpy`: Numerical computations
   - `scikit-learn`: Machine learning utilities

3. **Storage and Search**
   - `faiss`: Efficient similarity search
   - `pymongo`: MongoDB integration (optional)
   - `redis`: Caching (optional)

4. **Message Queue**
   - `confluent-kafka`: Kafka client
   - `pika`: RabbitMQ client (alternative)

5. **API and Web**
   - `fastapi`: High-performance API framework
   - `uvicorn`: ASGI server
   - `httpx`: Async HTTP client

### Data Flow Description

1. **Input Layer**
   ```
   Telegram Chat → Telegram Bot → Scraper Service
   ```
   - Receives messages from Telegram
   - Validates and formats data
   - Sends to scraping service

2. **Processing Layer**
   ```
   Scraper → Preprocessor → Embedder
   ```
   - Scrapes message content
   - Cleans and normalizes text
   - Generates embeddings

3. **Storage Layer**
   ```
   Embedder → Storage → FAISS Index
   ```
   - Stores embeddings
   - Creates searchable indices
   - Manages data persistence

### Service Descriptions

1. **Telegram Bot Service**
   - Handles user interactions
   - Routes messages to appropriate services
   - Manages bot commands and responses
   - Implements error handling and retries

2. **Scraper Service**
   - Connects to Telegram API
   - Extracts message content
   - Handles rate limiting
   - Manages session persistence

3. **Preprocessor Service**
   - Cleans text data
   - Removes unwanted content
   - Normalizes text format
   - Handles multiple languages

4. **Embedder Service**
   - Generates text embeddings
   - Manages model loading
   - Handles batch processing
   - Optimizes memory usage

5. **Storage Service**
   - Manages data persistence
   - Implements search functionality
   - Handles data indexing
   - Manages cache

[Rest of the README remains the same...] 