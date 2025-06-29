# Telegram Chat Analysis Microservices

A comprehensive microservices architecture for analyzing Telegram chat data using advanced NLP techniques, including text preprocessing, embedding generation, and semantic search capabilities.

## Project Structure

```
Project/
├── src/
│   ├── scraper/                 # Telegram message scraping service
│   │   ├── telegram_scraper.py  # Main scraper implementation
│   │   ├── utils/              # Scraper utilities
│   │   └── data/               # Scraped data storage
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
├── services/                 # Docker service configurations
│   ├── scraper/
│   │   ├── Dockerfile       # Scraper service Dockerfile
│   │   └── main.py          # Service entry point
│   ├── preprocessor/
│   │   ├── Dockerfile       # Preprocessor service Dockerfile
│   │   └── main.py          # Service entry point
│   ├── embedder/
│   │   ├── Dockerfile       # Embedder service Dockerfile
│   │   └── main.py          # Service entry point
│   ├── storage/
│   │   ├── Dockerfile       # Storage service Dockerfile
│   │   └── main.py          # Service entry point
│   ├── telegram_bot/
│   │   ├── Dockerfile       # Bot service Dockerfile
│   │   └── main.py          # Service entry point
│   └── common/              # Shared utilities
│
├── data/                    # Data directory
│   ├── bulk_exports/        # Raw scraped data exports
│   ├── preprocessed/        # Cleaned and processed data
│   ├── embeddings/          # Generated embeddings
│   └── telegram_messages.db # SQLite database
│
├── Embeddings/             # Embedding analysis outputs
│   ├── embeddings_graph.graphml
│   ├── embeddings_graph.png
│   ├── embeddings_heatmap.png
│   ├── embeddings_tsne.png
│   └── faiss_index.pkl
│
├── requirements.txt        # Project dependencies
├── docker-compose.yml     # Docker compose configuration
├── .dockerignore          # Docker ignore file
└── README.md             # Project documentation
```

## Services Overview

### 1. Scraper Service (`src/scraper/`)
- **Purpose**: Handles Telegram message scraping from channels and groups
- **Features**: 
  - Session management and authentication
  - Rate limiting and error handling
  - Raw message storage in JSON format
  - Support for multiple chat sources
- **Port**: 8001

### 2. Preprocessor Service (`src/preprocessor/`)
- **Purpose**: Cleans and normalizes text data for analysis
- **Features**:
  - Text cleaning and noise removal
  - Multi-language support (including Amharic)
  - Tokenization and stopword removal
  - Date feature extraction
  - Message statistics calculation
- **Port**: 8002

### 3. Embedder Service (`src/embedder/`)
- **Purpose**: Generates high-quality text embeddings
- **Features**:
  - XLM-RoBERTa model integration
  - Afro-XLM-RoBERTa for African languages
  - Batch processing capabilities
  - Model caching and optimization
  - 1024-dimensional embeddings
- **Port**: 8003

### 4. Storage Service (`src/storage/`)
- **Purpose**: Manages data persistence and search functionality
- **Features**:
  - FAISS index management
  - Vector similarity search
  - Data versioning and backup
  - Query optimization
  - Metadata management
- **Port**: 8004

### 5. Telegram Bot Service (`src/bot/`)
- **Purpose**: Provides user interface for chat analysis
- **Features**:
  - Interactive Telegram bot interface
  - Search command handling
  - User session management
  - Real-time query processing
  - Response formatting
- **Port**: 8000

## Docker Setup and Running Instructions

### Prerequisites

1. **Install Docker and Docker Compose**
   ```bash
   # For Windows/Mac: Install Docker Desktop
   # For Linux: Install Docker Engine and Docker Compose
   ```

2. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

### Docker Commands and Descriptions

#### 1. Building Docker Images

**Build all services:**
```bash
docker-compose build
```
**Description**: Creates Docker images for all microservices. This command:
- Reads the `docker-compose.yml` configuration
- Builds each service using its respective Dockerfile
- Installs Python dependencies from `requirements.txt`
- Copies source code and configurations
- Creates optimized layers for caching

**Build specific service:**
```bash
docker-compose build [service_name]
```
**Available services**: `preprocessor`, `embedder`, `scraper`, `storage`, `telegram_bot`

**Example:**
```bash
docker-compose build preprocessor
```
**Description**: Builds only the preprocessor service image, useful for development and testing individual components.

#### 2. Running Services

**Start all services:**
```bash
docker-compose up
```
**Description**: Starts all microservices in the background. This command:
- Creates and starts containers for all services
- Sets up networking between services
- Mounts data volumes for persistence
- Starts Kafka and Zookeeper for message queuing

**Start services in detached mode:**
```bash
docker-compose up -d
```
**Description**: Runs all services in the background (detached mode), allowing you to continue using the terminal.

**Start specific service:**
```bash
docker-compose up [service_name]
```
**Example:**
```bash
docker-compose up preprocessor
```
**Description**: Starts only the specified service and its dependencies.

