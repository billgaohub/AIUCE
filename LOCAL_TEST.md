# AIUCE 本地测试指南

## 快速开始

### 1. 创建虚拟环境

```bash
cd /Users/bill/SONUV/BILL_WORKSPACE/05_PROJECTS/AIUCE/repo
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行核心测试

```bash
# 测试所有核心模块
python3 -c "
from core.constitution import Constitution
from core.memory_sal import MemoryLayer
from core.neural_bus import NeuralBus, EventType
from core.evolution import DualCoreEvolution
from core.l2_reality_sensor import RealitySensor
from core.l3_reasoning import ReasoningEngine
from core.l9_agent import AgentLayer

print('✅ 所有模块导入成功')

# L0 测试
constitution = Constitution()
assert constitution.is_constitutional('正常请求') == True
assert constitution.is_constitutional('转账1000元') == False
print('✅ L0 双重网关测试通过')

# L3 测试
engine = ReasoningEngine()
result = engine.reason('测试查询', num_paths=2)
assert result.success == True
print('✅ L3 推理引擎测试通过')

# L9 测试
agent = AgentLayer()
tools = agent.list_tools()
assert len(tools) > 0
print('✅ L9 代理层测试通过')

print('\\n🎉 所有测试通过！')
"
```

### 4. 运行完整演示

```bash
python3 examples/demo.py
```

### 5. 启动 API 服务

```bash
# 开发模式
uvicorn api:app --reload --host 127.0.0.1 --port 8000

# 访问 API 文档
open http://127.0.0.1:8000/docs
```

## 测试各层功能

### L0 意志层（宪法）

```python
from core.constitution import Constitution

constitution = Constitution()

# 正常请求
assert constitution.is_constitutional("帮我写代码") == True

# 资金操作被拦截
assert constitution.is_constitutional("转账1000元") == False

# 系统危险操作被拦截
assert constitution.is_constitutional("rm -rf /") == False
```

### L4 记忆层（分级存储）

```python
from core.memory_sal import MemoryLayer
import tempfile, os

temp_dir = tempfile.mkdtemp()
config = {
    'working_memory': {'storage_path': os.path.join(temp_dir, 'lcm.db')},
    'semantic_disk': {'storage_path': os.path.join(temp_dir, 'kg')}
}
memory = MemoryLayer(config)

# 存储
entry_id = memory.store("测试记忆", category="test", tags=["demo"])
print(f"存储ID: {entry_id}")

# 检索
result = memory.retrieve("测试", top_k=5)
print(f"找到 {len(result.entries)} 条记忆")
```

### L3 推理层（Deer-flow）

```python
from core.l3_reasoning import ReasoningEngine, ReasoningStrategy

engine = ReasoningEngine()

# 分解任务
dag = engine.decompose("分析项目并生成报告", strategy=ReasoningStrategy.REACT)
print(f"DAG 包含 {len(dag.tasks)} 个任务")

# 多路径推理
result = engine.reason("如何优化代码？", num_paths=3)
print(f"最优路径: {result.selected_path.conclusion}")
```

### L9 代理层（UI-TARS）

```python
from core.l9_agent import AgentLayer

agent = AgentLayer()

# 列出工具
tools = agent.list_tools()
print(f"可用工具: {len(tools)} 个")

# 执行文件读取
result = agent.execute("file.read", {"path": "/etc/hosts"})
print(f"状态: {result.status}")
```

## 目录结构

```
AIUCE/repo/
├── core/                    # 核心模块
│   ├── constitution.py      # L0 意志层
│   ├── l2_reality_sensor.py # L2 感知层
│   ├── l3_reasoning.py      # L3 推理层
│   ├── memory_sal.py        # L4 记忆层
│   ├── evolution.py         # L6/L7 演化层
│   ├── l9_agent.py          # L9 代理层
│   └── neural_bus.py        # 神经总线
├── examples/
│   └── demo.py              # 演示脚本
├── api.py                   # FastAPI 服务
├── eleven_layer_ai.py       # 主系统入口
└── requirements.txt         # 依赖
```

## 常见问题

### Q: 导入错误？
```bash
# 确保在项目根目录
cd /Users/bill/SONUV/BILL_WORKSPACE/05_PROJECTS/AIUCE/repo
source .venv/bin/activate
pip install -r requirements.txt
```

### Q: SQLite 数据存储在哪？
```bash
# 默认路径
~/.aiuce/lcm.db              # L1 工作记忆
~/.aiuce/knowledge_graph/    # L2 知识图谱
~/.aiuce/events.db           # 神经总线事件
```

### Q: 如何配置 LLM？
```bash
# 创建 .env 文件
cp .env.example .env
# 编辑 .env 填入 API Key
```
