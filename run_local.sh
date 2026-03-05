#!/bin/bash

echo "🚀 Starting RAG Chatbot (Local Mode)"
echo "===================================="

# Check if Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Please install it first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3.11 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your settings!"
fi

# Start just Ollama, Postgres, and ChromaDB with Docker
echo "🐳 Starting infrastructure services (Ollama, PostgreSQL, ChromaDB)..."
cd ..
docker-compose up -d ollama postgres chroma

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Pull Ollama model if needed
echo "📥 Checking Ollama model..."
docker exec delhipolicechatbot-ollama-1 ollama list || docker exec delhipolicechatbot-ollama-1 ollama pull llama2

# Run database migrations
echo "🗄️  Setting up database..."
cd backend
export DATABASE_URL="postgresql://rag_user:rag_password@localhost:5432/rag_db"
export CHROMA_URL="http://localhost:8001"
export OLLAMA_URL="http://localhost:11434"

python -c "
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Start FastAPI server
echo "🚀 Starting FastAPI backend..."
echo "   Backend API: http://localhost:8000"
echo "   Admin UI: http://localhost:3000"
echo "   Chat UI: http://localhost:3001"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
