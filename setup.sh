#!/bin/bash

echo "🚀 RAG Chatbot Setup Script"
echo "============================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Copy env file
if [ ! -f backend/.env ]; then
    echo "📝 Creating .env file from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your settings!"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if Ollama is running
if ! docker exec rag-ollama ollama list &> /dev/null; then
    echo "❌ Ollama is not responding"
    exit 1
fi

echo "✅ Services are running!"

# Pull models
echo "📦 Downloading Ollama models (this may take a while)..."
docker exec rag-ollama ollama pull llama3
docker exec rag-ollama ollama pull nomic-embed-text

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Services:"
echo "   - Backend API: http://localhost:8001"
echo "   - API Docs: http://localhost:8001/docs"
echo "   - PostgreSQL: localhost:5432"
echo "   - ChromaDB: localhost:8000"
echo "   - Ollama: localhost:11434"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📖 Read README.md for API usage examples"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
