<!-- About 简介（推送后填写到仓库 About 栏）：
简历优化专家：ATS诊断到模拟面试一条龙 + 针对性求职信 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-resume
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, resume, career, ats -->

# lhg-resume：简历优化专家

> **一句话介绍**：给 AI 助手装上"求职组合拳"——粘贴简历+JD，ATS 诊断→bullet 量化改写→多版本管理→PDF 导出→模拟面试→针对性求职信→LinkedIn 资料打造，一条龙拿到面试。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-resume
> /plugin install lhg-resume@lhg-plugs
> ```

> **🔒 隐私声明（先看这个）**：你的简历只在本地处理，**绝不上传到任何外部服务**；
> 本插件带隐私硬门，会拦截疑似上传简历的命令。另：本插件**不编造任何"已验证"数据**——
> 没有证据的数字一律标 `[待确认]`，绝不替你编。

## 它是什么

`lhg-resume` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **5 个命令**（小白入口）：`resume` 简历优化一条龙，`resume-interview` 模拟面试，`resume-audit` 简历体检，`cover-letter` 针对性求职信，`linkedin` LinkedIn 资料打造
- **6 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等）：ATS 诊断、bullet 改写、多版本管理、模拟面试（STAR）、求职信（三段式）、LinkedIn 资料（headline/About/技能标签）
- **3 个专家 agent**：简历构建、简历审计、模拟面试官
- **2 个硬门 hooks**：上传简历拦截（隐私）、写简历文件提醒（均可一键豁免）
- **20 条确定性审计规则**：11 条简历 + 5 条求职信 + 4 条 LinkedIn（headline 超限/About 缺失/经历无量化/技能标签缺失），纯 Python、零第三方依赖，10 秒出结果

## 4 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-resume:resume` | 简历+JD 一条龙：ATS 诊断→bullet 改写→多版本→PDF 导出 | `/lhg-resume:resume`（然后粘贴简历和 JD） |
| `/lhg-resume:resume-interview` | 模拟面试：预测题→一次一题问答→STAR 评分→复盘 | `/lhg-resume:resume-interview --rounds 3` |
| `/lhg-resume:resume-audit` | 简历体检：16 条规则审计 + 人工复核清单 | `/lhg-resume:resume-audit --jd jd.txt` |
| `/lhg-resume:cover-letter` | 针对性求职信：JD 拆解→三段式写作→称呼/公司名/岗位名校验 | `/lhg-resume:cover-letter --resume resume.md`（然后粘贴 JD） |
| `/lhg-resume:linkedin` | LinkedIn 资料打造：headline 公式→About 故事线→经历改写→技能标签+背书策略 | `/lhg-resume:linkedin --resume resume.md`（+目标岗位） |

## 自查说明

自查 = 确定性脚本（机器）+ 人工复核清单（人）：

1. 先跑 `scripts/audit/resume_audit.py --target <简历文件> --jd <JD文件>`，零成本；
2. 发现分三级：**blocker**（联系方式缺失，必须修）、**warning**（无动词/无量化/关键词覆盖低，修或写豁免理由）、**nit**（bullet 过长、超 2 页）；
3. 再按 `lhg-rs-ats` 第 5 节过一遍脚本抓不到的（数字真实性、关键词自然度、错别字）。

blocker 清零才算"可投递"；**为清零编数字算作弊，绝不许**。

## 目录结构

```
lhg-resume/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 5 个命令：resume / resume-interview / resume-audit / cover-letter / linkedin
├── skills/                  # 6 个平台中立 skill（lhg-rs-ats/bullet/version/interview/cover-letter/linkedin）
├── agents/                  # 3 个专家 agent（resume-builder / resume-auditor / interview-coach）
├── hooks/                   # 2 个硬门（上传拦截 / 写简历提醒）+ 豁免说明
├── scripts/audit/           # 20 条确定性审计规则（11 简历 + 5 求职信 + 4 LinkedIn，零第三方依赖）
├── fixtures/                # 冒烟测试用例（bad.md / good.md / jd.txt + 求职信 bad/good/jd-cover-letter.txt + LinkedIn bad/good）
├── smoke_test.py            # 一键冒烟测试
├── ATTRIBUTION.md           # 灵感来源与许可声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你要投简历了，但不知道 ATS 那关怎么过 → 用 `/lhg-resume:resume`，先诊断再改
- 你的简历全是"负责""参与"，想改成"做成了什么" → `lhg-rs-bullet` 的动词库+量化公式就是干这个的
- 你海投 10 家，想每家都定制一版不断片 → `lhg-rs-version` 的版本库+CHANGELOG
- 你拿到面试了，想提前把坑踩完 → `/lhg-resume:resume-interview`，一次一题，真追问
- 你要投一家特别想去的公司，想附一封针对性求职信 → `/lhg-resume:cover-letter`，JD 拆解→三段式→三要素校验，一家公司一封
- 你的 LinkedIn 还是简历复印件，headline 写着"求职中" → `/lhg-resume:linkedin`，headline 公式→About 故事线→技能标签+背书，输出可直接粘贴的资料包

**什么时候不用：**

- 你想让 AI 帮你"编"一段漂亮的经历 → **本插件不干这个**，这是红线；没有证据的数字一律标 `[待确认]`
- 你要的是英文学术 CV（教授/博士后那种）→ 本插件按求职简历设计，学术 CV 格式差异大
- 你希望简历自动上传到招聘网站 → **不许**，隐私硬门会拦截；简历只做本地处理
- 你只想找个简历模板套一套 → 去套模板更快；本插件是"诊断+改写+面试"全链路，模板只是副产品

**隐私再强调一遍**：简历含手机号、邮箱等个人隐私。本插件所有处理都在本地完成，
hooks 会拦截 `curl -F` 上传、`scp` 传送等可疑命令。如需外发，请先脱敏或使用投递版 PDF 手动上传。

## lhg-plugs 插件矩阵

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-resume](https://github.com/lhg-plugs/lhg-resume) | 简历优化专家：ATS 诊断到模拟面试一条龙 + 针对性求职信 | `/plugin install lhg-resume@lhg-plugs` |
| *（后续插件在此追加，保持表格格式一致）* | | |

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、20 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-resume/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
