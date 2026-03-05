import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://rag:rag@postgres:5432/ragdb"
    
    # ChromaDB
    CHROMA_URL: str = "http://chroma:8000"
    CHROMA_PERSIST_DIR: str = "./chroma_data"  # For embedded mode on Render
    CHROMA_COLLECTION: str = "documents"  # Will be suffixed with provider name
    
    # LLM Provider (openai or ollama)
    LLM_PROVIDER: str = "ollama"  # Change to "openai" to use OpenAI
    
    @property
    def chroma_collection_name(self) -> str:
        """Get collection name with provider suffix to handle different dimensions."""
        return f"{self.CHROMA_COLLECTION}_{self.LLM_PROVIDER}"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # or gpt-4, gpt-3.5-turbo
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    
    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_LLM_MODEL: str = "llama3.2:1b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin credentials (change in production)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".docx"}
    
    # RAG
    CHUNK_SIZE: int = 1000  # Reduced from 1500 for faster processing
    CHUNK_OVERLAP: int = 200  # Reduced from 300
    TOP_K_RESULTS: int = 6  # Reduced from 8 for faster retrieval
    CHAT_HISTORY_LIMIT: int = 5  # Reduced from 10 to 5 for shorter context
    
    class Config:
        env_file = ".env"

settings = Settings()
