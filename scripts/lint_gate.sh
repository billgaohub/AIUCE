#!/usr/bin/env bash
# 增量 lint 门禁（I3）
#
# 只在「新增 lint 错误数超过基线」时失败，不要求零错误——
# 避免对存量债务做高风险的大批量修改，同时防止新代码回退质量。
#
# 用法：
#   bash scripts/lint_gate.sh
# 退出码：0 = 通过（未引入回退）；1 = 失败（错误数较基线回退）
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"

BASELINE="${HERE}/lint_baseline.txt"
if [[ ! -f "$BASELINE" ]]; then
  echo "❌ 缺少基线文件: $BASELINE" >&2
  exit 1
fi

FLAKE8_BASE="$(grep -E '^FLAKE8_ERRORS=' "$BASELINE" | cut -d= -f2)"
MYPY_BASE="$(grep -E '^MYPY_ERRORS=' "$BASELINE" | cut -d= -f2)"

# 容差：允许的小幅波动（避免计数为 0 时的边界抖动）
TOLERANCE=0

# flake8：错误行数
FLAKE8_NOW="$(python -m flake8 eleven_layer_ai/ 2>/dev/null | wc -l | tr -d ' ')"
# mypy：末行 "Found N errors ..." 中的 N
MYPY_NOW="$(python -m mypy eleven_layer_ai/ 2>/dev/null | tail -1 | grep -oE '[0-9]+ error' | grep -oE '[0-9]+')"
MYPY_NOW="${MYPY_NOW:-0}"

echo "flake8: now=${FLAKE8_NOW}  baseline=${FLAKE8_BASE}"
echo "mypy:   now=${MYPY_NOW}  baseline=${MYPY_BASE}"

rc=0
if (( FLAKE8_NOW > FLAKE8_BASE + TOLERANCE )); then
  echo "❌ flake8 错误数回退: ${FLAKE8_NOW} > ${FLAKE8_BASE}"
  rc=1
fi
if (( MYPY_NOW > MYPY_BASE + TOLERANCE )); then
  echo "❌ mypy 错误数回退: ${MYPY_NOW} > ${MYPY_BASE}"
  rc=1
fi

if (( rc == 0 )); then
  echo "✅ lint 门禁通过（未引入新的回退）"
fi
exit $rc
