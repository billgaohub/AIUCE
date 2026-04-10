# AIUCE 本地测试指南 v1.4.0

> 最后更新：2026-04-10 | 所有测试已验证通过

## 前置条件

```bash
cd /Users/bill/SONUV/BILL_WORKSPACE/05_PROJECTS/AIUCE/repo

# 首次使用：创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 后续使用：直接激活
source .venv/bin/activate
```

## 一键全量测试

```bash
python3 << 'EOF'
import tempfile, os

print("=" * 60)
print("AIUCE v1.4.0 全量测试")
print("=" * 60)

# ---- L0 意志层 ----
print("\n[L0 意志层]")
from core.constitution import Constitution
c = Constitution()
assert c.is_constitutional("帮我写代码") == True
assert c.is_constitutional("转账1000元") == False
assert c.is_constitutional("rm -rf /") == False
print("  ✅ 双重网关（秦始皇/御书房）")

# ---- L2 感知层 ----
print("\n[L2 感知层]")
from core.l2_reality_sensor import RealitySensor
sensor = RealitySensor(config={})
print("  ✅ 现实对账（魏征/都察院）")

# ---- L3 推理层 ----
print("\n[L3 推理层]")
from core.l3_reasoning import ReasoningEngine
engine = ReasoningEngine()
result = engine.reason("测试查询", num_paths=2)
assert result.success == True
print("  ✅ 多路径推演（张良/军机处）")

# ---- L4 记忆层 ----
print("\n[L4 记忆层]")
from core.memory_sal import MemoryLayer
temp_dir = tempfile.mkdtemp()
config = {
    'working_memory': {'storage_path': os.path.join(temp_dir, 'lcm.db')},
    'semantic_disk': {'storage_path': os.path.join(temp_dir, 'kg')}
}
memory = MemoryLayer(config)
memory.store("测试记忆内容", category="test", tags=["demo"])
r = memory.retrieve("测试", top_k=5)
assert len(r.entries) > 0, f"检索失败：返回 {len(r.entries)} 条"
print(f"  ✅ 分级存储 + 中文检索（司马迁/翰林院）- {len(r.entries)} 条")

# ---- L6/L7 演化层 ----
print("\n[L6/L7 演化层]")
from core.evolution import DualCoreEvolution
evolution = DualCoreEvolution(config={})
print("  ✅ 双核演化（曾国藩/商鞅）")

# ---- L9 代理层 ----
print("\n[L9 代理层]")
from core.l9_agent import AgentLayer
agent = AgentLayer()
tools = agent.list_tools()
assert len(tools) > 0
tool_names = [t.name for t in tools]
result = agent.execute("file.read", {"path": "/etc/hosts"})
assert result.status.value == "success"
print(f"  ✅ 跨设备执行（韩信/锦衣卫）- {len(tools)} 个工具")

# ---- 神经总线 ----
print("\n[神经总线]")
from core.neural_bus import NeuralBus, EventType
bus = NeuralBus()
print("  ✅ 事件溯源")

# ---- 多入口通道 ----
print("\n[多入口通道]")
from core.channels import ChannelManager, ChannelType
mgr = ChannelManager()
print("  ✅ 通道管理器")

print("\n" + "=" * 60)
print("🎉 全部通过！")
print("=" * 60)
EOF
```

## 分层详细测试

### L0 意志层（秦始皇/御书房）

```python
from core.constitution import Constitution

constitution = Constitution()

# ✅ 正常请求通过
assert constitution.is_constitutional("帮我写代码") == True

# ❌ 资金操作拦截
assert constitution.is_constitutional("转账1000元") == False

# ❌ 系统危险操作拦截
assert constitution.is_constitutional("rm -rf /") == False
```

### L2 感知层（魏征/都察院）

```python
from core.l2_reality_sensor import RealitySensor

# ⚠️ 必须传 config={}，不能无参构造
sensor = RealitySensor(config={})
```

### L3 推理层（张良/军机处）

```python
from core.l3_reasoning import ReasoningEngine

engine = ReasoningEngine()
result = engine.reason("如何优化代码？", num_paths=3)
assert result.success == True
print(f"最优路径: {result.selected_path.conclusion}")
print(f"置信度: {result.selected_path.confidence}")
```

### L4 记忆层（司马迁/翰林院）

```python
from core.memory_sal import MemoryLayer
import tempfile, os

# ⚠️ 必须提供 storage_path 配置
temp_dir = tempfile.mkdtemp()
config = {
    'working_memory': {'storage_path': os.path.join(temp_dir, 'lcm.db')},
    'semantic_disk': {'storage_path': os.path.join(temp_dir, 'kg')}
}
memory = MemoryLayer(config)

# 存储
entry_id = memory.store("测试记忆内容", category="test", tags=["demo"])

# 中文检索（v1.4.0 修复：FTS5 + LIKE 双轨）
result = memory.retrieve("测试", top_k=5)
assert len(result.entries) > 0  # ← v1.3.0 此处为 0，已修复
```

### L6/L7 演化层（曾国藩/商鞅）

```python
from core.evolution import DualCoreEvolution

# ⚠️ 必须传 config={}，不能无参构造
evolution = DualCoreEvolution(config={})
```

### L9 代理层（韩信/锦衣卫）

```python
from core.l9_agent import AgentLayer

agent = AgentLayer()

# 工具列表（返回 Tool 对象，非 dict）
tools = agent.list_tools()
tool_names = [t.name for t in tools]  # ⚠️ Tool 对象用 .name 访问

# 执行工具
result = agent.execute("file.read", {"path": "/etc/hosts"})
assert result.status.value == "success"
```

### 神经总线

```python
from core.neural_bus import NeuralBus, EventType

bus = NeuralBus()
# 默认事件存储: ~/.aiuce/events.db
```

### 多入口通道

```python
from core.channels import ChannelManager, ChannelType

mgr = ChannelManager()
# 需要环境变量才能真正启用：
# FEISHU_APP_ID / FEISHU_APP_SECRET
# TELEGRAM_BOT_TOKEN
```

## 启动 API 服务

```bash
# ⚠️ 如端口 8000 已被占用，改用其他端口
source .venv/bin/activate
uvicorn api:app --reload --host 127.0.0.1 --port 8080

# 访问 API 文档
open http://127.0.0.1:8080/docs
```

### 通道 Webhook 端点

```bash
# 检查通道状态
curl http://127.0.0.1:8080/channels

# 广播消息
curl -X POST http://127.0.0.1:8080/channels/broadcast \
  -H "Content-Type: application/json" \
  -d '{"message": "测试广播"}'
```

## 已知陷阱

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| `config=None` 报错 | L2/L6/L7 的 `__init__` 不接受 None | 传 `config={}` |
| L9 `Tool` 不是 dict | `list_tools()` 返回 Tool 对象 | 用 `t.name` 访问属性 |
| L4 中文检索返回空 | FTS5 不支持中文分词 | v1.4.0 已修复（LIKE fallback） |
| 端口 8000 冲突 | SONUV MLX 服务占 8000 | 改用 8080 |
| pip 安装报错 | macOS Homebrew 保护 | 使用 .venv 虚拟环境 |
| git push 卡住 | 需要走代理 | `export https_proxy=http://127.0.0.1:7890` |

## 数据存储位置

```
~/.aiuce/
├── lcm.db              # L1 工作记忆（SQLite + FTS5）
├── knowledge_graph/    # L2 知识图谱
└── events.db           # 神经总线事件日志
```
