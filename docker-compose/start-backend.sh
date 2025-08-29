#!/bin/bash

echo "🚀 Starting Backend Engineer Services..."

# Start base services first
docker-compose -f base.yml up -d

# Start backend-specific services
docker-compose -f backend.yml up -d

echo "✅ Backend services started!"
echo "📊 Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - MongoDB: localhost:27017"
echo "  - RabbitMQ: localhost:5672 (Management: localhost:15672)"
echo "  - Memcached: localhost:11211"
echo "  - Postman: Available in container"

echo ""
echo "🔧 To stop: docker-compose -f base.yml -f backend.yml down"
echo "📝 To view logs: docker-compose -f base.yml -f backend.yml logs -f [service]" 