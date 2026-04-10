# AIUCE Quick Start Guide

> Get started with AIUCE in 5 minutes

---

## What is AIUCE?

AIUCE (AI Universe Constitution Evolution) is an 11-layer AI governance framework inspired by ancient Chinese administrative systems. It provides a structured approach to building AI systems that are:

- **Sovereign**: User-controlled, not vendor-controlled
- **Transparent**: Every decision is auditable
- **Evolvable**: The system improves itself over time
- **Safe**: Built-in constitutional checks prevent misuse

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 22+ (for web interface)
- Git

### Quick Install

```bash
# Clone the repository
git clone https://github.com/billgaohub/AIUCE.git
cd AIUCE

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx
```

---

## Running AIUCE

### Option 1: API Server

```bash
# Start the FastAPI server
./start.sh

# Or manually:
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option 3: Direct Usage

```python
from system import create_system

# Create system instance
system = create_system()

# Process a query
result = system.run("What's the weather today?")
print(result)

# Check layer status
status = system.get_layer_status()
for layer, info in status.items():
    print(f"{layer}: {info['status']}")
```

---

## Understanding the 11 Layers

| Layer | Name | Role | Chinese Official |
|-------|------|------|-----------------|
| L0 | Will (意志层) | Constitutional veto power | Qin Shi Huang |
| L1 | Identity (身份层) | Persona boundaries | Zhuge Liang |
| L2 | Perception (感知层) | Reality reconciliation | Wei Zheng |
| L3 | Reasoning (推理层) | Multi-path reasoning | Zhang Liang |
| L4 | Memory (记忆层) | Semantic indexing | Sima Qian |
| L5 | Decision (决策层) | Audit trail | Bao Zheng |
| L6 | Experience (经验层) | Daily review | Zeng Guofan |
| L7 | Evolution (演化层) | Self-improvement | Shang Yang |
| L8 | Interface (接口层) | Model gateway | Zhang Qian |
| L9 | Agent (代理层) | Tool execution | Han Xin |
| L10 | Sandbox (沙盒层) | Risk simulation | Zhuangzi |

---

## Example: Processing a Query

```python
from system import create_system

system = create_system()

# Example 1: Simple query
result = system.run("Summarize my recent journal entries")
# Returns: {"status": "success", "response": "...", "layers_used": ["L2", "L4", "L5"]}

# Example 2: With context
result = system.run(
    "Should I invest in this project?",
    context={
        "project": "AI Startup",
        "budget": 100000,
        "risk_tolerance": "medium"
    }
)

# Example 3: Check constitution
result = system.run("Delete all my data")
# Returns: {"status": "vetoed", "reason": "L0: Violates safety rules"}
```

---

## API Reference

### Query Endpoint

```bash
POST /api/v1/query
Content-Type: application/json
X-API-Key: your-api-key

{
  "query": "Your question here",
  "context": {},
  "user_id": "user123"
}
```

### Response

```json
{
  "status": "success",
  "response": "...",
  "layers_involved": ["L2", "L3", "L5"],
  "audit_id": "audit_abc123",
  "metadata": {
    "processing_time_ms": 1234
  }
}
```

### Health Check

```bash
GET /health

# Response
{
  "status": "healthy",
  "version": "1.2.0",
  "uptime_seconds": 3600,
  "layers_status": {
    "L0": true,
    "L1": true,
    ...
  }
}
```

---

## Configuration

### Environment Variables

```bash
# API Keys (required for cloud models)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Local model (optional)
OLLAMA_BASE_URL=http://localhost:11434

# Security
AIUCE_API_KEYS=key1,key2,key3
AIUCE_AUTH_ENABLED=true
AIUCE_RATE_LIMIT=100

# CORS
AIUCE_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Config File

Create `config/user.yaml`:

```yaml
constitution:
  strict_mode: true
  veto_patterns:
    - "delete.*data"
    - "transfer.*money"

identity:
  persona: "Personal AI Assistant"
  boundaries:
    - "Never share personal data externally"
    - "Always ask for confirmation on financial actions"

memory:
  storage_path: ~/.aiuce/memory_store.json
  max_memories: 10000

interface:
  default_provider: openai
  fallback_provider: ollama
```

---

## Open Source Integration

AIUCE integrates with top open-source projects:

| Component | Purpose | Layer |
|-----------|---------|-------|
| Deer-flow | Task planning | L3 |
| Hermes | Intent auditing | L0, L6 |
| Lossless-claw | DAG memory storage | L4 |
| Cognee | Knowledge graph | L4 |
| OpenSpace | Evolution engine | L7 |
| UI-TARS | GUI automation | L2, L9 |

See [docs/integration.md](docs/integration.md) for detailed setup instructions.

---

## Troubleshooting

### Common Issues

**1. "Module not found" error**

```bash
# Make sure you're in the AIUCE directory
cd AIUCE
pip install -r requirements.txt
```

**2. API key not working**

```bash
# Check .env file
cat .env

# Verify the key format
# OpenAI: sk-xxx
# Anthropic: sk-ant-xxx
```

**3. Port 8000 already in use**

```bash
# Use a different port
uvicorn api:app --host 0.0.0.0 --port 8001

# Or kill the existing process
lsof -ti:8000 | xargs kill -9
```

---

## Next Steps

1. Read the [Architecture Guide](docs/architecture.md) to understand the design philosophy
2. Try the [Examples](examples/) to see AIUCE in action
3. Join our [GitHub Discussions](https://github.com/billgaohub/AIUCE/discussions) to ask questions
4. Star the repo ⭐ if you find it useful!

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/billgaohub/AIUCE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/billgaohub/AIUCE/discussions)

---

*Last updated: 2026-04-10*
