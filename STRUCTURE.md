# Eleven-Layer AI System - Project Structure
# 十一层架构 AI 系统 - 项目结构

```
eleven_layer_ai/
│
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖列表
├── setup.py                     # 安装脚本
├── config.yaml                  # 配置文件
├── .gitignore                   # Git忽略规则
├── STRUCTURE.md                 # 本文件 - 项目结构说明
│
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── constants.py             # 常量定义 (Layer, MsgType, RiskLevel等)
│   ├── types.py                 # 类型定义 (数据类、接口)
│   ├── message.py               # 消息总线实现
│   ├── constitution.py          # L0: 意志层/宪法引擎
│   └── audit.py                 # 审计日志系统
│
├── l1_identity.py               # L1: 身份层 - 诸葛亮/宗人府
├── l2_perception.py             # L2: 感知层 - 魏征/都察院
├── l3_reasoning.py              # L3: 推理层 - 张良/军机处
├── l4_memory.py                 # L4: 记忆层 - 司马迁/翰林院
├── l5_decision.py               # L5: 决策层 - 包拯/大理寺
├── l6_experience.py             # L6: 经验层 - 曾国藩/吏部
├── l7_evolution.py              # L7: 演化层 - 商鞅/中书省
├── l8_interface.py              # L8: 接口层 - 张骞/礼部
├── l9_agent.py                  # L9: 代理层 - 韩信/锦衣卫
├── l10_sandbox.py               # L10: 沙盒层 - 庄子/钦天监
│
├── system.py                    # 主系统入口 - ElevenLayerSystem
├── utils.py                     # 工具函数
├── __init__.py                  # 包初始化，导出主要类
├── cli.py                       # 命令行接口
│
├── examples/                    # 示例代码
│   ├── demo.py                  # 基础演示
│   └── tutorial.py              # 完整教程
│
├── tests/                       # 测试文件
│   ├── __init__.py
│   ├── test_system.py           # 系统级测试
│   └── test_layers.py           # 各层单元测试
│
├── docs/                        # 文档
│   ├── architecture.md          # 架构设计文档
│   ├── api_reference.md         # API参考
│   └── philosophy.md            # 设计哲学
│
├── data/                        # 数据存储 (gitignored)
│   ├── memory/                  # 记忆存储
│   ├── audit/                   # 审计日志
│   └── evolution/               # 演化记录
│
└── 20260320-十一层架构.md        # 原始架构设计文档
```

## 文件职责说明

### 核心文件

| 文件 | 职责 |
|------|------|
| `system.py` | 主系统类，协调所有11层，提供统一接口 |
| `utils.py` | 通用工具函数 (ID生成、风险评分、语义搜索等) |
| `cli.py` | 命令行工具入口 |

### 层级文件 (L0-L10)

| 文件 | 层级 | 名臣 | 职责 |
|------|------|------|------|
| `core/constitution.py` | L0 | 秦始皇 | 宪法引擎，一票否决权 |
| `l1_identity.py` | L1 | 诸葛亮 | 人设边界检查 |
| `l2_perception.py` | L2 | 魏征 | 现实对账，意图识别 |
| `l3_reasoning.py` | L3 | 张良 | 多路径推演 |
| `l4_memory.py` | L4 | 司马迁 | 语义索引，史料编纂 |
| `l5_decision.py` | L5 | 包拯 | 决策存证，审计落槌 |
| `l6_experience.py` | L6 | 曾国藩 | 复盘机制，模式固化 |
| `l7_evolution.py` | L7 | 商鞅 | 内核重构，变法执行 |
| `l8_interface.py` | L8 | 张骞 | 算力外交，模型调用 |
| `l9_agent.py` | L9 | 韩信 | 跨设备执行，工具调度 |
| `l10_sandbox.py` | L10 | 庄子 | 影子宇宙，模拟推演 |

### 核心模块 (core/)

| 文件 | 职责 |
|------|------|
| `constants.py` | 系统常量：层级标识、消息类型、风险等级等 |
| `types.py` | 数据类型定义：Message, ModelResponse, MemoryEntry等 |
| `message.py` | 消息总线实现，层间通信机制 |
| `constitution.py` | L0意志层实现 |
| `audit.py` | 审计日志系统 |

## 数据流

```
用户输入
    ↓
L2 感知层 (observe)
    ↓
┌─────────────┐    ┌─────────────┐
│ L0 意志层   │    │ L1 身份层   │
│ (合宪检查)  │    │ (边界检查)  │
└─────────────┘    └─────────────┘
    ↓                    ↓
    └────────┬───────────┘
             ↓
L4 记忆层 (retrieve)
    ↓
L3 推理层 (reason)
    ↓
L5 决策层 (adjudicate)
    ↓
┌─────────────┐    ┌─────────────┐
│ L10 沙盒层  │    │ L8 接口层   │
│ (模拟验证)  │    │ (模型调用)  │
└─────────────┘    └─────────────┘
    ↓                    ↓
    └────────┬───────────┘
             ↓
L9 代理层 (execute)
    ↓
┌─────────────┐    ┌─────────────┐
│ L6 经验层   │    │ L7 演化层   │
│ (复盘记录)  │    │ (检查变法)  │
└─────────────┘    └─────────────┘
```

## 快速导航

- **开始使用**: 阅读 `README.md`，运行 `examples/demo.py`
- **了解架构**: 阅读 `docs/architecture.md`
- **查看API**: 阅读 `docs/api_reference.md`
- **理解哲学**: 阅读 `docs/philosophy.md`
- **学习教程**: 运行 `examples/tutorial.py`
- **运行测试**: `pytest tests/`

## 扩展开发

### 添加新的心智模型 (L3)

编辑 `l3_reasoning.py`，在 `MindModel` 类中添加新的分析模型。

### 添加新的数据源 (L2)

编辑 `l2_perception.py`，实现 `DataSource` 接口并注册。

### 添加新的工具 (L9)

编辑 `l9_agent.py`，实现 `Tool` 接口并注册到工具箱。

### 修改宪法条款 (L0)

编辑 `config.yaml` 中的 `constitution` 部分，或运行时调用 `constitution.add_clause()`。

