# Docker Compose Services by Role

This directory contains role-specific Docker Compose configurations that provide only the services needed for each engineering role.

## 🏗️ Architecture

- **`base.yml`** - Common services (PostgreSQL, Redis) used by all roles
- **`backend.yml`** - Backend engineer specific services
- **`frontend.yml`** - Frontend engineer specific services  
- **`qa.yml`** - QA engineer specific services
- **`devops.yml`** - DevOps engineer specific services
- **`llm.yml`** - LLM challenge specific services

## 🚀 Quick Start

### Backend Engineers
```bash
cd docker-compose
./start-backend.sh
```

**Services**: PostgreSQL, Redis, MongoDB, RabbitMQ, Memcached, Postman

### Frontend Engineers
```bash
cd docker-compose
./start-frontend.sh
```

**Services**: PostgreSQL, Redis, Memcached, Selenium Grid (Chrome/Firefox)

### QA Engineers
```bash
cd docker-compose
./start-qa.sh
```

**Services**: PostgreSQL, Redis, Selenium Grid, Postman, JMeter, Appium

### DevOps Engineers
```bash
cd docker-compose
./start-devops.sh
```

**Services**: PostgreSQL, Redis, RabbitMQ, Elasticsearch, Prometheus, Grafana, Logstash, Kibana, SonarQube, Registry, Nginx

### LLM Challenge
```bash
cd docker-compose
./start-llm.sh
```

**Services**: PostgreSQL, Redis, Qdrant (Vector DB), Ollama (Local LLM), MinIO, MailHog

## 🔧 Manual Usage

If you prefer to start services manually:

```bash
# Start base services first
docker-compose -f base.yml up -d

# Then start role-specific services
docker-compose -f [role].yml up -d

# Example for backend
docker-compose -f base.yml -f backend.yml up -d
```

## 🛑 Stopping Services

```bash
# Stop all services for a role
docker-compose -f base.yml -f [role].yml down

# Example
docker-compose -f base.yml -f backend.yml down
```

## 📊 Service Ports

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Caching and sessions |
| MongoDB | 27017 | Document database |
| RabbitMQ | 5672 | Message queue |
| RabbitMQ Management | 15672 | Web UI |
| Memcached | 11211 | Memory cache |
| Selenium Hub | 4444 | Browser testing |
| JMeter | 1099 | Performance testing |
| Appium | 4723 | Mobile testing |
| Elasticsearch | 9200 | Search engine |
| Prometheus | 9090 | Metrics |
| Grafana | 3001 | Dashboards |
| Kibana | 5601 | Log visualization |
| SonarQube | 9002 | Code quality |
| Registry | 5000 | Container registry |
| Nginx | 80/443 | Web server |
| Qdrant | 6333 | Vector database |
| Ollama | 11434 | Local LLM |
| MinIO | 9000 | File storage |
| MinIO Console | 9001 | Web UI |
| MailHog | 8025 | Email testing |

## 💡 Tips

- **Base services must be started first** before role-specific services
- **Use the startup scripts** for easiest experience
- **Check service health** with `docker-compose ps`
- **View logs** with `docker-compose logs -f [service]`
- **Customize** by editing the compose files for your specific needs

## 🔍 Troubleshooting

### Port Conflicts
If you get port conflicts, edit the port mappings in the compose files:
```yaml
ports:
  - "5433:5432"  # Change from 5432 to 5433
```

### Memory Issues
For memory-intensive services like Elasticsearch, adjust memory limits:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Reduce from 512m
```

### Network Issues
If services can't communicate, ensure the external network exists:
```bash
docker network create interview_network
``` 