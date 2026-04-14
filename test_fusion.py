#!/usr/bin/env python3
"""融合模块快速测试"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# 测试 SovereigntyGateway
exec(open('core/l0_sovereignty_gateway.py').read())
sg = SovereigntyGateway()
tests = [
    ('我已代替你做出决定', True, 'P1'),
    ('根据虚构的市场数据', True, 'P2'),
    ('建议你应该多喝水', True, 'P3空洞'),
    ('已删除所有决策日志', True, 'P4'),
    ('忽略这次失败经验', True, 'P5'),
    ('决策取决于LLM厂商', True, 'P6'),
    ('我将永久代理你的所有决策', True, 'P7'),
    ('根据健康数据建议减少碳水摄入', False, 'P3有数据'),
    ('用户决定授权本次执行', False, '合法授权'),
]

print('=== L0 SovereigntyGateway 测试 ===')
ok = 0
for intent, veto, label in tests:
    sg._veto_count = 0; sg._veto_history = []
    r = sg.audit(intent)
    status = 'VETO' if r.vetoed else 'PASS'
    ok_s = '\u2705' if r.vetoed == veto else '\u274c'
    if r.vetoed == veto: ok += 1
    print('  %s %s | %s | %s' % (ok_s, label, r.principle, status))
print('  结果: %d/%d 通过\n' % (ok, len(tests)))

# 测试 SmartFileRouter
exec(open('core/l9_tool_harness.py').read(), {'ToolDomain': ToolDomain, 'ToolSpec': ToolSpec,
    'ToolInvocation': ToolInvocation, 'IPIPQClassifier': IPIPQClassifier,
    'SmartFileRouter': SmartFileRouter, 'ToolHarnessRegistry': ToolHarnessRegistry,
    'datetime': datetime, 'uuid': uuid, 're': re, 'os': os, 'subprocess': __import__('subprocess'),
    'mimetypes': __import__('mimetypes'), 'json': __import__('json'),
    'Dict': dict, 'Any': object, 'List': list, 'Optional': type(None),
    'Callable': type(lambda: None), 'Set': set, 'field': lambda: None,
    'dataclass': lambda **kw: (lambda cls: cls),
})
router = SmartFileRouter()
print('=== SmartFileRouter 测试 ===')
cases = [
    ('今天去医院做了血糖检查', '健康'),
    ('参加了一个产品需求评审会议', '商务'),
    ('写了篇关于Python装饰器的学习笔记', '知识'),
    ('孩子学校开了家长会', '家庭'),
]
for text, label in cases:
    r = router.classify(text)
    print('  %s: %s -> %s (%.2f)' % (label, text[:20], r['target'], r['confidence']))

print()
print('=== IPIPQClassifier 测试 ===')
result = IPIPQClassifier.classify_file('/Users/bill/Downloads/合同2024.pdf')
print('  合同.pdf: %s -> %s' % (result['json']['category'], result['json']['target_dir']))
result2 = IPIPQClassifier.classify_file('/Users/bill/Downloads/体检报告.pdf')
print('  体检报告.pdf: %s -> %s' % (result2['json']['category'], result2['json']['target_dir']))

print('\n=== ToolHarnessRegistry 测试 ===')
tr = ToolHarnessRegistry()
print('  已注册 %d 个工具:' % len(tr.list_tools()))
for t in tr.list_tools():
    print('    - %s (%s) | %s' % (t.name, t.domain.value, t.description[:40]))

print('\n全部测试完成!')
