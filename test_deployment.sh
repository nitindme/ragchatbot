#!/bin/bash

# 🧪 Local Deployment Test Script
# Tests the chatbot locally before deploying to cloud

set -e  # Exit on error

echo "🚀 Delhi Police RAG Chatbot - Local Deployment Test"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env and add your OPENAI_API_KEY${NC}"
    echo ""
    read -p "Press Enter when you've added your OPENAI_API_KEY to .env..."
fi

# Check if OpenAI API key is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your-openai-api-key-here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set in .env file${NC}"
    echo "Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo -e "${GREEN}✅ Environment file configured${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Stop any running containers
echo "🛑 Stopping any existing containers..."
docker-compose down -v 2>/dev/null || true
echo ""

# Start services
echo "🐳 Starting services with Docker Compose..."
echo "   - PostgreSQL (Database)"
echo "   - Backend (FastAPI + ChromaDB embedded)"
echo ""
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
BACKEND_URL="http://localhost:8000"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "${BACKEND_URL}/health" > /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check logs with: docker-compose logs backend"
    exit 1
fi

echo ""
echo "🧪 Running test queries..."
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
HEALTH_RESPONSE=$(curl -s "${BACKEND_URL}/health")
echo "Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Pass${NC}"
else
    echo -e "${RED}❌ Fail${NC}"
fi
echo ""

# Test 2: Check if OpenAI connection works
echo "Test 2: OpenAI Connection"
# Create a test conversation
CHAT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hello, can you hear me?",
        "conversation_id": "test-123"
    }')

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✅ OpenAI connection successful${NC}"
    echo "Response preview: $(echo $CHAT_RESPONSE | head -c 100)..."
else
    echo -e "${RED}❌ OpenAI connection failed${NC}"
    echo "Response: $CHAT_RESPONSE"
    echo "Please check your OPENAI_API_KEY in .env"
fi
echo ""

# Test 3: Document upload endpoint
echo "Test 3: Document Upload Endpoint (without file)"
UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" "${BACKEND_URL}/api/documents/upload" || true)
HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "422" ] || [ "$HTTP_CODE" == "401" ]; then
    echo -e "${GREEN}✅ Endpoint responding (requires auth)${NC}"
else
    echo -e "${YELLOW}⚠️  Endpoint returned: HTTP $HTTP_CODE${NC}"
fi
echo ""

# Test 4: Check database connection
echo "Test 4: Database Connection"
DB_TEST=$(docker-compose exec -T postgres psql -U rag -d ragdb -c "SELECT 1;" 2>&1 || true)
if echo "$DB_TEST" | grep -q "1 row"; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
fi
echo ""

# Test 5: Check ChromaDB embedded mode
echo "Test 5: ChromaDB Embedded Mode"
if docker-compose logs backend | grep -q "Using embedded ChromaDB"; then
    echo -e "${GREEN}✅ ChromaDB running in embedded mode${NC}"
elif docker-compose logs backend | grep -q "Using HTTP ChromaDB"; then
    echo -e "${YELLOW}⚠️  ChromaDB running in HTTP mode (old config)${NC}"
    echo "Update docker-compose.yml to use embedded mode"
else
    echo -e "${RED}❌ ChromaDB status unknown${NC}"
fi
echo ""

echo "=================================================="
echo "📊 Test Summary"
echo "=================================================="
echo ""
echo "Backend URL:  ${BACKEND_URL}"
echo "API Docs:     ${BACKEND_URL}/docs"
echo "Health Check: ${BACKEND_URL}/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f backend"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To start frontend apps:"
echo "  cd frontend/admin && npm install && npm run dev"
echo "  cd frontend/chat && npm install && npm run dev"
echo ""
echo -e "${GREEN}🎉 Local testing complete!${NC}"
echo ""
echo "If all tests passed, you're ready to deploy to Render/Vercel."
echo "See DEPLOYMENT_GUIDE.md for detailed instructions."
echo ""
