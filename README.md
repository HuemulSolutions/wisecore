# Wisecore - Huemul Solutions

**To test wisecore locally, refer to the following link:** https://github.com/HuemulSolutions/wisecore-orch 

version 0.4

## Description

Wisecore is an advanced AI-powered knowledge management platform that enables automated generation of business documents. The application uses multiple Large Language Models (LLMs) to generate structured content based on customizable templates and domain-specific context.

## Key Features

- **Automated Document Generation**: Document creation using AI with multiple LLM models
- **Customizable Templates**: Template system with interdependent sections
- **Multiple LLM Models**: Support for GPT-4.1, Claude Sonnet-4, Llama-4 Maverick, GPT-OSS, and Granite-4
- **Integrated Chatbot**: Conversational interaction with generated content
- **Context Management**: Advanced context system and dependencies between sections
- **RESTful API**: Complete interface for integration with other applications
- **Real-time Streaming**: Content generation with real-time response
- **PostgreSQL Database**: Robust storage with vector support
- **Organization System**: Multi-tenant management with folders and document types

## Technical Architecture

### Core Technologies

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy with async support
- **AI/LLM**: LangChain, LangGraph
- **Migrations**: Alembic
- **Containerization**: Docker

### Project Structure

```
src/
├── chatbot/          # Conversational chatbot system
├── database/         # Data models and repositories
├── graph/           # Generation flow logic (LangGraph)
├── llm/             # Language model integration
├── routes/          # API endpoints
├── services/        # Business logic
├── config.py        # Application configuration
├── main.py          # Application entry point
└── schemas.py       # Validation schemas (Pydantic)
```

## Database Models

The system handles the following main entities:

- **Organizations**: Organizations with multi-tenant management
- **Documents**: Base documents with metadata and description
- **Templates**: Reusable templates with structured sections
- **Sections**: Individual sections with prompts and dependencies
- **Executions**: Generation executions with state and LLM model
- **Folders**: Hierarchical organization system
- **DocumentTypes**: Document classification with colors
- **Context**: Additional context to improve generation
- **LLM**: Available language model configuration

## API Endpoints

### Document Generation
- `POST /generation/stream` - Stream document generation
- `POST /generation/generate_document` - Complete document generation
- `POST /generation/fix_section` - Fix specific sections
- `POST /generation/redact_section_prompt` - Improve section prompts
- `POST /generation/chatbot` - Chatbot interaction

### Document Management
- `GET /documents/` - List documents
- `POST /documents/` - Create documents
- `GET /documents/{id}` - Get specific document
- `PUT /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document

### Templates and Sections
- `GET /templates/` - List templates
- `POST /templates/` - Create template
- `GET /sections/` - List sections
- `POST /sections/` - Create section

### Executions
- `GET /executions/` - List executions
- `POST /executions/` - Create execution
- `GET /executions/{id}/status` - Execution status

### LLM Management
- `GET /llms/` - List available models

## Generation Flow

1. **Entrypoint**: Context and configuration initialization
2. **Sort Sections**: Section ordering by dependencies
3. **Get Dependencies**: Resolution of dependencies between sections
4. **Execute Section**: Content generation using LLM
5. **Save Section Execution**: Persistence of generated content
6. **Should Continue**: Process continuity evaluation
7. **End Execution**: Finalization and consolidation

## Supported LLM Models

- **GPT-4.1**: Advanced OpenAI model
- **Claude Sonnet-4**: Anthropic model
- **Llama-4 Maverick**: Optimized Meta model
- **GPT-OSS**: Open source version
- **Granite-4**: IBM model

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/wisecore
ENVIRONMENT=LOCAL
ALEMBIC_DATABASE_URL=postgresql://user:password@localhost/wisecore
DEFAULT_LLM=gpt-4.1
MODEL_GATEWAY_URL=https://your-model-gateway.com
MODEL_GATEWAY_APIKEY=your-api-key
```

## Installation and Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- Docker (optional)

### Local Installation

1. Clone the repository
```bash
git clone https://github.com/HuemulSolutions/wisecore.git
cd wisecore
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup database
```bash
# Create PostgreSQL database
# Run migrations
alembic upgrade head
```

5. Configure environment variables
```bash
cp .env.example .env.dev
# Edit .env.dev with your configurations
```

6. Run the application
```bash
uvicorn src.main:app --reload
```

### Docker Installation

```bash
docker build -t wisecore .
docker run -p 8000:8000 wisecore
```

## Basic Usage

### Create an Organization
```python
POST /organizations/
{
    "name": "My Company",
    "description": "Company description"
}
```

### Create a Document
```python
POST /documents/
{
    "name": "Monthly Report",
    "description": "Monthly sales report",
    "organization_id": "organization-uuid"
}
```

### Generate Content
```python
POST /generation/generate_document
{
    "document_id": "document-uuid",
    "execution_id": "execution-uuid",
    "instructions": "Generate with focus on Q4 metrics"
}
```


### Migration Structure
Migrations are handled with Alembic. To create a new migration:

```bash
alembic revision --autogenerate -m "Change description"
alembic upgrade head
```

## License


## Support

For technical support or inquiries, contact the Huemul Solutions team.