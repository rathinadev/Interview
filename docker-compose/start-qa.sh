#!/bin/bash

echo "🧪 Starting QA Engineer Services..."

# Start base services first
docker-compose -f base.yml up -d

# Start QA-specific services
docker-compose -f qa.yml up -d

echo "✅ QA services started!"
echo "📊 Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Selenium Hub: localhost:4444"
echo "  - Chrome Node: Available via Selenium Hub"
echo "  - Firefox Node: Available via Selenium Hub"
echo "  - Postman: Available in container"
echo "  - JMeter: localhost:1099"
echo "  - Appium: localhost:4723"

echo ""
echo "🔧 To stop: docker-compose -f base.yml -f qa.yml down"
echo "📝 To view logs: docker-compose -f base.yml -f qa.yml logs -f [service]" 