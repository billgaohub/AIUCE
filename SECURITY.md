# Security Policy

## 支持的版本

| 版本 | 支持状态 |
|------|----------|
| 1.1.x | ✅ actively supported |
| 1.0.x | ⚠️ security fixes only |
| < 1.0 | ❌ no longer supported |

## 报告安全漏洞

如果您发现了安全漏洞，请 **不要** 通过公开 issue 报告。

请通过以下方式私下报告：

1. 发送邮件至项目维护者
2. 在邮件主题中注明 "[AIUCE Security]"
3. 提供详细的漏洞描述和复现步骤
4. 等待我们的回复（通常在 48 小时内）

---

## 安全特性 (v1.1.0)

### API 安全

#### 1. API Key 认证
- 所有 API 请求需要携带 `X-API-Key` Header
- 支持多个 API Key（逗号分隔）
- 可通过环境变量 `AIUCE_API_KEYS` 配置
- 开发模式可通过 `AIUCE_AUTH_ENABLED=false` 关闭

```bash
# 设置 API Keys
export AIUCE_API_KEYS="key1,key2,key3"

# 使用 API Key
curl -H "X-API-Key: your-key" http://localhost:8000/status
```

#### 2. Rate Limiting
- 默认限制: 100 请求/分钟
- 可通过环境变量 `AIUCE_RATE_LIMIT` 调整
- 超限返回 429 Too Many Requests

```bash
export AIUCE_RATE_LIMIT="200"  # 每分钟 200 请求
```

#### 3. 异常脱敏
- 所有异常不暴露内部细节
- 返回 request_id 用于追踪
- 详细错误记录在服务端日志

#### 4. CORS 配置
- 可通过 `AIUCE_CORS_ORIGINS` 配置允许的来源
- 默认允许所有来源（`*`）

```bash
export AIUCE_CORS_ORIGINS="https://example.com,https://app.example.com"
```

---

### 执行沙箱 (L9)

L9 代理层实现了安全执行沙箱：

#### 命令白名单
仅允许执行以下安全命令：
```
ls, pwd, cat, echo, grep, find, wc, head, tail
git, python, python3, pip, pip3
curl, wget, npm, node
```

#### 危险字符检测
自动拦截包含以下危险字符的命令：
```
; | & $() > < ` .. 
```

#### 超时限制
- 默认超时: 30 秒
- 最大超时: 120 秒

#### 风险等级分类
- **LOW**: 文件读取、信息查询
- **MEDIUM**: 文件写入、配置修改
- **HIGH**: 系统命令、网络操作
- **CRITICAL**: 删除、格式化、权限修改

---

### 层级安全机制

#### L0 意志层 (Constitution)
- 一票否决权
- 合宪性检查
- 最高意志守护
- 6 条内置宪法条款

#### L1 身份层 (Identity)
- 人设边界检查
- 权限控制
- 越权防护

#### L5 决策层 (Decision)
- 审计日志
- 决策存证
- 可追溯性

#### L10 沙盒层 (Universe)
- 影子模拟
- 风险验证
- 安全测试

---

## 环境变量配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AIUCE_API_KEYS` | API 密钥列表（逗号分隔） | 无 |
| `AIUCE_AUTH_ENABLED` | 是否启用认证 | `true` |
| `AIUCE_RATE_LIMIT` | 每分钟最大请求数 | `100` |
| `AIUCE_CORS_ORIGINS` | CORS 允许来源 | `*` |
| `AIUCE_LOG_LEVEL` | 日志级别 | `INFO` |
| `AIUCE_LOG_FILE` | 日志文件路径 | 无 |

---

## 最佳实践

1. **生产环境必须配置 API Keys**
   ```bash
   export AIUCE_API_KEYS="your-secure-key-here"
   ```

2. **定期更新** - 保持系统更新到最新版本

3. **审查配置** - 定期审查 config.yaml 中的安全设置

4. **监控日志** - 关注审计日志中的异常行为

5. **限制访问** - 生产环境限制 API 访问权限

6. **使用 HTTPS** - 生产环境必须使用 HTTPS

7. **保护 API Keys** - 不要将 API Keys 提交到版本控制

---

## 已知问题

暂无已知安全问题。

---

## 致谢

感谢所有报告安全问题的贡献者！
