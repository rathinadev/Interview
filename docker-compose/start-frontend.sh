#!/bin/bash

echo "🎨 Starting Frontend Engineer Services..."

# Start base services first
docker-compose -f base.yml up -d

# Start frontend-specific services
docker-compose -f frontend.yml up -d

echo "✅ Frontend services started!"
echo "📊 Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Memcached: localhost:11211"
echo "  - Selenium Hub: localhost:4444"
echo "  - Chrome Node: Available via Selenium Hub"
echo "  - Firefox Node: Available via Selenium Hub"

echo ""
echo "🔧 To stop: docker-compose -f base.yml -f frontend.yml down"
echo "📝 To view logs: docker-compose -f base.yml -f frontend.yml logs -f [service]" 