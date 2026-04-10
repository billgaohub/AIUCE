# 🏯 十一层架构 AI 系统 - 快速开始

## 一键启动

```bash
cd /Users/bill/SONUV/BILL_WORKSPACE/05_PROJECTS/AIUCE/repo

# 方式1: 虚拟环境启动（推荐）
source .venv/bin/activate && python3 api.py

# 方式2: 直接启动
python3 api.py
```

启动后会自动打开浏览器访问 Web 界面。

## 访问地址

| 服务 | 地址 |
|------|------|
| **Web 界面** | http://localhost:8000/static/index.html |
| **API 文档** | http://localhost:8000/docs |
| **API 地址** | http://localhost:8000 |

## 功能特性

### 🏛️ 十一层架构

- **L0 意志层** (秦始皇) - 最高宪法，一票否决
- **L1 身份层** (诸葛亮) - 人设边界，防止越权
- **L2 感知层** (魏征) - 现实对账，只说真话
- **L3 推理层** (张良) - 多路径推演
- **L4 记忆层** (司马迁) - 全域语义索引
- **L5 决策层** (包拯) - 决策存证审计
- **L6 经验层** (曾国藩) - 复盘机制
- **L7 演化层** (商鞅) - 内核重构
- **L8 接口层** (张骞) - 算力外交
- **L9 代理层** (韩信) - 跨设备执行
- **L10 沙盒层** (庄子) - 影子宇宙模拟

### 💬 使用方式

**1. Web 界面**
打开 http://localhost:8000/static/index.html 直接在浏览器中对话

**2. API 调用**
```bash
# 查看状态
curl http://localhost:8000/status

# 对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 简单对话
curl -X POST http://localhost:8000/chat/simple \
  -H "Content-Type: application/json" \
  -d '{"message": "介绍一下自己"}'
```

**3. Python 代码**
```python
from system import create_system

system = create_system()
response = system.chat("你好")
print(response)
```

### 📡 多入口通道

配置环境变量后，API 自动支持飞书/Telegram：

```bash
# 飞书
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx

# Telegram
export TELEGRAM_BOT_TOKEN=xxx:xxx
```

配置后自动启用，详见 [docs/channels.md](docs/channels.md)。

## 项目结构

```
aiuce/
├── api.py              # FastAPI 服务 (v1.4.0) ⭐
├── system.py           # 十一层系统主入口
├── core/               # 核心模块
│   ├── constitution.py  # L0 合宪性网关（秦始皇）
│   ├── identity.py      # L1 身份边界
│   ├── l2_reality_sensor.py # L2 感知层（魏征）
│   ├── l3_reasoning.py   # L3 推理引擎（张良）
│   ├── l4_memory.py     # L4 记忆存储（司马迁）
│   ├── l5_decision.py   # L5 决策审计（包拯）
│   ├── memory_sal.py    # L4 分级存储抽象层
│   ├── neural_bus.py    # 神经总线事件溯源
│   ├── evolution.py    # L6/L7 双核演化（曾国藩/商鞅）
│   ├── l9_agent.py      # L9 代理执行（韩信）
│   ├── message.py       # 消息总线
│   ├── constants.py     # 系统常量
│   └── channels/        # 多入口通道 ⭐
│       ├── base.py      # 统一适配器接口
│       ├── feishu.py    # 飞书适配器
│       ├── telegram.py   # Telegram 适配器
│       └── manager.py   # 通道管理器
├── docs/               # 文档
├── tests/              # 测试文件
└── examples/           # 示例代码
```

## 常用命令

```bash
# 启动服务
./run.sh

# 运行演示
python3 demo.py

# 运行教程
python3 examples/tutorial.py

# 运行测试
python3 -m unittest tests.test_system -v

# 停止服务
lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9
```

## 配置

编辑 `config.yaml` 修改系统配置：

```yaml
constitution:
  clauses:
    - id: "privacy"
      content: "绝不泄露用户隐私"
      
identity:
  name: "AI助手"
  
interface:
  providers:
    openai:
      model: "gpt-4"
```

## 停止服务

```bash
# 查找并停止
lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9
```

---

**系统已就绪，运行 `./run.sh` 开始体验！** 🎉
