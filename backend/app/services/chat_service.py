from typing import List, Dict
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.document_service import DocumentService

class ChatService:
    def __init__(self):
        print(f"DEBUG: Initializing ChatService with provider: {settings.LLM_PROVIDER}")
        
        if settings.LLM_PROVIDER.lower() == "openai":
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
                raise ValueError("OPENAI_API_KEY not configured. Please set it in .env file.")
            
            print(f"DEBUG: Using OpenAI model: {settings.OPENAI_MODEL}")
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.3,
                max_tokens=1024
            )
        else:  # ollama
            print(f"DEBUG: Using Ollama model: {settings.OLLAMA_LLM_MODEL}")
            print(f"DEBUG: OLLAMA_URL: {settings.OLLAMA_URL}")
            self.llm = Ollama(
                base_url=settings.OLLAMA_URL,
                model=settings.OLLAMA_LLM_MODEL,
                temperature=0.3,
                num_predict=256,
                num_ctx=2048,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
        
        print(f"DEBUG: LLM initialized successfully")
        self.document_service = DocumentService()
    
    def format_chat_history(self, messages: List[Dict[str, str]]) -> str:
        """Format chat history for prompt"""
        formatted = []
        for msg in messages[-settings.CHAT_HISTORY_LIMIT:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['message']}")
        return "\n".join(formatted)
    
    def generate_response(self, question: str, chat_history: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Generate RAG response with multi-query retrieval.
        Returns dict with response, sources, and chunks for feedback tracking.
        """
        # Try multiple query variations to improve retrieval
        query_variations = [question]
        
        # Add semantic variations for better retrieval
        if "dress code" in question.lower() or "uniform" in question.lower() or "wear" in question.lower():
            query_variations.extend([
                "uniform requirements for training",
                "what to wear during training",
                "clothing attire for trainees",
                "dress uniform police",
                "proper attire",
                "khaki uniform",
                "clothing requirements"
            ])
        
        # Get relevant context - try all variations and combine unique results
        all_chunks = []
        all_metadatas = []
        seen_chunks = set()
        
        for query in query_variations:
            chunks, metas = self.document_service.search_similar(query, top_k=5)
            for chunk, meta in zip(chunks, metas):
                # Deduplicate chunks
                chunk_hash = hash(chunk[:100])  # Use first 100 chars as hash
                if chunk_hash not in seen_chunks:
                    seen_chunks.add(chunk_hash)
                    all_chunks.append(chunk)
                    all_metadatas.append(meta)
        
        # Limit to top results
        context_chunks = all_chunks[:settings.TOP_K_RESULTS]
        metadatas = all_metadatas[:settings.TOP_K_RESULTS]
        context = "\n\n".join(context_chunks)
        
        # Debug: Print retrieved context
        print(f"\nDEBUG: Retrieved {len(context_chunks)} chunks")
        print(f"DEBUG: Total context length: {len(context)} characters")
        if context_chunks:
            print(f"DEBUG: First chunk preview: {context_chunks[0][:200]}...")
            # Print all chunk previews to debug what's being retrieved
            for i, chunk in enumerate(context_chunks[:3]):  # First 3 chunks
                print(f"DEBUG: Chunk {i+1} preview: {chunk[:300]}...")
        
        # Extract unique source documents
        sources = set()
        for meta in metadatas:
            if 'filename' in meta:
                sources.add(meta['filename'])
        
        # Format chat history
        history = self.format_chat_history(chat_history)
        
        # Create improved prompt with better instructions
        history_section = f"Previous conversation:\n{history}\n\n" if history else ""
        
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context below. 

Context from documents:
{context}

{history_section}Question: {question}

Instructions:
- If the answer is directly stated in the context, provide a clear and complete answer
- If the context mentions the topic but doesn't provide full details (e.g., "shall be specified by X"), explain what the document says, including who/where the information can be found
- Use exact quotes from the context when relevant to show what the document states
- If the context is completely unrelated to the question, politely explain that you can only answer questions based on the uploaded Delhi Police documents

Answer:"""
        
        # Generate response
        response = self.llm.invoke(prompt)
        
        # Extract text content from response
        # OpenAI returns a message object, Ollama returns a string
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Add citations only if the response actually uses information from documents
        # Don't add citations if the response says it doesn't have information
        should_add_citation = sources and not any(phrase in response_text.lower() for phrase in [
            "i don't have information",
            "i don't know",
            "not mentioned in",
            "not provided in",
            "no information about"
        ])
        
        if should_add_citation:
            citation_text = "\n\n---\n**Sources:**\n" + "\n".join([f"• {src}" for src in sorted(sources)])
            response_text = response_text + citation_text
        
        # Return response with metadata for feedback tracking
        return {
            "response": response_text,
            "sources": list(sources),
            "retrieved_chunks": [
                {
                    "text": chunk[:500],  # First 500 chars for storage
                    "metadata": meta
                }
                for chunk, meta in zip(context_chunks, metadatas)
            ]
        }
