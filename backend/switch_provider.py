#!/usr/bin/env python3
"""
Script to switch between OpenAI and Ollama providers.
Automatically handles separate collections for different embedding dimensions.
"""

import sys
import os

def update_env_file(provider: str):
    """Update the .env file to switch LLM provider."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return False
    
    # Read current .env content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update LLM_PROVIDER line
    updated_lines = []
    for line in lines:
        if line.startswith('LLM_PROVIDER='):
            updated_lines.append(f'LLM_PROVIDER={provider}\n')
            print(f"✅ Updated LLM_PROVIDER to: {provider}")
        else:
            updated_lines.append(line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    return True

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['openai', 'ollama']:
        print("Usage: python switch_provider.py [openai|ollama]")
        print("\nExample:")
        print("  python switch_provider.py openai")
        print("  python switch_provider.py ollama")
        sys.exit(1)
    
    provider = sys.argv[1]
    
    print(f"\n🔄 Switching to {provider.upper()}...\n")
    
    # Update .env file
    if not update_env_file(provider):
        sys.exit(1)
    
    # Show information about collections
    print(f"\n📦 Collection Information:")
    print(f"   - OpenAI uses collection: 'documents_openai' (1536 dimensions)")
    print(f"   - Ollama uses collection: 'documents_ollama' (768 dimensions)")
    print(f"   - Current provider: {provider}")
    print(f"   - Active collection: 'documents_{provider}'")
    
    # Show next steps
    print(f"\n✨ Next Steps:")
    print(f"   1. Your backend will auto-reload (if running with --reload)")
    print(f"   2. Upload documents through admin UI if collection is empty")
    print(f"   3. Each provider maintains its own document collection")
    
    # Provider-specific notes
    if provider == 'ollama':
        print(f"\n⚠️  Ollama Requirements:")
        print(f"   - Ensure Ollama is running: docker-compose up -d ollama")
        print(f"   - Update OLLAMA_URL in .env if running locally")
        print(f"   - Pull required models:")
        print(f"     docker exec -it rag-ollama ollama pull llama3.2:1b")
        print(f"     docker exec -it rag-ollama ollama pull nomic-embed-text")
    else:
        print(f"\n✅ OpenAI Configuration:")
        print(f"   - Using model: gpt-4o-mini")
        print(f"   - Using embeddings: text-embedding-3-small")
        print(f"   - API key configured in .env")
    
    print(f"\n🎉 Provider switch complete!\n")

if __name__ == "__main__":
    main()