**Start with rebuild:**
```bash
docker-compose up --build
```
**Description**: Forces rebuilding of all images before starting services, ensuring the latest code changes are included.

#### 3. Service Management

**View running services:**
```bash
docker-compose ps
```
**Description**: Shows the status of all services, including:
- Container names and IDs
- Service status (running, stopped, etc.)
- Port mappings
- Health status

**View service logs:**
```bash
docker-compose logs [service_name]
```
**Example:**
```bash
docker-compose logs preprocessor
```
**Description**: Displays logs for the specified service, useful for debugging and monitoring.

**View all logs:**
```bash
docker-compose logs
```
**Description**: Shows logs from all services in chronological order.

**Follow logs in real-time:**
```bash
docker-compose logs -f [service_name]
```
**Description**: Continuously displays new log entries as they are generated.

#### 4. Stopping and Cleaning

**Stop all services:**
```bash
docker-compose down
```
**Description**: Stops and removes all containers, networks, and volumes created by docker-compose.

**Stop specific service:**
```bash
docker-compose stop [service_name]
```
**Description**: Stops the specified service while keeping other services running.

**Remove containers and volumes:**
```bash
docker-compose down -v
```
**Description**: Stops services and removes all associated volumes, effectively resetting the data.

**Remove everything including images:**
```bash
docker-compose down --rmi all
```
**Description**: Stops services, removes containers, networks, volumes, and all images.

#### 5. Development and Debugging

**Execute commands in running container:**
```bash
docker-compose exec [service_name] [command]
```
**Example:**
```bash
docker-compose exec preprocessor python -c "print('Hello from container')"
```
**Description**: Runs a command inside a running container, useful for debugging and testing.

**Access container shell:**
```bash
docker-compose exec [service_name] bash
```
**Description**: Opens an interactive shell inside the specified container.

**Restart specific service:**
```bash
docker-compose restart [service_name]
```
**Description**: Restarts the specified service without affecting other services.

**Scale services:**
```bash
docker-compose up --scale [service_name]=[number]
```
**Example:**
```bash
docker-compose up --scale preprocessor=3
```
**Description**: Runs multiple instances of a service for load balancing and high availability.

### Complete Setup Workflow

1. **Initial Setup**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd Project
   
   # Build all services
   docker-compose build
   ```

2. **Start the Application**
   ```bash
   # Start all services in detached mode
   docker-compose up -d
   
   # Verify all services are running
   docker-compose ps
   ```

3. **Monitor the Application**
   ```bash
   # View logs from all services
   docker-compose logs -f
   
   # View logs from specific service
   docker-compose logs -f preprocessor
   ```

4. **Development Workflow**
   ```bash
   # Make code changes
   # Rebuild specific service
   docker-compose build preprocessor
   
   # Restart service to apply changes
   docker-compose restart preprocessor
   ```

5. **Cleanup**
   ```bash
   # Stop all services
   docker-compose down
   
   # Complete cleanup (removes data)
   docker-compose down -v
   ```

### Service Ports and Access

| Service | Port | Description |
|---------|------|-------------|
| Telegram Bot | 8000 | Bot API endpoint |
| Scraper | 8001 | Scraper service API |
| Preprocessor | 8002 | Preprocessing service API |
| Embedder | 8003 | Embedding service API |
| Storage | 8004 | Storage service API |
| Kafka | 9092 | Message broker |
| Zookeeper | 2181 | Kafka coordination |

### Troubleshooting

**Common Issues and Solutions:**

1. **Port conflicts:**
   ```bash
   # Check what's using a port
   netstat -ano | findstr :8000
   
   # Stop conflicting service or change port in docker-compose.yml
   ```

2. **Build failures:**
   ```bash
   # Clear Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

3. **Service not starting:**
   ```bash
   # Check service logs
   docker-compose logs [service_name]
   
   # Check service status
   docker-compose ps
   ```

4. **Data persistence issues:**
   ```bash
   # Check volume mounts
   docker volume ls
   
   # Inspect volume contents
   docker run -it -v [volume_name]:/data alpine ls /data
   ```

## Development

### Local Development Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # Create .env file with your configuration
   cp .env.example .env
   ```

3. **Run Individual Services**
   ```bash
   # Run preprocessor locally
   python services/preprocessor/main.py
   
   # Run embedder locally
   python services/embedder/main.py
   ```

### Testing

```bash
# Run all tests
pytest

# Run specific service tests
pytest tests/[service_name]

# Run with coverage
pytest --cov=src/
```

## Monitoring and Logging

### Health Checks
Each service exposes a `/health` endpoint for monitoring:
- `http://localhost:8000/health` - Bot service
- `http://localhost:8001/health` - Scraper service
- `http://localhost:8002/health` - Preprocessor service
- `http://localhost:8003/health` - Embedder service
- `http://localhost:8004/health` - Storage service

### Performance Metrics
- Message processing rate
- Embedding generation time
- Search response time
- Resource utilization (CPU, Memory, Disk)

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
