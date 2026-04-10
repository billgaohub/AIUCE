# AIUCE Changelog

All notable changes to this project will be documented in this file.


## [1.4.0] - 2026-04-10

### Added - 多入口通道支持

**飞书/Telegram 适配器**
- `core/channels/`: 新增多入口通道模块
  - `base.py`: 统一 ChannelMessage 格式
  - `feishu.py`: 飞书机器人适配器
  - `telegram.py`: Telegram Bot 适配器
  - `manager.py`: 统一通道管理器
- API 新增端点: /webhook/feishu, /webhook/telegram, /channels, /channels/broadcast

### Changed - 架构现代化

**移除古代人物命名**
- 所有古代人物改为现代模块名
- `core/constants.py`, `core/message.py` 等文件

### Fixed - 配置初始化

- L9 AgentLayer config=None 修复
- 所有模块默认 config={} 确保安全初始化

---
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.0] - 2026-04-10

### Added - 核心架构升级（开源技术深度融合）

**L0 意志层 - 双重合宪性网关**
- `core/constitution.py`: 重构为双重网关架构
  - 硬网关 (HardGateway): 确定性规则引擎，< 1ms 延迟
  - 软网关 (SoftGateway): 语义审查引擎，预留 Hermes 集成接口
  - 预编译正则匹配，支持资金/系统目录/权限/隐私/有害内容拦截

**L4 记忆层 - 分级存储抽象层 (SAL)**
- `core/memory_sal.py`: 全新分级存储架构
  - L1 工作记忆: Lossless-claw DAG 结构 + FTS5 全文检索
  - L2 长期语义盘: Cognee 知识图谱微服务
  - 异步归档队列 + 实体提取 + 关系构建
  - SQLite 持久化 (~/.aiuce/lcm.db, ~/.aiuce/knowledge_graph/)

**神经总线 - 事件溯源引擎**
- `core/neural_bus.py`: AIUCE-Node 神经总线
  - 事件队列 (EventQueue): 内存/Redis Stream 可选
  - 事件存储 (EventStore): SQLite Append-only + 索引
  - 20+ 事件类型覆盖全部 11 层
  - correlation_id/causation_id 事件链追踪
  - 事件回放 (Replay) 支持审计

**L6/L7 演化层 - 双核变法引擎**
- `core/evolution.py`: 内圣外王双核架构
  - 内环 (InnerEvolution): Hermes 风格，成功模式提取 + 技能标准化
  - 外环 (OuterEvolution): OpenSpace 风格，FIX/DERIVED/CAPTURED 三模式
  - 最大重构尝试次数限制 + Fallback to Human 机制
  - 变异记录 + 回滚支持

**L2 感知层 - 现实对账引擎**
- `core/l2_reality_sensor.py`: UI-TARS 集成
  - 多模态感知器: 屏幕捕获/文本/鼠标/键盘/文件事件
  - 现实数据管道: 数据清洗 + 事件聚合 + 异常检测
  - 真相对账器: 声明验证 + 偏离检测 + 告警触发

**L3 推理层 - 多路径推演引擎**
- `core/l3_reasoning.py`: Deer-flow 集成
  - 任务规划器: 复杂任务分解 + DAG 依赖管理
  - 多路径推演: 演绎/归纳/溯因/类比/ReAct/ToT 策略
  - 路径评分与最优选择

**L9 代理层 - 跨设备执行引擎**
- `core/l9_agent.py`: UI-TARS 集成
  - 工具注册中心: 工具发现 + 能力声明 + 白名单管理
  - 执行引擎: 命令/脚本/API/UI 多模式执行
  - 风险评估 + 危险命令拦截 + 确认机制

### Architecture

```
用户输入
    ↓
[L0 双重网关] → 硬网关 (<1ms) → 软网关 (语义)
    ↓
[L2 感知层] → 多模态感知 → 现实对账
    ↓
[L3 推理层] → Deer-flow DAG → 多路径推演
    ↓
[L4 分级存储] → L1 DAG 工作记忆 → L2 知识图谱
    ↓
[神经总线] → 事件溯源 → 审计日志
    ↓
[L6/L7 双核演化] → 内环(Hermes) + 外环(OpenSpace)
    ↓
[L9 代理层] → 工具执行 → UI-TARS 交互
```

### Integrations Ready
- Hermes-agent: L0 软网关语义审查 + L6 内环学习
- Lossless-claw: L4 L1 DAG 存储
- Cognee: L4 L2 知识图谱
- OpenSpace: L7 外环演化引擎
- Deer-flow: L3 推理层任务规划
- UI-TARS: L2 感知层 + L9 代理层

### Tests
- ✅ L0 双重网关: 资金拦截/系统保护/正常放行
- ✅ L3 推理引擎: 任务分解/多路径推理
- ✅ L4 分级存储: DAG存储/FTS检索/知识图谱
- ✅ 神经总线: 事件发布/链追踪/订阅
- ✅ L6/L7 演化: 成功模式/规则创建

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
