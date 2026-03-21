# 🏯 十一层架构 AI 系统 - 快速开始

## 一键启动

```bash
cd /Users/bill/Downloads/Qclaw_Dropzone/eleven_layer_ai

# 方式1: 使用启动脚本（推荐）
./run.sh

# 方式2: 手动启动
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

## 项目结构

```
eleven_layer_ai/
├── run.sh              # 一键启动脚本 ⭐
├── api.py              # API 服务
├── static/
│   └── index.html      # Web 界面
├── system.py           # 主系统
├── l1_identity.py      # L1 身份层
├── l2_perception.py    # L2 感知层
├── l3_reasoning.py     # L3 推理层
├── l4_memory.py        # L4 记忆层
├── l5_decision.py      # L5 决策层
├── l6_experience.py    # L6 经验层
├── l7_evolution.py     # L7 演化层
├── l8_interface.py     # L8 接口层
├── l9_agent.py         # L9 代理层
├── l10_sandbox.py      # L10 沙盒层
├── core/               # 核心模块
├── examples/           # 示例代码
├── tests/              # 测试文件
└── docs/               # 文档
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
