# AI Agent for GCP Web App Generation

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-org/gcp-ai-agent)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous AI agent that generates complete, working GCP web applications from natural language requirements. Features self-healing capabilities, multi-provider LLM support, and production-ready deployment automation.

## 🚀 Features

- **Natural Language to Code**: Transform requirements into full-stack applications
- **Multi-Framework Support**: React, Vue, Angular frontends with FastAPI, Express backends
- **Self-Healing Architecture**: Automatic error recovery and system optimization
- **GCP Native**: Built for Google Cloud Platform with native service integration
- **Production Ready**: Includes monitoring, testing, and deployment automation
- **Real-time Updates**: Live progress tracking with WebSocket support

## 🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Planning │ │ Generation │ │ Deployment │
│ Agent │───▶│ Engine │───▶│ Manager │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ LLM │ │ Module │ │ GCP │
│ Manager │ │ Generators │ │ Services │
└─────────────────┘ └─────────────────┘ └─────────────────┘

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud SDK
- Docker (optional)
- Node.js 18+ (for frontend development)

### Installation

1. **Clone the repository**
git clone https://github.com/your-org/gcp-ai-agent.git
cd gcp-ai-agent

2. **Set up environment**
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt


3. **Configure environment variables**
cp .env.example .env


4. **Initialize GCP services**
python -m app.gcp_services.gcp_services_setup


5. **Run the application**
uvicorn app.main:app --reload


Visit `http://localhost:8080` to access the dashboard.

### Docker Setup
docker-compose up -d


## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | ✅ |
| `OPENAI_API_KEY` | OpenAI API Key | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API Key | ❌ |
| `JWT_SECRET_KEY` | JWT Secret for authentication | ✅ |
| `FIRESTORE_DATABASE` | Firestore database name | ❌ |

### LLM Providers

The system supports multiple LLM providers with automatic failover:

- **OpenAI GPT-4** (Primary)
- **Anthropic Claude** (Fallback)
- **Google Gemini** (Fallback)

## 📖 Usage

### API Usage
import requests

Generate application architecture
response = requests.post("http://localhost:8080/api/v1/generate/architecture", json={
"project_id": "my-project",
"requirements": "Create an e-commerce platform with user authentication, product catalog, and payment processing"
})

architecture = response.json()


### Web Interface

1. Navigate to the dashboard at `http://localhost:8080`
2. Click "New Project"
3. Enter your application requirements in natural language
4. Monitor real-time generation progress
5. Download generated code or deploy directly to GCP

### CLI Usage
Generate a new application
python -m app.tools.project_generator
--requirements "Task management app with real-time collaboration"
--output ./generated-app

Deploy to GCP
python -m app.deployment.deployment_manager
--project-path ./generated-app
--target cloud-run


## 🧪 Testing
Run all tests
pytest

Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

Run with coverage
pytest --cov=app tests/


## 📊 Monitoring

The system includes comprehensive monitoring:

- **Prometheus metrics** at `:9090/metrics`
- **Grafana dashboards** at `:3000`
- **Application logs** via structured JSON logging
- **Real-time performance tracking**

### Key Metrics

- Generation success rate
- Average generation time
- LLM provider health
- Error rates by component
- Self-healing actions

## 🚀 Deployment

### Local Development
docker-compose up -d


### Google Cloud Run
gcloud builds submit --config cloudbuild.yaml


### Kubernetes
kubectl apply -f deployment/kubernetes/


### Terraform
cd terraform
terraform init
terraform plan
terraform apply


## 🔧 Development

### Project Structure
app/
├── core/ # Core AI agents
├── llm_integration/ # LLM provider management
├── module_generators/ # Code generation engines
├── deployment/ # Deployment managers
├── api/ # REST API and WebSocket
├── ui/ # Web interface
└── gcp_services/ # GCP service clients


### Adding New Module Generators

1. Extend `BaseModuleGenerator`
2. Implement `generate()` and `get_template()` methods
3. Add to `TaskExecutionEngine.generators`
4. Create templates in `app/module_generators/templates/`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Documentation](docs/api_documentation.md)
- [Deployment Guide](docs/deployment_guide.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🐛 Troubleshooting

### Common Issues

**LLM Provider Errors**
Check provider health
curl http://localhost:8080/api/v1/health


**Generation Failures**
Check logs
docker-compose logs ai-agent


**Deployment Issues**
Verify GCP permissions
gcloud auth list
gcloud projects get-iam-policy $GCP_PROJECT_ID


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 📧 Email: support@yourcompany.com
- 💬 Discord: [Join our community](https://discord.gg/your-server)
- 📖 Documentation: [docs.yourcompany.com](https://docs.yourcompany.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/gcp-ai-agent/issues)

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API  
- Google Cloud Platform
- FastAPI framework
- The open-source community

---

**Built with ❤️ for developers who want to focus on ideas, not infrastructure.**

