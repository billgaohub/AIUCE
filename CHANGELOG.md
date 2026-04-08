# Changelog

All notable changes to the AIUCE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-08

### Security
- **API Key Authentication**: All API endpoints require `X-API-Key` header
- **Rate Limiting**: Default 100 requests/minute with configurable limits
- **Exception Sanitization**: No internal error details exposed to clients
- **Request ID Tracking**: All errors include request_id for debugging
- **CORS Configuration**: Configurable allowed origins via environment

### Added
- **L8 Real API Calls**: Implemented actual API calls for OpenAI, Claude, Qwen, DeepSeek
- **Local Model Support**: Added Ollama and MLX local model integration
- **Unified Logging**: New `core/logging_config.py` with structured logging
- **Error Handling Framework**: Custom exception classes for each layer
- **Environment Config Parser**: Automatic `${ENV_VAR}` resolution in config
- **Pre-commit Hooks**: Code quality checks (black, flake8, mypy, isort)
- **Docker Healthcheck**: Proper health check for container orchestration

### Changed
- **requirements.txt**: Added FastAPI, uvicorn dependencies
- **docs/api_reference.md**: Complete rewrite for v1.1.0 API
- **SECURITY.md**: Updated with new security features
- **docker-compose.yml**: Enhanced with healthcheck and env vars

### Fixed
- **Path Hardcoding**: All paths now use `~/.aiuce/` or environment variables
- **Mock Mode**: L8 interface now supports real API calls (mock optional)

## [1.0.0] - 2026-03-21

### Added
- **L0 Constitution Layer (秦始皇/御书房)**: Supreme constitution with veto power
- **L1 Identity Layer (诸葛亮/宗人府)**: Identity boundary management
- **L2 Perception Layer (魏征/都察院)**: Reality data reconciliation
- **L3 Reasoning Layer (张良/军机处)**: Multi-path reasoning with 25 mind models
- **L4 Memory Layer (司马迁/翰林院)**: Semantic indexing and knowledge storage
- **L5 Decision Layer (包拯/大理寺)**: Decision audit and logging
- **L6 Experience Layer (曾国藩/吏部)**: Daily review and pattern recognition
- **L7 Evolution Layer (商鞅/中书省)**: Self-evolution and rule updates
- **L8 Interface Layer (张骞/礼部)**: Multi-model provider interface
- **L9 Agent Layer (韩信/锦衣卫)**: Cross-device execution and tool scheduling
- **L10 Sandbox Layer (庄子/钦天监)**: Shadow universe simulation
- Complete API documentation with FastAPI
- Interactive Web UI for system visualization
- Docker and Docker Compose support
- Comprehensive test suite
- MIT License

### Features
- Layered governance with checks and balances
- Constitutional veto mechanism
- Audit trail for all decisions
- Progressive evolution through daily reviews
- Multi-model AI provider support
- Real-time system status monitoring

[Unreleased]: https://github.com/billgaohub/AIUCE/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/billgaohub/AIUCE/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/billgaohub/AIUCE/releases/tag/v1.0.0
