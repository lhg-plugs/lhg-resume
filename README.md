<!-- About 简介（推送后填写到仓库 About 栏）：
简历优化专家：粘贴简历+JD，ATS诊断→bullet量化改写→多版本管理→PDF导出→模拟面试→针对性求职信→LinkedIn资料打造，求职一条龙组合拳。 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-resume
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, resume, cv, ats, career, interview -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="lhg-resume — 简历优化专家">
</p>

> **一句话介绍**：简历优化专家：粘贴简历+JD，ATS诊断→bullet量化改写→多版本管理→PDF导出→模拟面试→针对性求职信→LinkedIn资料打造，求职一条龙组合拳。

**一键安装**：在 Claude Code 里运行

```bash
/plugin marketplace add lhg-plugs/lhg-resume
/plugin install lhg-resume@lhg-plugs
```

## 它能帮你做出什么

每条产出先过确定性脚本自查，再交人工复核清单——数字全部数自仓库里的审计脚本，不靠模型"自觉"。

| 自查脚本 | 规则数 | blocker | warning | nit | 覆盖 |
|---|---|---|---|---|---|
| `scripts/audit/resume_audit.py` | 19 | 5 | 12 | 2 | 联系方式、隐私、格式、结构、表达、JD匹配、篇幅、求职信 |
| **合计** | **19** | **5** | **12** | **2** | |

- **零 LLM 成本**：规则是纯 Python 脚本，零第三方依赖，本地运行。
- **坏 / 好对照可验**：`fixtures/` 里备有坏/好用例，冒烟测试断言命中情况。
- **冒烟全绿**：`python3 smoke_test.py` 70 项全部通过（JSON 合法、frontmatter 完整、命令/skill/agent 齐全）。

## 它是什么

`lhg-resume` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **5 个命令**（小白入口）：`cover-letter`求职信+JD 一条龙、`linkedin`LinkedIn 资料打造、`resume`简历+JD 一条龙、`resume-audit`简历体检、`resume-interview`基于你的简历模拟面试
- **6 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：lhg-cover-letter, lhg-linkedin, lhg-rs-ats, lhg-rs-bullet, lhg-rs-interview, lhg-rs-version
- **3 个专家 agent**：interview-coach, resume-auditor, resume-builder
- **2 个 hooks**（`hooks/`：post_resume_warn.py, pre_export_guard.py），关键操作前自动把关
- **19 条确定性自查规则**：纯 Python 脚本，见上表

## 为什么是它

不是一个 prompt，而是一套互相兜底的机制：

1. **确定性脚本（机器）+ 人工复核清单（人）**：先跑 `scripts/` 下的审计脚本（共 19 条规则），发现分三级：**blocker**（必须修）、**warning**（修或写豁免理由）、**nit**（顺手修）；再按对应 skill 的复核清单过一遍脚本抓不到的（内容真实性、越权、口径一致）。blocker 清零才算做完；为清零改规则算作弊，不许。
2. **硬门，不是提醒**：hooks 在关键操作前自动拦截或警告（见 `hooks/`），而不是只在文档里写一句"请注意"。
3. **方法论沉淀在 skill 里**：流程、检查清单、口径都写在 `skills/` 的方法论里，命令只是入口；换个 agent 平台也能复用同一套做法。
4. **可验，不是可信**：`fixtures/` 备有坏/好对照用例，`smoke_test.py` 一键验证，规则有没有生效、自己跑一遍就知道。

## 快速上手

```bash
# 1. 安装（Claude Code 里运行）
/plugin marketplace add lhg-plugs/lhg-resume
/plugin install lhg-resume@lhg-plugs

# 2. 求职信+JD 一条龙：JD 拆解→三段式求职信（钩子+匹配论证+行动收尾）→称呼
/lhg-resume:cover-letter --resume resume.md（然后粘贴 JD）
```

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-resume:cover-letter` | 求职信+JD 一条龙：JD 拆解→三段式求职信（钩子+匹配论证+行动收尾）→称呼/公司名/岗位名校验→一页纸交付… | `/lhg-resume:cover-letter --resume resume.md（然后粘贴 JD）` |
| `/lhg-resume:linkedin` | LinkedIn 资料打造：基于你的简历重写 headline（职业头衔公式）→About 故事线→经历 bullet … | `/lhg-resume:linkedin --resume resume.md（+目标岗位）` |
| `/lhg-resume:resume` | 简历+JD 一条龙：ATS诊断→bullet量化改写→多版本管理→PDF导出，全程本地处理。 | `/lhg-resume:resume（然后粘贴简历和 JD）` |
| `/lhg-resume:resume-audit` | 简历体检：跑确定性审计脚本（关键词/日期/联系方式/动词/量化），输出分级报告。 | `/lhg-resume:resume-audit --jd jd.txt` |
| `/lhg-resume:resume-interview` | 基于你的简历模拟面试：预测题→模拟问答→STAR评分→追问，给出可执行的改进清单。 | `/lhg-resume:resume-interview --rounds 3` |

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你需要求职信+JD 一条龙时 → 用 `/lhg-resume:cover-letter`
- 你需要LinkedIn 资料打造时 → 用 `/lhg-resume:linkedin`
- 你需要简历+JD 一条龙时 → 用 `/lhg-resume:resume`

**什么时候不用：**

- 你只需要其中一个零散能力时 → 本插件是成套流程，单点需求用更轻量的 skill 更合适
- 你希望 AI 完全自由发挥、不接受任何自查与硬门时 → 它的规则审计与 hooks 会介入（可关，但那就别装它）
- 🔒 隐私声明（先看这个）：你的简历只在本地处理，绝不上传到任何外部服务；
- 你的场景不在上面命令表覆盖范围内时 → 先看命令表，没有对应命令就别硬套

## 目录结构

```
lhg-resume/
├── smoke_test.py          # 一键冒烟测试
├── ATTRIBUTION.md         # 灵感来源与许可声明
├── LICENSE                # MIT
├── README.md              # 本文件
├── .claude-plugin/
├── agents/
├── assets/
├── commands/
├── fixtures/
├── hooks/
├── scripts/
├── skills/
```

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（本次实测 70 项全部通过）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-resume/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

同门插件见 [lhg-plugs](https://github.com/lhg-plugs)，86 个插件的完整矩阵在 [marketplace](https://github.com/lhg-plugs/marketplace) 维护。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
