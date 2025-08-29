# Ragworks AI Interview System

A comprehensive technical interview platform designed to evaluate software engineering candidates across different specializations through practical, role-specific challenges.

## 🎯 System Overview

**IMPORTANT: Candidates should ONLY work in their target role directory. You do NOT need to complete all roles or understand the entire system.**

This platform provides:
- **Role-specific assessments** tailored to different engineering disciplines
- **Modular infrastructure** with only the services you need
- **Practical challenges** that mirror real-world development scenarios
- **Clear evaluation criteria** and submission guidelines

## 🚀 Choose Your Challenge

### 🏗️ **Backend Engineers** (`backend-engineer/`)
**Focus**: API development, database design, system architecture
- **Duration**: 2-3 coding problems (6-10 hours total)
- **Deliverables**: Working APIs, database schemas, system designs
- **Tech Stack**: FastAPI, PostgreSQL, Redis, Docker, message queues
- **Infrastructure**: `docker-compose/start-backend.sh`

### 🎨 **Frontend Engineers** (`frontend-engineer/`)
**Focus**: UI/UX implementation, modern web development
- **Duration**: 2-3 UI/UX challenges (6-10 hours total)
- **Deliverables**: Interactive components, responsive layouts, optimized applications
- **Tech Stack**: React, Next.js, TypeScript, Tailwind CSS, testing frameworks
- **Infrastructure**: `docker-compose/start-frontend.sh`

### 🧪 **QA Engineers** (`qa-engineer/`)
**Focus**: Test automation, quality assurance, testing strategies
- **Duration**: 2-3 testing challenges (6-10 hours total)
- **Deliverables**: Test frameworks, automation scripts, testing strategies
- **Tech Stack**: Python, Selenium/Playwright, Pytest, performance tools
- **Infrastructure**: `docker-compose/start-qa.sh`

### 🏗️ **DevOps Engineers** (`devops-engineer/`)
**Focus**: Infrastructure as Code, CI/CD, monitoring, security
- **Duration**: 2-3 infrastructure challenges (6-10 hours total)
- **Deliverables**: Terraform configs, CI/CD pipelines, monitoring dashboards
- **Tech Stack**: Terraform, Kubernetes, Docker, Prometheus, CI/CD tools
- **Infrastructure**: `docker-compose/start-devops.sh`

### 🤖 **LLM Challenge** (`llm-challenge/`) - *Optional*
**Focus**: LLM integration, RAG implementation, full-stack development
- **Duration**: Build a complete application (timeline flexible)
- **Deliverables**: Streamlit + FastAPI RAG application with authentication
- **Tech Stack**: Streamlit, FastAPI, LLM APIs, Vector databases
- **Senior Bonus**: Email integration for automatic responses
- **Infrastructure**: `docker-compose/start-llm.sh`

## 🚀 Quick Start

### 1. **Fork & Clone**
```bash
# Fork this repository to your GitHub account
# Clone your forked repository
git clone <your-forked-repo>
cd ragworks/Interview
```

### 2. **Choose Your Role**
```bash
# Navigate to your role directory
cd [your-role-directory]  # e.g., backend-engineer, frontend-engineer, etc.
# OR for LLM challenge:
cd llm-challenge
```

### 3. **Start Infrastructure**
```bash
# Navigate to docker-compose directory
cd ../docker-compose

# Start services for your role
./start-[role].sh  # e.g., start-backend.sh, start-frontend.sh, etc.
```

### 4. **Begin Assessment**
```bash
# Return to your role directory
cd ../[your-role-directory]

# Read the README for specific requirements
# Start building your solution
```

### 5. **Submit Your Work**
- **Test thoroughly** and ensure all requirements are met
- **Document your solution** with clear setup and usage instructions
- **Final Step**: Reach out to engineering@ragworks.ai with your repo link and a good README on how to run the program

## 🔧 Infrastructure Services

### **Base Services** (All Roles)
- **PostgreSQL** (5432) - Primary database
- **Redis** (6379) - Caching and sessions

### **Role-Specific Services**

| Role | Services | Memory Usage |
|------|----------|--------------|
| **Backend** | MongoDB, RabbitMQ, Memcached, Postman | ~800MB |
| **Frontend** | Memcached, Selenium Grid | ~600MB |
| **QA** | Selenium Grid, Postman, JMeter, Appium | ~1.2GB |
| **DevOps** | RabbitMQ, Elasticsearch, Prometheus, Grafana, SonarQube | ~2.5GB |
| **LLM** | Qdrant, Ollama, MinIO, MailHog | ~1.5GB |

### **Quick Infrastructure Start**
```bash
cd docker-compose

# Start services for your role
./start-backend.sh      # For backend engineers
./start-frontend.sh     # For frontend engineers
./start-qa.sh          # For QA engineers
./start-devops.sh      # For DevOps engineers
./start-llm.sh         # For LLM challenge
```

## 📊 Service Access

### **Common Services**
- **PostgreSQL**: localhost:5432 (interview_user/interview_password)
- **Redis**: localhost:6379 (redis_password)

