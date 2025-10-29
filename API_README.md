# 🚀 AI Documentation Generator API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.120.2-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-000000)](https://ollama.ai/)

A **production-ready RESTful API** for automated documentation generation using local AI models. Built with FastAPI, this server provides async task processing, real-time progress tracking, and comprehensive documentation generation for any software project.

## ✨ Features

- 🔐 **100% Local & Private** - All AI processing happens on your machine
- 🚀 **Async Task Processing** - Non-blocking documentation generation with background tasks
- 📊 **Real-time Progress Tracking** - Monitor task status and completion percentage
- 📦 **ZIP File Upload Support** - Analyze projects via file upload or local path
- ⚙️ **Configurable Everything** - Customize AI models, documentation style, and output
- 📚 **Auto-generated API Docs** - Interactive Swagger UI and ReDoc interfaces
- 🔄 **CORS Enabled** - Safe cross-origin requests for frontend integration
- 🐳 **Docker Ready** - Containerized deployment with Docker support
- ✅ **Production Tested** - Comprehensive error handling and logging

## 📋 Prerequisites

Before running the API server, ensure you have:

1. **Python 3.11+** installed
2. **Ollama** running locally:
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama serve
   
   # Pull a model (required)
   ollama pull llama3.2
   # Or use codellama for code-focused documentation
   ollama pull codellama
   ```

## 🛠️ Installation

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-doc-generator.git
cd ai-doc-generator

# Install dependencies
pip install -e .

# Create environment file (optional)
cp .env.example .env
# Edit .env with your settings

# Start the server
python -m src.api.main
# Or use uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 5000 --reload
```

### Option 2: Docker

```bash
# Build the image
docker build -t ai-doc-generator-api .

# Run the container
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  ai-doc-generator-api
```

## 🚦 Quick Start

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:5000/
- **ReDoc**: http://localhost:5000/redoc

### Example: Generate Documentation

```bash
# 1. Start a documentation generation task
curl -X POST "http://localhost:5000/analyze" \
  -F "project_path=/path/to/your/project" \
  -F "model_name=llama3.2" \
  -F "overwrite=false"

# Response:
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "pending",
#   "message": "Documentation generation started",
#   "created_at": "2025-10-29T10:30:00"
# }

# 2. Check task progress
curl "http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000"

# 3. Get generated documentation (when complete)
curl "http://localhost:5000/docs/550e8400-e29b-41d4-a716-446655440000"

# 4. Get AI-generated summary
curl "http://localhost:5000/summary/550e8400-e29b-41d4-a716-446655440000"
```

## 📡 API Endpoints

### `POST /analyze`
Start documentation generation for a project.

**Parameters:**
- `project_path` (string, optional): Local path to project directory
- `zip_file` (file, optional): ZIP file containing the project
- `config_overrides` (JSON string, optional): Configuration overrides
- `model_name` (string, optional): Ollama model to use
- `overwrite` (boolean): Overwrite existing files (default: false)

**Response:**
```json
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Documentation generation started",
  "created_at": "2025-10-29T10:30:00"
}
```

### `GET /status/{task_id}`
Get real-time status of a documentation task.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "running",
  "progress": 60,
  "current_step": "Generating documentation",
  "message": "Running AI workflow",
  "started_at": "2025-10-29T10:30:01",
  "completed_at": null,
  "error": null,
  "result": null
}
```

### `GET /docs/{task_id}`
Retrieve generated documentation files.

**Response:**
```json
{
  "documentation": {
    "README.md": "# Project Name\n...",
    "ARCHITECTURE.md": "# Architecture\n...",
    "API.md": "# API Reference\n..."
  },
  "format": "markdown",
  "task_id": "uuid"
}
```

### `GET /summary/{task_id}`
Get AI-generated project summary.

**Response:**
```json
{
  "summary": "This project is a FastAPI-based REST API...",
  "task_id": "uuid",
  "project_name": "ai-doc-generator",
  "languages": ["Python", "JavaScript"],
  "frameworks": ["FastAPI", "React"]
}
```

### `GET /config`
Get current configuration settings.

### `PUT /config`
Update configuration settings.

**Request Body:**
```json
{
  "config": {
    "ollama": {
      "model": "codellama",
      "temperature": 0.2
    },
    "documentation": {
      "style": "professional",
      "verbosity": "detailed"
    }
  }
}
```

### `GET /health`
Health check endpoint.

### `GET /info`
API information and capabilities.

## ⚙️ Configuration

Configuration can be set via environment variables or `.env` file:

```bash
# Server Settings
API_HOST=0.0.0.0
API_PORT=5000
API_RELOAD=true
LOG_LEVEL=info

