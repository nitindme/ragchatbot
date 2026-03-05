# RAG Chatbot with Ollama - Workspace Instructions

## Project Overview
Local RAG chatbot using Ollama with admin document management, deduplication, conversation history, and Dockerized deployment.

## Tech Stack
- **Backend**: FastAPI, LangChain, Ollama, ChromaDB, PostgreSQL
- **Frontend**: React/Next.js (Admin UI), React (Public Chat UI)
- **Infrastructure**: Docker, Docker Compose

## Project Checklist

- [x] Create copilot-instructions.md file
- [x] Get project setup information
- [x] Create project structure
- [x] Create backend API
- [x] Create Docker setup
- [x] Create frontend UIs  
- [x] Create documentation

## Key Features
- SHA256 deduplication
- ChromaDB cleanup on delete
- JWT authentication for admin
- Conversation history in PostgreSQL
- RAG with context + chat history
