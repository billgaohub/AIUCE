"""
Examples 导入冒烟测试（S2：此前 3 个示例 import 了不存在的 aiuce 包）。

策略：将 examples/ 加入 sys.path，用 importlib 导入全部示例模块，
断言其顶层 demonstrate_* 入口函数存在且可调用。
示例仅在 __main__ 中执行，导入本身不触发网络/模型调用，因此快速且离线。

运行：
    python -m pytest tests/test_examples_import.py -v
"""

import importlib
import os
import sys

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

# 每个示例模块名 -> 期望存在的演示入口函数
EXPECTED = {
    "demo": "demo_basic",
    "tutorial": "tutorial_basic_usage",
    "basic_usage": "demonstrate_basic_usage",
    "layer_interaction": "demonstrate_layer_interaction",
    "multi_model_integration": "demonstrate_multi_model",
}


def _load(module_name):
    if EXAMPLES_DIR not in sys.path:
        sys.path.insert(0, EXAMPLES_DIR)
    return importlib.import_module(module_name)


def test_all_examples_import_without_aiuce_package():
    """全部示例都能导入（不再引用不存在的 aiuce 包）。"""
    for name in EXPECTED:
        mod = _load(name)  # 若仍 import aiuce 会在此抛 ModuleNotFoundError
        assert hasattr(mod, EXPECTED[name]), f"{name} 缺少入口函数 {EXPECTED[name]}"
        assert callable(getattr(mod, EXPECTED[name])), f"{name}.{EXPECTED[name]} 不可调用"


def test_no_stale_aiuce_import():
    """确认没有任何示例仍在 import 死包 aiuce。"""
    import pathlib

    for path in pathlib.Path(EXAMPLES_DIR).glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "from aiuce" not in text and "import aiuce" not in text, (
            f"{path.name} 仍引用死包 aiuce"
        )
