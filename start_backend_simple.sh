#!/bin/bash

echo "🚀 Simple Backend Starter"
echo "========================"

cd backend

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

echo "📦 Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Install with flexible versioning
pip install --upgrade pip
pip install --no-cache-dir \
    'fastapi>=0.109.0' \
    'uvicorn[standard]>=0.27.0' \
    'python-multipart>=0.0.6' \
    'slowapi>=0.1.9' \
    'langchain>=0.1.0' \
    'langchain-community>=0.0.10' \
    'langchain-chroma>=0.1.0' \
    'ollama>=0.1.6' \
    'chromadb>=0.4.22' \
    'sqlalchemy>=2.0.25' \
    'psycopg2-binary>=2.9.9' \
    'alembic>=1.13.1' \
    'python-jose[cryptography]>=3.3.0' \
    'passlib[bcrypt]>=1.7.4' \
    'python-dotenv>=1.0.0' \
    'pypdf>=4.0.0' \
    'python-docx>=1.1.0'

# Setup environment variables
export DATABASE_URL="postgresql://rag:rag@localhost:5432/ragdb"
export CHROMA_URL="http://localhost:8001"
export OLLAMA_URL="http://localhost:11434"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

# Create database tables
echo "🗄️  Setting up database..."
python -c "
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Start FastAPI
echo ""
echo "🚀 Starting backend on http://localhost:8000"
echo "   Admin UI: http://localhost:3000"
echo "   Chat UI: http://localhost:3001"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
