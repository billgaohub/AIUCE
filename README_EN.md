# AIUCE System 🏯

[![CI](https://github.com/billgaohub/AIUCE/actions/workflows/ci.yml/badge.svg)](https://github.com/billgaohub/AIUCE/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

> **AIUCE** = **A**I System + **U**niverse + **C**onstitution + **E**volution
>
> **Personal AI Infrastructure with Layered Governance**
>
> Inspired by Ancient Chinese Bureaucratic Wisdom

---

## 🎯 Why AIUCE?

### The Problem with AI Today

| Problem | Impact |
|---------|--------|
| ❌ **Black Box** | You can't understand why AI made a decision |
| ❌ **Unpredictable** | AI evolves in unexpected directions |
| ❌ **No Veto Power** | You can't stop AI from doing something harmful |
| ❌ **No Memory** | AI forgets context across sessions |
| ❌ **No Accountability** | You can't trace who made what decision |

### The AIUCE Solution

| Solution | Layer |
|----------|-------|
| ✅ **Constitutional Veto** | L0 - Supreme Constitution with veto power |
| ✅ **Controlled Evolution** | L7 - Conservative but continuous improvement |
| ✅ **Full Audit Trail** | L5 - Every decision is logged and traceable |
| ✅ **Semantic Memory** | L4 - Persistent knowledge across sessions |
| ✅ **11-Layer Governance** | L0-L10 - Checks and balances at every level |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/billgaohub/aiuce.git
cd aiuce

# Start with Docker
docker-compose up -d

# Access the API
curl http://localhost:8000/health
```

### Option 2: Manual Installation

```bash
# Clone and install
git clone https://github.com/billgaohub/aiuce.git
cd aiuce
pip install -r requirements.txt

# Start the API server
python api.py

# Open Web UI
open http://localhost:8000/static/index.html
```

---

## 🏛️ The 11-Layer Architecture

AIUCE implements a unique governance structure inspired by ancient Chinese bureaucratic wisdom:

```
┌─────────────────────────────────────────────────────────┐
│                    L0 CONSTITUTION                      │
│         "Emperor's Study" - Supreme Veto Power          │
├─────────────────────────────────────────────────────────┤
│                    L1 IDENTITY                          │
│         "Ministry of Rites" - Boundary Control          │
├─────────────────────────────────────────────────────────┤
│                    L2 PERCEPTION                        │
│         "Censorate" - Reality Reconciliation            │
├─────────────────────────────────────────────────────────┤
│                    L3 REASONING                         │
│         "Grand Council" - Multi-path Reasoning          │
├─────────────────────────────────────────────────────────┤
│                    L4 MEMORY                            │
│         "Hanlin Academy" - Knowledge Storage            │
├─────────────────────────────────────────────────────────┤
│                    L5 DECISION                          │
│         "Supreme Court" - Audit & Logging               │
├─────────────────────────────────────────────────────────┤
│                    L6 EXPERIENCE                        │
│         "Ministry of Personnel" - Daily Review          │
├─────────────────────────────────────────────────────────┤
│                    L7 EVOLUTION                         │
│         "Secretariat" - Self-Improvement                │
├─────────────────────────────────────────────────────────┤
│                    L8 INTERFACE                         │
│         "Ministry of Foreign Affairs" - Model Gateway   │
├─────────────────────────────────────────────────────────┤
│                    L9 AGENT                             │
│         "Imperial Guard" - Execution & Tools            │
├─────────────────────────────────────────────────────────┤
│                    L10 SANDBOX                          │
│         "Astronomical Bureau" - Shadow Universe         │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Name | Responsibility | Key Feature |
|-------|------|----------------|-------------|
| **L0** | Constitution | Supreme will, veto power | 🛡️ One-vote veto |
| **L1** | Identity | Persona boundaries | 🔒 Prevent overreach |
| **L2** | Perception | Reality data | 📊 Ground truth |
| **L3** | Reasoning | Multi-path analysis | 🧠 25 mind models |
| **L4** | Memory | Knowledge storage | 📚 Semantic indexing |
| **L5** | Decision | Audit & logging | ⚖️ Full traceability |
| **L6** | Experience | Daily review | 🔄 Pattern recognition |
| **L7** | Evolution | Self-improvement | 🔄 Kernel refactoring |
| **L8** | Interface | Model gateway | 🌐 Multi-provider API |
| **L9** | Agent | Execution | ⚔️ Tool scheduling |
| **L10** | Sandbox | Shadow simulation | 🌌 Monte Carlo testing |

---

## 🔐 Security Features

### API Security (v1.1.0)

- **API Key Authentication**: All endpoints require `X-API-Key` header
- **Rate Limiting**: 100 requests/minute (configurable)
- **Exception Sanitization**: No internal errors exposed
- **Request Tracking**: All errors include `request_id`

```bash
# Set API keys
export AIUCE_API_KEYS="your-secret-key-1,your-secret-key-2"

# Make authenticated request
curl -H "X-API-Key: your-secret-key-1" http://localhost:8000/status
```

### Execution Sandbox (L9)

- **Command Whitelist**: Only safe commands allowed
- **Dangerous Pattern Detection**: Auto-block risky operations
- **Timeout Limits**: 30s default, 120s max
- **Risk Classification**: LOW/MEDIUM/HIGH/CRITICAL

---

## 🌐 Multi-Model Support (L8)

AIUCE supports multiple AI providers:

| Provider | Model | Status |
|----------|-------|--------|
| OpenAI | GPT-4o-mini | ✅ Supported |
| Anthropic | Claude 3.5 Sonnet | ✅ Supported |
| Alibaba | Qwen-Plus | ✅ Supported |
| DeepSeek | DeepSeek-Chat | ✅ Supported |
| Local | Ollama (Llama3) | ✅ Supported |
| Local | MLX (Qwen2.5-7B) | ✅ Supported |

```python
from aiuce import AIUCE

# Initialize with preferred provider
ai = AIUCE(provider="openai")

# Or use local model
ai = AIUCE(provider="mlx")

# Process with full governance
response = ai.process("Your request here")
```

---

## 📊 Architecture Philosophy

> "Governing a large country is like cooking a small fish" — Lao Tzu

AIUCE applies ancient governance wisdom to modern AI:

### 1. **Separation of Powers**
Each layer has clear responsibilities. No single layer can dominate.

### 2. **Checks and Balances**
L0/L1 have veto power. L5 logs all decisions. L6 reviews daily.

### 3. **Accountability**
Every decision is traceable. Every action is auditable.

### 4. **Controlled Evolution**
L7 enables self-improvement, but changes require approval.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](QUICKSTART.md) | 5-minute setup guide |
| [Architecture](docs/architecture.md) | Deep dive into 11 layers |
| [API Reference](docs/api_reference.md) | Complete API documentation |
| [Philosophy](docs/philosophy.md) | Design principles |
| [Security](SECURITY.md) | Security features and policies |
| [Changelog](CHANGELOG.md) | Version history |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .

# Type checking
mypy aiuce/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🌟 Star History

If you find AIUCE useful, please consider giving it a star ⭐

---

**AIUCE** - Personal AI Infrastructure with Layered Governance

🏯 *Bringing Ancient Wisdom to Modern AI*
