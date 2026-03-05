import hashlib
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
import chromadb
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from app.core.config import settings

class DocumentService:
    def __init__(self):
        # Initialize embeddings based on provider
        if settings.LLM_PROVIDER.lower() == "openai":
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
                raise ValueError("OPENAI_API_KEY not configured. Please set it in .env file.")
            print(f"DEBUG: Using OpenAI embeddings: {settings.OPENAI_EMBED_MODEL}")
            self.embeddings = OpenAIEmbeddings(
                model=settings.OPENAI_EMBED_MODEL,
                api_key=settings.OPENAI_API_KEY
            )
        else:  # ollama
            print(f"DEBUG: Using Ollama embeddings: {settings.OLLAMA_EMBED_MODEL}")
            self.embeddings = OllamaEmbeddings(
                base_url=settings.OLLAMA_URL,
                model=settings.OLLAMA_EMBED_MODEL
            )
        
        # Initialize ChromaDB client - HTTP for local/docker, embedded for Render
        if settings.CHROMA_URL and settings.CHROMA_URL.startswith("http"):
            print(f"DEBUG: Using HTTP ChromaDB client at {settings.CHROMA_URL}")
            # Simple initialization - let ChromaDB handle tenant creation
            try:
                self.chroma_client = chromadb.HttpClient(
                    host=settings.CHROMA_URL.split("://")[1].split(":")[0],
                    port=int(settings.CHROMA_URL.split(":")[-1])
                )
                # Test the connection
                self.chroma_client.heartbeat()
                print("DEBUG: ChromaDB connection successful")
            except Exception as e:
                print(f"ERROR: Failed to connect to ChromaDB: {e}")
                # Wait and retry once
                import time
                time.sleep(2)
                self.chroma_client = chromadb.HttpClient(
                    host=settings.CHROMA_URL.split("://")[1].split(":")[0],
                    port=int(settings.CHROMA_URL.split(":")[-1])
                )
        else:
            # Embedded mode for local path
            chroma_path = settings.CHROMA_URL if settings.CHROMA_URL else settings.CHROMA_PERSIST_DIR
            print(f"DEBUG: Using embedded ChromaDB at {chroma_path}")
            self.chroma_client = chromadb.PersistentClient(
                path=chroma_path
            )
        
        # Use provider-specific collection name to handle different embedding dimensions
        collection_name = settings.chroma_collection_name
        print(f"DEBUG: Using ChromaDB collection: {collection_name}")
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )
        
        # Initialize Docling converter with OCR enabled for scanned PDFs
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # Keep OCR for scanned documents
        pipeline_options.do_table_structure = True  # Keep table extraction
        pipeline_options.images_scale = 1.0  # Normal scale
        pipeline_options.generate_picture_images = False  # Skip images for speed
        
        self.doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    backend=PyPdfiumDocumentBackend
                )
            }
        )
        
        # Use simpler text splitter - Docling already provides good chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
        )
    
    def compute_file_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of file content"""
        return hashlib.sha256(content).hexdigest()

    def load_document(self, file_path: str, file_type: str) -> str:
        """Load and extract text from document using Docling"""
        if file_type == ".pdf":
            try:
                print(f"DEBUG: Using Docling to process PDF: {file_path}")
                
                import time
                start_time = time.time()
                
                # Convert document using Docling
                result = self.doc_converter.convert(file_path)
                doc = result.document
                
                conversion_time = time.time() - start_time
                
                # Quick table count
                table_count = sum(1 for item in doc.body if item.label == 'table')
                
                # Export to markdown format which preserves tables nicely
                markdown_text = doc.export_to_markdown()
                
                total_time = time.time() - start_time
                print(f"DEBUG DOCLING: Processed {len(doc.pages)} pages in {total_time:.2f}s")
                print(f"DEBUG DOCLING: Extracted {len(markdown_text)} chars, {table_count} tables")
                
                if len(markdown_text) < 10:
                    raise ValueError("PDF contains no text. The document may be blank or corrupted.")
                
                return markdown_text
                
            except Exception as e:
                print(f"ERROR loading PDF with Docling: {e}")
                raise ValueError(f"Failed to extract text from PDF: {str(e)}")
                
        elif file_type == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
                
        elif file_type == ".docx":
            try:
                print(f"DEBUG: Using Docling to process DOCX: {file_path}")
                result = self.doc_converter.convert(file_path)
                markdown_text = result.document.export_to_markdown()
                print(f"DEBUG DOCLING: Extracted {len(markdown_text)} characters from DOCX")
                return markdown_text
            except Exception as e:
                print(f"ERROR loading DOCX with Docling: {e}")
                raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into chunks"""
        docs = [LCDocument(page_content=text)]
        chunks = self.text_splitter.split_documents(docs)
        return [chunk.page_content for chunk in chunks]
    
    def store_embeddings(self, document_id: str, chunks: List[str], filename: str):
        """Store document chunks in ChromaDB with optimized batching"""
        print(f"DEBUG: Storing {len(chunks)} chunks for document {document_id}")
        print(f"DEBUG: First chunk (first 100 chars): {chunks[0][:100] if chunks else 'EMPTY'}")
        
        # Generate embeddings - OpenAI SDK already batches internally
        # But we can still monitor progress for large documents
        import time
        start_time = time.time()
        
        embeddings = self.embeddings.embed_documents(chunks)
        
        embed_time = time.time() - start_time
        print(f"DEBUG: Generated {len(embeddings)} embeddings in {embed_time:.2f}s ({len(embeddings)/embed_time:.1f} chunks/sec)")
        
        if not embeddings or len(embeddings) == 0:
            raise ValueError(f"Failed to generate embeddings for {len(chunks)} chunks")
        
        # Store in ChromaDB - also batched internally
        store_start = time.time()
        self.collection.add(
            ids=[f"{document_id}_{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i
            } for i in range(len(chunks))]
        )
        store_time = time.time() - store_start
        print(f"DEBUG: Stored in ChromaDB in {store_time:.2f}s")
        print(f"DEBUG: Total embedding+storage time: {embed_time + store_time:.2f}s")
    
    def delete_embeddings(self, document_id: str):
        """Delete all embeddings for a document"""
        self.collection.delete(where={"document_id": document_id})
    
    def search_similar(self, query: str, top_k: int = None) -> tuple[List[str], List[dict]]:
        """Search for similar chunks and return chunks with metadata"""
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        query_embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        chunks = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        return chunks, metadatas
