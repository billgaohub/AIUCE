# Security Policy

AIUCE（AI Universe Constitution Evolution System）是一套以**安全治理**为核心的 AI 框架。
我们认真对待自身代码的安全问题——如果你发现漏洞，请按以下流程上报。

## 上报渠道（请勿公开）

**请通过 GitHub Security Advisories 私下上报，不要公开开 issue 讨论漏洞细节。**

- 在仓库页面 → **Security** → **Report a vulnerability**（GitHub 私有 advisory，仅维护者可见）
- 或邮件联系维护者（见 `MAINTAINERS` / `CODEOWNERS`）

公开 issue 仅用于功能讨论与非安全类 bug；**安全漏洞请走上述私有渠道**，以便我们在修复前不向攻击者暴露细节。

## 适用范围

- `eleven_layer_ai/` 运行时代码、记忆/治理/策略引擎
- `api.py` 提供的 HTTP / Webhook 服务（认证、限流、通道集成）
- 随仓库发布的配置与构建脚本

## 我们特别关注的风险类别

作为治理框架，以下与本项目的威胁模型高度相关：

- **提示注入 / 越权**：绕过 L0 宪法否决或 L1 人设边界
- **策略引擎绕过**：`PolicyEngine` 的授权判定被规避
- **记忆投毒**：外部内容污染记忆层（`memory_sal` / `hybrid_memory` / `unified_memory`）
- **工具/执行越权**：L9 代理层执行了未授权操作（见 `l9_agent.SafeExecTool`）
- **Webhook / 通道认证缺陷**：飞书 / Telegram webhook 缺少校验
- **依赖供应链**：第三方包漏洞

## 修复与披露

- 维护者确认后会在私有 advisory 中沟通修复排期；
- 修复随安全版本发布，并在 release notes 中致谢上报者（如需匿名亦可）；
- 我们不设漏洞赏金（bounty），但重视每一份负责任的报告。

## 安全设计参考

- 认证：`api.py` 的 `check_api_key` + `AIUCE_AUTH_ENABLED` / `AIUCE_API_KEYS`
- 限流：`api.py` 的 `check_rate_limit`
- 异常脱敏：`api.py` 的 `global_exception_handler`（不向客户端泄露内部堆栈）
- 治理否决：`system.py` 的 L0 / L1 一票否决路径

> 本项目安全实践本身应与框架宣扬的治理原则一致——如发现框架"说一套做一套"，这正是最高优先级的安全问题。
