# AIUCE Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2026-04-10

### Added
- **`core/async_message.py`**: 异步消息总线实现
  - 支持同步和异步订阅者混合
  - 并发投递消息到多个层级
  - 异步钩子机制
  - 线程池执行同步回调
- **`benchmarks/performance.py`**: 性能基准测试套件
  - 消息总线吞吐量测试
  - 异步消息总线测试
  - 消息创建性能测试
  - 层级枚举性能测试
  - 端到端延迟测试
- **`QUICKSTART_EN.md`**: 英文快速开始指南
- **`l4_memory.py`**: 完善类型注解
  - MemoryCategory, MemoryPriority 枚举
  - EmbeddingProvider 协议
  - MemoryQuery, MemorySearchResult, MemoryStats 数据类

### Changed
- **`requirements.txt`**: 新增 pytest-asyncio, pytest-cov
- **`core/__init__.py`**: 导出 AsyncMessageBus 相关类型

### Improved
- 文档国际化质量提升
- L4 记忆层类型注解完善

---

## [1.2.0] - 2026-04-10

### Added
- **`.env.example`**: 环境变量配置示例文件
- **`docs/integration.md`**: 开源组件集成指南（Deer-flow、Hermes、UI-TARS 等）
- **`core/types.py`**: 完整的类型注解定义

### Changed
- **`examples/demo.py`**: 移除硬编码路径
- **`.github/workflows/ci.yml`**: 新增 lint/build job, Codecov 支持
- **`docs/architecture.md`**: 新增开源组件集成章节

---

## [1.1.0] - 2026-04-08

### Added
- **API Security Features**
  - API Key authentication for all endpoints
  - Rate limiting (100 req/min by default)
  - Request tracking with `request_id`
  - Exception sanitization (no internal errors exposed)
- **L9 Agent Layer Enhancements**
  - Command whitelist for safe execution
  - Dangerous pattern detection
  - Risk classification (LOW/MEDIUM/HIGH/CRITICAL)
  - Timeout limits (30s default, 120s max)
- **L8 Interface Layer**
  - Multi-provider support (OpenAI, Claude, Qwen, DeepSeek)
  - Local model support (Ollama, MLX)
  - Automatic model selection
- **Documentation**
  - English README (README_EN.md)
  - Architecture diagrams (docs/architecture_diagrams.md)
  - Promotion articles (CN + EN)
  - Social preview design

### Changed
- Improved error handling across all layers
- Enhanced L4 Memory with better semantic indexing
- Optimized L10 Sandbox simulation performance

### Fixed
- Fixed L0 constitution check bypass issue
- Fixed L5 decision log missing timestamps
- Fixed L7 evolution candidate approval flow

---

## [1.0.0] - 2026-04-01

### Added
- **Core 11-Layer Architecture**
  - L0: Constitution layer with veto power
  - L1: Identity layer with boundary control
  - L2: Perception layer for reality reconciliation
  - L3: Reasoning layer with 25 mind models
  - L4: Memory layer with semantic indexing
  - L5: Decision layer with audit trail
  - L6: Experience layer for daily review
  - L7: Evolution layer for self-improvement
  - L8: Interface layer for model gateway
  - L9: Agent layer for tool execution
  - L10: Sandbox layer for risk simulation
- **API Server**
  - FastAPI-based REST API
  - WebSocket support for real-time updates
  - Health check endpoints
  - Module status monitoring
- **Web UI**
  - Simple HTML/CSS/JavaScript interface
  - Real-time request/response visualization
- **Docker Support**
  - Dockerfile for containerized deployment
  - docker-compose.yml for easy setup
- **Testing**
  - Unit tests for all layers
  - Integration tests
  - Test coverage reporting

---

## [0.2.0] - 2026-03-25

### Added
- L0-L3 layers implementation
- Basic memory system (L4)
- Simple API endpoints
- Initial documentation

### Changed
- Refactored architecture from 7-layer to 11-layer

---

## [0.1.0] - 2026-03-20

### Added
- Initial project structure
- Basic L0 Constitution implementation
- Simple CLI interface
- README and LICENSE

---

## Future Roadmap

### [1.3.0] - Planned
- Mobile app (iOS/Android)
- Enterprise edition (multi-tenant, RBAC)
- Multi-language support (i18n)
- Cloud deployment guides (AWS/GCP/Azure)

### [2.0.0] - Planned
- Distributed architecture
- Plugin system
- Visual workflow builder
- AI training pipeline

---

## [1.2.0] - 2026-04-10

### Added
- **`.env.example`**: 环境变量配置示例文件
- **`docs/integration.md`**: 开源组件集成指南（Deer-flow、Hermes、UI-TARS 等）
- **`core/types.py`**: 完整的类型注解定义
  - LayerID, MessageType, DecisionStatus, RiskLevel 枚举
  - Message, Event, LayerResult 数据类
  - MemoryNode, MemoryQuery, MemorySearchResult 记忆系统类型
  - Decision 决策记录类型
  - Pydantic API 模型
  - 泛型 Result 容器

### Changed
- **`examples/demo.py`**: 移除硬编码路径，使用相对路径
- **`.github/workflows/ci.yml`**: 
  - 新增 lint job（Black、Flake8、MyPy）
  - 新增 build job
  - 新增 Codecov 覆盖率上传
- **`docs/architecture.md`**: 新增开源组件集成章节
- **`api.py`**: 新增 OpenAPI Tags 定义
- **`README.md`**: 新增集成指南链接

### Fixed
- 修复 demo.py 中的硬编码路径问题
- 修复 CI 流程不完整问题
- 修复 API 文档缺少标签分类问题

### Security
- 新增 `.env.example` 说明安全配置最佳实践

---

## Future Roadmap (Legacy)

### [1.2.0] - Planned
- Web UI visualization dashboard
- LangChain integration
- Enhanced L3 reasoning with chain-of-thought
- Improved L10 Monte Carlo simulation

### [1.3.0] - Planned
- Mobile app (iOS/Android)
- Enterprise edition (multi-tenant, RBAC)
- Multi-language support (i18n)
- Cloud deployment guides (AWS/GCP/Azure)

### [2.0.0] - Planned
- Distributed architecture
- Plugin system
- Visual workflow builder
- AI training pipeline

---

## Version Naming Convention

- **Major (X.0.0)**: Architecture changes, breaking changes
- **Minor (1.X.0)**: New features, enhancements
- **Patch (1.1.X)**: Bug fixes, minor improvements

---

[1.1.0]: https://github.com/billgaohub/AIUCE/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/billgaohub/AIUCE/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/billgaohub/AIUCE/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/billgaohub/AIUCE/releases/tag/v0.1.0