### **Role-Specific Services**
- **Backend**: MongoDB (27017), RabbitMQ (5672/15672), Memcached (11211)
- **Frontend**: Selenium Grid (4444)
- **QA**: Selenium Grid (4444), JMeter (1099), Appium (4723)
- **DevOps**: Elasticsearch (9200), Prometheus (9090), Grafana (3001), SonarQube (9002)
- **LLM**: Qdrant (6333), Ollama (11434), MinIO (9000/9001), MailHog (8025)

## 📋 Evaluation Criteria

### **Common Metrics** (All Roles)
- **Functionality** (30%) - Does the solution work as intended?
- **Code Quality** (25%) - Clean, maintainable, well-structured code
- **Best Practices** (20%) - Following industry standards and patterns
- **Documentation** (15%) - Clear setup and usage instructions
- **Testing** (10%) - Proper testing and validation

### **Role-Specific Focus**
- **Backend**: API design, database optimization, system architecture
- **Frontend**: UI/UX quality, performance, accessibility
- **QA**: Test coverage, automation quality, testing strategies
- **DevOps**: Infrastructure design, CI/CD implementation, monitoring
- **LLM**: AI integration, RAG implementation, full-stack development

## 🛠️ Technology Stack

### **Backend Technologies**
- **Languages**: Python, Node.js, Go, Java, C#
- **Frameworks**: FastAPI, Flask, Express, Spring Boot, .NET
- **Databases**: PostgreSQL, MongoDB, Redis, MySQL
- **Message Queues**: RabbitMQ, Apache Kafka, Redis

### **Frontend Technologies**
- **Frameworks**: React, Vue, Angular, Next.js, Nuxt.js
- **Languages**: TypeScript, JavaScript
- **Styling**: Tailwind CSS, CSS-in-JS, SCSS
- **Testing**: Jest, React Testing Library, Cypress, Playwright

### **DevOps Technologies**
- **Infrastructure**: Terraform, CloudFormation, Ansible
- **Containers**: Docker, Kubernetes, Docker Compose
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, ArgoCD
- **Monitoring**: Prometheus, Grafana, ELK Stack, Jaeger

### **LLM Technologies**
- **APIs**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Frameworks**: LangChain, LlamaIndex, Transformers
- **Vector DBs**: Qdrant, Pinecone, Chroma, Weaviate
- **Tools**: Ollama, LM Studio, Hugging Face

## 📚 Documentation

- [Backend Engineer Assessment](./backend-engineer/README.md) - **Complete 2-3 problems in 6-10 hours**
- [Frontend Engineer Assessment](./frontend-engineer/README.md) - **Complete 2-3 problems in 6-10 hours**
- [QA Engineer Assessment](./qa-engineer/README.md) - **Complete 2-3 problems in 6-10 hours**
- [DevOps Engineer Assessment](./devops-engineer/README.md) - **Complete 2-3 problems in 6-10 hours**
- [LLM Challenge](./llm-challenge/README.md) - **Build Streamlit + FastAPI RAG application**
- [Docker Compose Services](./docker-compose/README.md) - **Role-specific infrastructure setup**

## 🚦 Management Commands

### **Start Services**
```bash
cd docker-compose
./start-[role].sh
```

### **Stop Services**
```bash
docker-compose -f base.yml -f [role].yml down
```

### **View Logs**
```bash
docker-compose -f base.yml -f [role].yml logs -f [service]
```

### **Check Status**
```bash
docker-compose -f base.yml -f [role].yml ps
```

## 💡 Best Practices & Success Tips

### **Development**
- **Start Simple**: Begin with a working solution, then optimize
- **Test Early**: Write tests as you develop, not after
- **Document**: Keep documentation updated with your code
- **Version Control**: Use meaningful commits and branches
- **Error Handling**: Implement proper error handling and validation

### **Infrastructure**
- **Use Role-Specific Scripts**: Start only the services you need
- **Check Service Health**: Ensure services are running before starting development
- **Monitor Resources**: Watch memory and CPU usage
- **Clean Up**: Stop services when not in use

### **Submission**
- **README Quality**: Clear setup instructions are crucial
- **Working Solution**: Ensure everything runs without manual intervention
- **Environment Setup**: Document all dependencies and configuration
- **Testing Instructions**: Include how to test your solution

## 🔍 Troubleshooting

### **Common Issues**
- **Port Conflicts**: Edit port mappings in docker-compose files
- **Memory Issues**: Adjust memory limits for resource-intensive services
- **Network Issues**: Ensure Docker network exists and services can communicate
- **Service Dependencies**: Start base services before role-specific ones

### **Getting Help**
- Check the role-specific README files
- Review the docker-compose documentation
- Check service logs: `docker-compose logs -f [service]`
- Verify service health: `docker-compose ps`
- Contact engineering@ragworks.ai for support

## 🤝 Support

For technical support or questions:
1. Check the role-specific documentation
2. Review the docker-compose guides
3. Contact the development team at engineering@ragworks.ai

---

**Good luck! We're excited to see what you build! 🚀**