# CORS Settings
CORS_ORIGINS=*

# Upload Settings
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=100

# Ollama Settings (via config.yaml)
CONFIG_PATH=config.yaml
```

### Configuration File (config.yaml)

Create a `config.yaml` for persistent settings:

```yaml
ollama:
  base_url: http://localhost:11434
  model: llama3.2
  temperature: 0.3
  timeout: 120

documentation:
  style: professional  # professional, casual, technical
  tone: clear         # clear, friendly, formal
  verbosity: detailed # concise, moderate, detailed
  include_emojis: true
  include_badges: true
  include_table_of_contents: true

output:
  docs_directory: docs
  create_readme: true
  create_api_docs: true
  create_architecture_docs: true
  overwrite_existing: false

advanced:
  generate_summary: true
  analyze_dependencies: true
  enable_markdown_enhancements: true
  enable_seo_optimization: true
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build
docker build -t ai-doc-generator-api .

# Run with environment variables
docker run -d \
  --name doc-generator-api \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  ai-doc-generator-api
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./config.yaml:/app/config.yaml
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=5000
      - OLLAMA_URL=http://host.docker.internal:11434
    restart: unless-stopped
```

## 📊 Usage Examples

### Python Client

```python
import requests
import time

API_URL = "http://localhost:5000"

# Start documentation generation
response = requests.post(
    f"{API_URL}/analyze",
    data={
        "project_path": "/path/to/project",
        "model_name": "llama3.2",
        "overwrite": False
    }
)
task_id = response.json()["task_id"]

# Poll for completion
while True:
    status = requests.get(f"{API_URL}/status/{task_id}").json()
    print(f"Progress: {status['progress']}% - {status['message']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)

# Get documentation
if status['status'] == 'completed':
    docs = requests.get(f"{API_URL}/docs/{task_id}").json()
    print("Generated files:", list(docs['documentation'].keys()))
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';

async function generateDocs(projectPath) {
  // Start task
  const { data } = await axios.post(`${API_URL}/analyze`, {
    project_path: projectPath,
    model_name: 'llama3.2'
  }, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  const taskId = data.task_id;
  
  // Poll for completion
  while (true) {
    const status = await axios.get(`${API_URL}/status/${taskId}`);
    console.log(`Progress: ${status.data.progress}%`);
    
    if (['completed', 'failed'].includes(status.data.status)) {
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  // Get docs
  const docs = await axios.get(`${API_URL}/docs/${taskId}`);
  return docs.data;
}
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/api --cov-report=html
```

## 📁 Project Structure

```
ai-doc-generator/
├── src/
│   ├── api/                    # FastAPI server
│   │   ├── core/              # Core functionality
│   │   │   ├── config_manager.py
│   │   │   └── task_manager.py
│   │   ├── models/            # Pydantic models
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── routes/            # API endpoints
│   │   │   ├── analyze.py
│   │   │   ├── status.py
│   │   │   ├── docs.py
│   │   │   ├── config.py
│   │   │   └── summary.py
│   │   ├── services/          # Business logic
│   │   │   └── documentation_service.py
│   │   └── main.py            # FastAPI app
│   └── docgen/                # CLI tool (reused by API)
│       ├── core/
│       ├── generators/
│       └── analyzers/
├── tests/                     # Unit tests
├── uploads/                   # Upload directory
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Docker Compose config
├── .env.example              # Environment template
├── API_README.md             # This file
└── pyproject.toml            # Package config
```

## 🔒 Security Best Practices

- **API Keys**: Never commit API keys or secrets to version control
- **CORS**: Configure `CORS_ORIGINS` to restrict allowed origins in production
- **File Uploads**: Validate and scan uploaded files before processing
- **Rate Limiting**: Consider adding rate limiting for production deployments
- **Authentication**: Add authentication middleware for public deployments

## 🐛 Troubleshooting

### "Connection refused" to Ollama

Ensure Ollama is running:
```bash
ollama serve
```

### "Task failed" errors

Check logs for detailed error messages:
```bash
# View server logs
tail -f /path/to/logs

# Check Ollama logs
journalctl -u ollama -f
```

### ZIP file upload fails

Ensure upload directory exists and has write permissions:
```bash
mkdir -p uploads
chmod 755 uploads
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/ai-doc-generator/issues
- Documentation: http://localhost:5000/docs

---

Built with ❤️ using FastAPI, Ollama, LangChain, and LangGraph
