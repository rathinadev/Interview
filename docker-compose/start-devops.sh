#!/bin/bash

echo "🏗️ Starting DevOps Engineer Services..."

# Start base services first
docker-compose -f base.yml up -d

# Start DevOps-specific services
docker-compose -f devops.yml up -d

echo "✅ DevOps services started!"
echo "📊 Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ: localhost:5672 (Management: localhost:15672)"
echo "  - Elasticsearch: localhost:9200"
echo "  - Prometheus: localhost:9090"
echo "  - Grafana: localhost:3001 (admin/admin123)"
echo "  - Logstash: localhost:5044, 5000, 9600"
echo "  - Kibana: localhost:5601"
echo "  - SonarQube: localhost:9002"
echo "  - Registry: localhost:5000"
echo "  - Nginx: localhost:80, 443"

echo ""
echo "🔧 To stop: docker-compose -f base.yml -f devops.yml down"
echo "📝 To view logs: docker-compose -f base.yml -f devops.yml logs -f [service]" 