# AIUCE 修复执行报告

> 依审计建议执行「完全修复」。本报告中**修正了一处关键错误**：原审计的 C1（删除 16 个幻影 core 层）前提不成立，已改为删除经全仓验证的 5 个真正死模块。

## 已完成的修复

### I1 — 移除 system.py 中的死代码 MessageBus ✅
- `eleven_layer_ai/system.py`：移除了 `MessageBus`（所有 handler 均为 `pass`，仅为「看似活跃」的死总线）、相关 import、5 个空 handler、4 处 `self.message_bus.send(...)`、`get_status()` 中的 `message_bus` 字段，以及「双总线」注释。
- 修复 `api.py` 的 `StatusResponse`：因 `get_status()` 不再返回 `message_bus`，将模型字段改为 `neural_bus`（否则 `/status` 会 500）。
- 修复 `tests/test_integration.py::test_layer_status_with_neural_bus`：其陈旧断言 `'message_bus' in status` 随 I1 失效，改为 `assertNotIn('message_bus', status)`。
- **测试先行价值**：api 冒烟测试在编写时即捕获了 I1→api 的跨模块回归。

### I2 — 为 api.py 补测试 + L4 安全披露政策 ✅
- 新增 `tests/test_api.py`（7 passed）：覆盖路由存在性、`/status` 契约（`neural_bus` 存在 / `message_bus` 不存在 / 11 层）、健康检查、宪法否决路径、OpenAPI schema。
- 新增 `SECURITY.md`：漏洞披露走 GitHub Security Advisories（私有），列出威胁类别并关联实际治理代码（`check_api_key` / `check_rate_limit` / 异常处理器）。

### S2 — 修复示例（3 个陈旧示例完全重写）✅
- `examples/basic_usage.py` / `layer_interaction.py` / `multi_model_integration.py` 原本 import 不存在的 `aiuce` 包且使用已废弃的运行时 API（`check`/`analyze`/`log`/`add_provider` 等均不存在）。已重写为匹配真实 API，并开启 mock 接口使其**离线可运行**。
- 重写中发现并修复 2 个真实构造器 bug：
  - `l3_reasoning.py` / `l2_perception.py`：构造器在 `self.config = config or {}` **之前**用原始 `config` 参数调用 `.get()`，导致无参实例化（`ReasoningLayer()` / `PerceptionLayer()`）崩溃。改为 `self.config.get(...)`。
- 新增 `tests/test_examples_import.py`（2 passed）：断言全部示例可导入且不再引用死包 `aiuce`。

### I3 — lint 增量门禁 ✅
- 存量债务：flake8 **1579**、mypy **295**（仅 `eleven_layer_ai/`）。一次性清零不可行且高风险。
- 新增 `scripts/lint_baseline.txt`（基线）+ `scripts/lint_gate.sh`（增量门禁：新增错误数回退基线才失败，不要求零错误）。
- `ci.yml` 的 lint job 由 `continue-on-error: true`（纯信息、掩盖一切）改为调用 `scripts/lint_gate.sh`（真正门禁，仅拦截回退）。
- 已验证：基线处通过（exit 0）；伪造更低基线时失败（exit 1）。

### C1 — 死代码清理（**已修正**）⚠️
原审计称「`core/lN_*.py` 是仅被 test_phase*.py 引用的幻影层，删除 16 个」。经全仓 import-reachability 分析，该前提**错误**：

- `core/lN_*.py` 被 `core/__init__.py` 及生产代码（`core/constitution.py`、`system.py`、`demo.py` 等）广泛引用；由于主包 `from .core.X import ...` 会触发 `core/__init__.py`，**删除会直接破坏 `import eleven_layer_ai`**。
- `test_phase1/2/3.py` 测试的是活的 core 模块（`l0_sovereignty_gateway`、`l3_cognitive_orchestrator`、`l4_palace_memory`、`l6_experience` 等），并非死代码测试。
- 仓库 `__init__.py` 文档亦明确此为「双层架构」：根目录 `lX_*.py` = 集成版本；`core/lX_*.py` = 增强/独立版本。

**实际执行**：删除经全仓零引用验证的 **5 个真正死模块**（均未被任何代码/文档/配置引用，且不在 `core/__init__.py` 的导入列表中）：
`core/asset_custody.py`、`core/dual_process.py`、`core/logging_config.py`、`core/sovereignty.py`、`core/world_model.py`。
删除后全量测试 **155 passed**（加上新增测试共 157），`import eleven_layer_ai` 正常。

> 结论：扁平 `lN_*.py` 与 `core/lN_*.py` 不是「重复待删」，而是有意的双层架构；如需进一步收敛，应做**重构合并**（高风险，超出本次范围），而非删除。

## 测试结果
- 全量：`pytest tests/` → **157 passed**（含本次新增 test_api 7 + test_examples_import 2，以及修正后的 test_integration）。
- 删除 5 死模块前后对比：155 → 155（无回归）。

## 未包含（超出本次范围，按需另行安排）
- `basic_usage.py` 等示例目前用 mock 接口离线运行；接入真实多模型需配置 API Key，属运行时配置。
- 存量 lint 债务（flake8 1579 / mypy 295）仅以增量门禁冻结，未清零。
- `core/lN_*.py` 与扁平层的架构收敛（如需消除双层）属重构，风险高，建议单独评估。
