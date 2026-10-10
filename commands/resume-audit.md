---
description: 简历体检：跑确定性审计脚本（关键词/日期/联系方式/动词/量化），输出分级报告。
argument-hint: [简历文件] [--jd JD文件] [--fix]
---

# /lhg-resume:resume-audit —— 简历体检

用户输入在 `$ARGUMENTS` 中：`[简历文件] [--jd <JD文件>] [--fix]`。简历文件缺省为 `resume-source.md`。

## 流程（加载 lhg-rs-ats 全程指导）

### 1. 跑脚本
```bash
python3 <插件目录>/scripts/audit/resume_audit.py --target <简历文件或目录> [--jd <JD文件>] --format text
```
记下 blocker / warning / nit 的数量与明细（含行号、规则说明）。

### 2. 分级与修复
- blocker（联系方式缺失等）：逐条修；`--fix` 缺省即自动修（最小改动原则）。
- 修不掉的（如缺真实数字、缺 JD）→ 列入"需人工补充"，不许编数字凑数。
- warning：修掉或写豁免理由；nit：顺手修。

### 3. 人工复核（脚本覆盖不到的）
按 lhg-rs-ats 第 5 节清单执行：
- 数字真实性：每个数字都能说出出处吗
- 动词强度：每条 bullet 第一个词是强动词吗
- JD 针对性：关键词是自然融入还是硬堆
- 一页纸：是否超 2 页，超了砍什么

### 4. 输出报告
按 lhg-rs-ats 第 6 节模板输出体检报告，存为 `resume-audit-YYYYMMDD.md`，结论写清"可投递 / 需修改"。

## 硬规则
- 有 blocker 就说"可投递" → 不许。
- 为清零改脚本规则或阈值 → 作弊，不许。
- 编数字让"量化检查"通过 → 不许，这是红线中的红线。
