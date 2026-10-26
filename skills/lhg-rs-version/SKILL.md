---
name: lhg-rs-version
description: 简历多版本管理：master 档案 + 按 JD 定制版本 + 命名规范 + 变更日志 + PDF 导出流程。一份简历海投的终结者。
license: MIT
compatibility: 适用于任何支持 Markdown 指令的 AI 助手（Claude Code、豆包、Workbuddy 等）
metadata:
  version: 1.0.0
  author: 刘洪光
---

# lhg-rs-version：简历多版本管理

> 目标：一份 master 档案（事实源头）+ N 个投递版本（按 JD 定制），
> 版本之间可追溯、可回滚、不串味。
> 核心纪律：**master 只增不改（事实），版本按需裁剪（表达）**；
> 任何版本里的数字都必须能在 master 里找到出处。

## 1. 何时使用

- `/lhg-resume:resume` 的 Phase 3 → 按本 skill 建版本库
- 拿到新 JD 要定制一版 → 走第 4 步
- 面试前要带"详细版" → 走第 5 步
- 想回滚到上一版 → 走第 6 步

## 2. 输入与输出

- **输入**：master 档案（或初版简历）、目标 JD（可选）
- **输出**：版本目录 `resume-versions/<版本名>/`（含简历 Markdown + CHANGELOG）
- **不输出**：覆盖掉 master 的"优化版"——master 永远保持事实完整

## 3. 目录结构

```
resume-workspace/
├── resume-source.md          # 用户给的原始稿（只读，不动）
├── resume-master.md          # master 档案：最全事实，可长可详细
├── resume-versions/
│   ├── bytedance-增长-20261011/
│   │   ├── resume.md         # 投递版（一页，PDF 导出用这个）
│   │   └── CHANGELOG.md      # 相对 master 改了什么、为什么
│   ├── tencent-策略-20261010/
│   │   ├── resume.md
│   │   └── CHANGELOG.md
│   └── interview-detail-20261011/
│       └── resume-detail.md  # 详细版（面试携带，可 2-3 页）
└── resume-audit-*.md         # 历次体检报告
```

### 命名规范
`<公司>-<岗位关键词>-<YYYYMMDD>`，如 `bytedance-增长-20261011`。
不要用 `v1/v2/final/final2`——三个月后你根本不知道 final3 投的是哪家。

### master 档案 vs 投递版本

| | master 档案 | 投递版本 |
|---|---|---|
| 作用 | 事实源头 | 针对某 JD 的表达 |
| 长度 | 不限，越全越好 | 1 页（应届可 1 页，资深最多 2 页） |
| bullet | 全量，带 [待确认] 标记 | 只留与 JD 相关的，[待确认] 必须清零或删除 |
| 更新 | 新增经历/数字只改这里 | 从不反向改 master |

## 4. 按 JD 定制一版（四步）

### 步骤 1：拆 JD
从 JD 提取三类信息，写进 CHANGELOG 开头：
- **硬门槛**（缺了直接被刷）：如"3 年以上增长经验""英语可做工作语言"
- **加分项**：如"有 0-1 经验""带过团队"
- **关键词**：技能词、业务词，抄 8-15 个

### 步骤 2：排序与裁剪
- 把 master 里与硬门槛/加分项相关的经历提到前面；无关经历压缩或删除。
- 每条 bullet 问一遍："这条能证明 JD 里某句话吗？"不能 → 删。
- 一页纸装不下时，优先砍"自我评价""兴趣爱好"，再砍最久远的经历。

### 步骤 3：关键词自然融入
- 按 lhg-rs-ats 3.1 的要求，把 JD 关键词嵌进 bullet，不要堆在技能栏。
- 改完跑审计脚本，RES-JD-001（覆盖率）通过、RES-JD-002（堆砌）不触发。

### 步骤 4：写 CHANGELOG
每个版本必须有 CHANGELOG，模板：

```markdown
# CHANGELOG：bytedance-增长-20261011
## 目标 JD 要点
- 硬门槛：3年增长经验、SQL、A/B测试
- 加分项：0-1、小程序
## 相对 master 的改动
- 提升"小程序拉新"经历到第一条（对标加分项）
- 删除"ERP 实施"经历（与 JD 无关，腾地方）
- 技能栏新增：A/B测试（master 里有，之前没写）
## 待确认
- 无（投递版不许留 [待确认]）
```

## 5. 详细版（面试携带）

- 从 master 生成，2-3 页，保留被投递版删掉的细节（项目背景、技术选型、踩坑）。
- 用途：面试官问"展开讲讲这个项目"时，你手里有提纲，不会漏关键数字。
- 详细版不投递、不外发，只自己看。

## 6. 回滚与追溯

- 每次改版前，把旧版整个目录复制一份加 `-bak-YYYYMMDD` 后缀（或走 git）。
- 面试被问"简历上写的 xxx"时，先查对应版本的 CHANGELOG，确认当时写了什么、
  数字是多少——**防止面试说的和投递版对不上**。
- 数字口径统一：同一数字在所有版本里必须一致，改一个版本要同步检查其他版本。

## 7. PDF 导出流程

1. 用投递版 `resume.md` 导出，不要用 master。
2. 导出方式（按推荐度）：
   - 本机 Word 打开 Markdown（粘贴）→ 调一版式 → 导出 PDF（版式最可控）
   - `pandoc resume.md -o resume.pdf --pdf-engine=xelatex`（需 TeX 环境，中文字体用 Noto Sans CJK）
   - 在线 Markdown 转 PDF（**注意**：涉及隐私，优先本地方式）
3. 导出后检查：文字可选（非图片）、1 页、无乱码、无"葬爱家族"式邮箱。
4. 文件名：`姓名-应聘岗位-年份.pdf`，如 `张三-用户增长-2026.pdf`。
   不要用 `resume.pdf`/`新建文档.pdf`——HR 的文件夹里有 500 个 resume.pdf。

### 导出前最终检查清单
- [ ] 用的是投递版 `resume.md`，不是 master
- [ ] 文字可选、无乱码、无错别字（公司名/人名零容忍）
- [ ] 1 页（资深最多 2 页），页边距正常
- [ ] 文件名是 `姓名-应聘岗位-年份.pdf`
- [ ] 审计脚本 blocker 清零，[待确认] 清零

## 8. 常见误区（反模式）

- ❌ 一份简历海投 50 家——每家的 JD 关键词都不一样，不过 ATS 是常态
- ❌ 改完版本不写 CHANGELOG——面试被问到时全靠猜
- ❌ master 和投递版数字对不上——面试 3 分钟穿帮
- ❌ 投递版留 [待确认]——投出去的就是承诺，HR 会当真的
- ❌ 简历文件名叫 `final-final-真的终版.pdf`
- ❌ 把简历上传到"免费 AI 简历优化"网站——**隐私红线**，你的手机号会出现在别人的数据库里

## 9. 自检与反馈

每次生成新版本：

1. CHANGELOG 是否写了（改了什么、针对哪个 JD）？→ 没写不算做完
2. 跑审计脚本：blocker 清零、RES-JD-001 通过、RES-JD-002 不触发
3. [待确认] 是否清零？→ 投递版里不许留
4. 数字口径：抽 3 个数字，和 master 对一遍 → 对不上就修
5. 文件名是否规范？→ `姓名-应聘岗位-年份.pdf`

反馈渠道：以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-resume/issues，
正文写清"场景 → 问题 → 期望"。版本管理有更好的命名/流程想法也欢迎提。

## 出品：刘洪光

本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
