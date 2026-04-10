# AIUCE System 🏯

[![CI](https://github.com/billgaohub/AIUCE/actions/workflows/ci.yml/badge.svg)](https://github.com/billgaohub/AIUCE/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

> **AIUCE** = **A**I System + **U**niverse + **C**onstitution + **E**volution
>
> Personal AI Infrastructure with Layered Governance

AIUCE 不仅是本项目的代号，更是这套 Personal AI Infrastructure 核心运行机制的微缩密码。它由四个代表系统底层哲学的核心概念缩写而成，完美映射了我们基于「十一层架构」的分层治理、主权制衡与渐进式演化思想。

---

## 命名释义

### 🤖 A - AI System (十一层架构人工智能)

代表我们构建的具备分层治理、制衡机制与记忆能力的有机体。系统借鉴了中国古代官僚体系的智慧，打破了单一大模型的「黑箱」局限，实现了从感知、推理、决策到物理执行的完整多体协同生命周期。

**对应层级**: L0-L10 全架构

---

### 🌌 U - Universe (影子宇宙)

对应系统 **L10 沙盒层（庄子/钦天监）** 的核心机制。系统在虚拟的「影子宇宙」中通过蒙特卡洛模拟和 A/B 测试，模拟百万次失败，以此来验证高风险决策，只为在现实中坍缩出一条可行的生路。

**核心能力**:
- 蒙特卡洛模拟
- A/B 测试验证
- 影子推演空间

---

### ⚖️ C - Constitution (最高宪法)

对应系统 **L0 意志层（秦始皇/御书房）** 的绝对主权。作为系统的最高权力中心，它存放着最高宪法，依靠严格的合宪性检查，对一切偏离主权意志的指令行使「一票否决权」，确保 AI 永远处于绝对可控的轨道上。

**核心能力**:
- 一票否决权
- 合宪性检查
- 最高意志守护

---

### 🔄 E - Evolution (渐进式演化)

代表系统的核心生命力——渐进式演化哲学，对应 **L7 演化层（商鞅/中书省）** 的变法机制。系统通过持续的反馈循环，一旦经验层证明旧逻辑已过时，便会立即在物理层面重构内核代码与权重，实现真正的系统自动演化与自我变法。

**核心能力**:
- 每日复盘机制
- 成功模式固化
- 内核自动重构

---

## 十一层架构

| 层级 | 架构层 | 名臣 | 部门 | 核心能力 | AIUCE 映射 |
|------|--------|------|------|----------|------------|
| L0 | 意志层 | 秦始皇 | 御书房 | 最高宪法，一票否决 | **C**onstitution |
| L1 | 身份层 | 诸葛亮 | 宗人府 | 人设边界，防止越权 | AI System |
| L2 | 感知层 | 魏征 | 都察院 | 现实对账，只说真话 | AI System |
| L3 | 推理层 | 张良 | 军机处 | 多路径推演 | AI System |
| L4 | 记忆层 | 司马迁 | 翰林院 | 语义索引，史料编纂 | AI System |
| L5 | 决策层 | 包拯 | 大理寺 | 决策存证，审计落槌 | AI System |
| L6 | 经验层 | 曾国藩 | 吏部 | 复盘机制，偏离扫描 | **E**volution |
| L7 | 演化层 | 商鞅 | 中书省 | 内核重构，物理变法 | **E**volution |
| L8 | 接口层 | 张骞 | 礼部 | 算力外交，模型调用 | AI System |
| L9 | 代理层 | 韩信 | 锦衣卫 | 跨设备执行，工具调度 | AI System |
| L10 | 沙盒层 | 庄子 | 钦天监 | 影子宇宙，模拟推演 | **U**niverse |

---

## 核心特性

### 🏛️ 分层治理
- 每层职责明确，互不越权
- L0/L1 拥有否决权，制衡机制完善
- 数据流清晰：感知 → 推理 → 决策 → 执行

### 🔄 渐进演化
- L6 每日复盘，扫描偏离度
- L7 自动变法，重构内核
- 保守但持续的自我改进

### 🔒 安全可控
- L0 宪法一票否决
- L10 沙盒模拟验证
- 全链路审计日志

### 🌐 开放集成
- FastAPI 后端服务
- Web 可视化界面
- Docker 容器化部署

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/billgaohub/aiuce.git
cd aiuce

# 一键启动
./run.sh
```

访问 http://localhost:8000/static/index.html 查看 Web 界面。

---

## 架构哲学

> "治大国若烹小鲜" —— 老子

AIUCE 系统借鉴中国古代两千年的官僚治理智慧，为现代 AI 系统提供一种可持续的治理模式：

- **分层**让复杂系统可控
- **制衡**让权力不被滥用
- **审计**让决策可追溯
- **演化**让系统持续改进

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📚 文档

- [快速开始](QUICKSTART.md) - 5分钟上手
- [架构设计](docs/architecture.md) - 深入了解十一层架构
- [开源集成指南](docs/integration.md) - 如何集成 Deer-flow、Hermes 等组件
- [API 参考](docs/api_reference.md) - 完整的 API 文档
- [设计哲学](docs/philosophy.md) - AIUCE 的设计思想
- [贡献指南](CONTRIBUTING.md) - 如何参与贡献
- [更新日志](CHANGELOG.md) - 版本历史

## 🚀 社区项目

| 项目 | 状态 | 说明 |
|------|------|------|
| [IPIPQ](https://github.com/billgaohub/ipipq) | ✅ Active | AI 文件自动整理工具（主变现产品） |
| [teonu-worldmodel](https://github.com/billgaohub/teonu-worldmodel) | 📦 Archived | 元认知调度引擎（已合并至 AGF） |
| [agent-sovereignty-rules](https://github.com/billgaohub/agent-sovereignty-rules) | 📦 Archived | 决策权保护框架（已合并至 AGF） |
| [smart-file-router](https://github.com/billgaohub/smart-file-router) | 📦 Archived | 智能文件分类引擎（已演进为 IPIPQ） |

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

**AIUCE** - Personal AI Infrastructure with Layered Governance  
🏯 治大国若烹小鲜
