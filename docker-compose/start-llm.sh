#!/bin/bash

echo "🤖 Starting LLM Challenge Services..."

# Start base services first
docker-compose -f base.yml up -d

# Start LLM-specific services
docker-compose -f llm.yml up -d

echo "✅ LLM Challenge services started!"
echo "📊 Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Qdrant (Vector DB): localhost:6333"
echo "  - Ollama (Local LLM): localhost:11434"
echo "  - MinIO (File Storage): localhost:9000 (Console: localhost:9001)"
echo "  - MailHog (Email Testing): localhost:8025"

echo ""
echo "🔧 To stop: docker-compose -f base.yml -f llm.yml down"
echo "📝 To view logs: docker-compose -f base.yml -f llm.yml logs -f [service]"
echo ""
echo "💡 Tips:"
echo "  - Use Qdrant for storing and retrieving embeddings"
echo "  - Ollama supports models like llama2, codellama, mistral"
echo "  - MinIO for storing documents and files"
echo "  - MailHog for testing email integrations" 