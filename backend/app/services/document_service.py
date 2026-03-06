import hashlib
import os
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

    def load_document(self, file_path: str, file_type: str, progress_callback=None) -> tuple[str, int]:
        """Load and extract text from document using Docling
        
        Args:
            file_path: Path to the document file
            file_type: File extension (.pdf, .txt, .docx)
            progress_callback: Optional callback function(progress_percent) for progress updates
            
        Returns:
            tuple: (extracted_text, page_count)
        """
        if file_type == ".pdf":
            try:
                print(f"DEBUG: Using Docling to process PDF: {file_path}")
                
                import time
                import threading
                start_time = time.time()
                
                # Start a background thread to report progress during conversion
                conversion_done = threading.Event()
                
                def report_progress():
                    """Report progress estimates while conversion is running"""
                    if not progress_callback:
                        return
                    
                    # Progress from 30% to 85% over the conversion time
                    # Increment steadily every 10 seconds
                    
                    while not conversion_done.is_set():
                        time.sleep(10)  # Update every 10 seconds
                        elapsed = time.time() - start_time
                        
                        # Progress formula: 30% + (elapsed/20) * 55, capped at 85%
                        # This gives ~3% increase every 10 seconds
                        # 10s->32%, 30s->37%, 60s->47%, 120s->63%, 180s->79%, 200s->85%
                        progress_increment = (elapsed / 20.0) * 55
                        current_progress = min(85, int(30 + progress_increment))
                        
                        progress_callback(current_progress)
                        print(f"   📄 OCR progress: {current_progress}% ({elapsed:.0f}s elapsed)")
                
                # Start progress reporting thread
                progress_thread = threading.Thread(target=report_progress, daemon=True)
                progress_thread.start()
                
                # Convert document using Docling
                print(f"DEBUG: Starting Docling converter.convert()...")
                result = self.doc_converter.convert(file_path)
                
                # Stop progress reporting
                conversion_done.set()
                progress_thread.join(timeout=1)
                
                print(f"DEBUG: Docling conversion complete! Processing result...")
                doc = result.document
                page_count = len(doc.pages)
                print(f"DEBUG: Document object retrieved, pages: {page_count}")
                
                conversion_time = time.time() - start_time
                print(f"DEBUG: Conversion took {conversion_time:.2f}s")
                
                # Export to markdown format which preserves tables nicely
                print(f"DEBUG: Exporting to markdown...")
                markdown_text = doc.export_to_markdown()
                print(f"DEBUG: Markdown export complete! Length: {len(markdown_text)} chars")
                
                # Quick table count from markdown (safer than iterating body structure)
                table_count = markdown_text.count('|---') if '|' in markdown_text else 0
                
                total_time = time.time() - start_time
                print(f"DEBUG DOCLING: Processed {page_count} pages in {total_time:.2f}s")
                print(f"DEBUG DOCLING: Extracted {len(markdown_text)} chars, ~{table_count} tables")
                
                if len(markdown_text) < 10:
                    raise ValueError("PDF contains no text. The document may be blank or corrupted.")
                
                return markdown_text, page_count
                
            except Exception as e:
                print(f"ERROR loading PDF with Docling: {e}")
                raise ValueError(f"Failed to extract text from PDF: {str(e)}")
                
        elif file_type == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                return text, 1  # Text files count as 1 page
                
        elif file_type == ".docx":
            try:
                print(f"DEBUG: Using Docling to process DOCX: {file_path}")
                result = self.doc_converter.convert(file_path)
                markdown_text = result.document.export_to_markdown()
                page_count = len(result.document.pages)
                print(f"DEBUG DOCLING: Extracted {len(markdown_text)} characters from DOCX ({page_count} pages)")
                return markdown_text, page_count
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
        """Store document chunks in ChromaDB with optimized batch processing"""
        print(f"DEBUG: Storing {len(chunks)} chunks for document {document_id}")
        print(f"DEBUG: First chunk (first 100 chars): {chunks[0][:100] if chunks else 'EMPTY'}")
        
        import time
        start_time = time.time()
        
        # Process in batches for better performance and memory management
        BATCH_SIZE = 100  # Process 100 chunks at a time
        all_embeddings = []
        
        total_chunks = len(chunks)
        batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division
        
        print(f"DEBUG: Processing {total_chunks} chunks in {batches} batch(es) of {BATCH_SIZE}")
        
        for i in range(0, total_chunks, BATCH_SIZE):
            batch_start = time.time()
            batch_chunks = chunks[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            
            # Generate embeddings for this batch
            batch_embeddings = self.embeddings.embed_documents(batch_chunks)
            all_embeddings.extend(batch_embeddings)
            
            batch_time = time.time() - batch_start
            print(f"DEBUG: Batch {batch_num}/{batches}: {len(batch_chunks)} chunks in {batch_time:.2f}s ({len(batch_chunks)/batch_time:.1f} chunks/sec)")
        
        embed_time = time.time() - start_time
        avg_rate = total_chunks / embed_time if embed_time > 0 else 0
        print(f"DEBUG: Total embedding time: {embed_time:.2f}s (avg {avg_rate:.1f} chunks/sec)")
        
        if not all_embeddings or len(all_embeddings) == 0:
            raise ValueError(f"Failed to generate embeddings for {len(chunks)} chunks")
        
        # Store in ChromaDB in one batch for efficiency
        store_start = time.time()
        self.collection.add(
            ids=[f"{document_id}_{i}" for i in range(len(chunks))],
            embeddings=all_embeddings,
            documents=chunks,
            metadatas=[{
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i
            } for i in range(len(chunks))]
        )
        store_time = time.time() - store_start
        print(f"DEBUG: Stored in ChromaDB in {store_time:.2f}s")
        print(f"DEBUG: ✅ Total time: {embed_time + store_time:.2f}s for {total_chunks} chunks")
    
    def process_pdf(self, content: bytes, filename: str, document_id: str, progress_callback=None) -> dict:
        """Process PDF with Docling and store embeddings, return metadata
        
        Args:
            content: File content as bytes
            filename: Original filename
            document_id: Unique document identifier
            progress_callback: Optional callback(progress_percent: int) for progress updates
            
        Returns:
            dict with total_chunks, page_count, processing_time
        """
        import time
        import tempfile
        
        print(f"📄 Starting PDF processing for: {filename} (ID: {document_id})")
        print(f"   File size: {len(content) / 1024:.2f} KB")
        
        # Save to temp file
        file_ext = os.path.splitext(filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        print(f"   Temp file created: {tmp_path}")
        
        try:
            start_time = time.time()
            
            # Extract text with progress tracking
            print(f"🔍 Step 1/4: Extracting text with Docling OCR...")
            extract_start = time.time()
            text, page_count = self.load_document(tmp_path, file_ext, progress_callback)
            extract_time = time.time() - extract_start
            print(f"   ✅ Text extracted in {extract_time:.2f}s ({len(text)} characters from {page_count} pages)")
            
            # OCR complete - update to 90%
            if progress_callback:
                progress_callback(90)
            
            # Chunk document
            print(f"✂️  Step 2/4: Chunking document...")
            chunk_start = time.time()
            chunks = self.chunk_document(text)
            total_chunks = len(chunks)
            chunk_time = time.time() - chunk_start
            print(f"   ✅ Created {total_chunks} chunks in {chunk_time:.2f}s")
            
            if total_chunks == 0:
                raise ValueError("No text content could be extracted from the document")
            
            # Update to 92% after chunking
            if progress_callback:
                progress_callback(92)
            
            # Store embeddings
            print(f"💾 Step 3/4: Generating and storing embeddings...")
            embed_start = time.time()
            self.store_embeddings(document_id, chunks, filename)
            embed_time = time.time() - embed_start
            print(f"   ✅ Stored {total_chunks} embeddings in {embed_time:.2f}s")
            
            # Update to 95% after embeddings
            if progress_callback:
                progress_callback(95)
            
            total_time = time.time() - start_time
            print(f"✨ COMPLETE: {filename} processed in {total_time:.2f}s")
            print(f"   Summary: {page_count} pages → {total_chunks} chunks")
            print(f"   Time breakdown: Extract={extract_time:.1f}s, Chunk={chunk_time:.1f}s, Embed={embed_time:.1f}s")
            
            return {
                "total_chunks": total_chunks,
                "page_count": page_count,
                "processing_time": total_time
            }
        except Exception as e:
            print(f"❌ ERROR processing {filename}: {str(e)}")
            raise
        finally:
            os.unlink(tmp_path)
            print(f"🧹 Cleaned up temp file: {tmp_path}")
    
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
