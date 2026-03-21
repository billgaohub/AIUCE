# Eleven-Layer AI System
# 十一层架构 AI 系统

## 简介

基于「十一层架构」理念构建的AI系统，每层职责明确，层间通信规范。

## 架构层次

| 层级 | 架构层 | 驻守名臣 | 核心部门 | 主权内涵 |
|------|--------|----------|----------|----------|
| L0 | 意志层 | 秦始皇 | 御书房 | 定鼎：最高宪法，一票否决权 |
| L1 | 身份层 | 诸葛亮 | 宗人府 | 守本：人设管家，防止越权 |
| L2 | 感知层 | 魏征 | 都察院 | 风闻：现实对账，只说真话 |
| L3 | 推理层 | 张良 | 军机处 | 参赞：多路径推演，后果分析 |
| L4 | 记忆层 | 司马迁 | 翰林院 | 修史：全域语义索引，史料编纂 |
| L5 | 决策层 | 包拯 | 大理寺 | 落槌：决策存证，审计日志 |
| L6 | 经验层 | 曾国藩 | 吏部 | 考功：复盘机制，偏离度扫描 |
| L7 | 演化层 | 商鞅 | 中书省 | 草拟：内核重构，物理变法 |
| L8 | 接口层 | 张骞 | 礼部 | 邦交：算力外交，丝绸之路 |
| L9 | 代理层 | 韩信 | 锦衣卫 | 执行：跨设备执行，物理调度 |
| L10 | 沙盒层 | 庄子 | 钦天监 | 观星：影子宇宙，模拟推演 |

## 数据流

```
外部输入 → L2感知 → L3推理 → L4记忆 → L5决策 → L7演化 → L8接口 → L9执行
            ↑                                               ↓
            ←─────────── L10沙盒模拟 ← ← ← ← ← ← ← ← ← ← ←
            ↓
       L0意志 + L1身份 ← 可一票否决任意上层
       L6经验  ← 每日复盘，L7提供演化依据
```

## 安装

```bash
# 克隆仓库
git clone <repo-url>
cd eleven_layer_ai

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

```python
from eleven_layer_ai import create_system

# 创建系统实例
system = create_system()

# 简单对话
response = system.chat("你好，今天天气怎么样？")
print(response)

# 查看系统状态
status = system.get_status()
print(status)
```

## 项目结构

```
eleven_layer_ai/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── setup.py                  # 安装脚本
├── config.yaml               # 配置文件
├── .gitignore                # Git忽略文件
│
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── constants.py          # 常量定义
│   ├── types.py              # 类型定义
│   ├── message.py            # 消息总线
│   ├── constitution.py       # L0: 意志层/宪法引擎
│   └── audit.py              # 审计日志
│
├── l1_identity.py            # L1: 身份层
├── l2_perception.py          # L2: 感知层
├── l3_reasoning.py           # L3: 推理层
├── l4_memory.py              # L4: 记忆层
├── l5_decision.py            # L5: 决策层
├── l6_experience.py          # L6: 经验层
├── l7_evolution.py           # L7: 演化层
├── l8_interface.py           # L8: 接口层
├── l9_agent.py               # L9: 代理层
├── l10_sandbox.py            # L10: 沙盒层
├── system.py                 # 主系统入口
├── utils.py                  # 工具函数
│
├── examples/                 # 示例代码
│   ├── demo.py
│   └── tutorial.py
│
├── tests/                    # 测试文件
│   ├── __init__.py
│   ├── test_system.py
│   └── test_layers.py
│
├── docs/                     # 文档
│   ├── architecture.md
│   ├── api_reference.md
│   └── philosophy.md
│
└── data/                     # 数据存储
    ├── memory/
    ├── audit/
    └── evolution/
```

## 配置

编辑 `config.yaml` 来自定义系统行为：

```yaml
constitution:
  clauses:
    - id: "privacy"
      content: "绝不泄露用户隐私数据"
      priority: 10

identity:
  name: "AI助手"
  traits: ["helpful", "honest", "harmless"]

memory:
  storage_path: "./data/memory"
  max_entries: 10000

interface:
  providers:
    openai:
      model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"
```

## API 参考

### ElevenLayerSystem

主系统类，协调所有层级。

```python
system = ElevenLayerSystem(config)

# 处理用户输入
result = system.run(user_input)

# 快捷对话
response = system.chat(user_input)

# 每日复盘
review = system.daily_review()

# 获取状态
status = system.get_status()

# 获取审计日志
logs = system.get_audit_log(limit=100)
```

## 开发

```bash
# 运行测试
pytest tests/

# 运行示例
python examples/demo.py

# 代码格式化
black eleven_layer_ai/
```

## 许可证

MIT License

## 致谢

- 架构设计灵感来源于中国古代官僚体系
- 历史人物隐喻帮助理解各层职责
