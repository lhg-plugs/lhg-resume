#!/usr/bin/env python3
"""lhg-resume 确定性简历审计：11 条规则，零第三方依赖。

扫描目标（单个 .md/.txt 简历文件或目录），输出 JSON 与人类可读报告；
有 blocker 时以 exit code 2 退出（供 hooks 与 CI 使用）。

用法：
    python3 resume_audit.py --target <简历文件或目录> [--jd <JD文件>] [--format json|text] [--fail-on blocker|warning|nit]

规则文案均为本项目原创（方法论思路受 ResumeSkills 等开源项目启发，
未复制任何第三方原文案与代码）。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-resume/resume-audit"

SCAN_EXTS = {".md", ".txt", ".text"}

PHONE_RE = re.compile(r"1[3-9]\d{9}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ID_RE = re.compile(r"\d{17}[\dXx]")
OVER_PII_RE = re.compile(r"身份证|家庭住址|现居.{0,6}(区|街道|路.{0,4}号|小区)")

# 强动词库（bullet 首词白名单，中英）
VERBS = [
    # 从0到1
    "主导", "创立", "搭建", "开拓", "孵化", "破冰",
    # 带团队
    "带领", "管理", "组建", "培养", "指导", "协调", "推动",
    # 增长
    "提升", "增长", "扩大", "翻倍", "拉新", "促活", "转化", "留存",
    # 降本增效
    "优化", "降低", "缩减", "节省", "重构", "提效",
    # 技术
    "设计", "开发", "上线", "攻克", "落地", "迁移", "保障",
    # 分析决策
    "分析", "拆解", "定位", "验证", "复盘", "制定",
    # 对外
    "谈判", "签约", "拓展", "维护", "获奖", "入选", "发表",
]
EN_VERBS = [
    "spearheaded", "led", "launched", "built", "drove", "increased",
    "reduced", "optimized", "automated", "negotiated", "delivered",
    "exceeded", "transformed", "designed", "developed", "founded",
]

BULLET_RE = re.compile(r"^\s*(?:[-*•·]\s+|\d{1,2}[.)、]\s*)(.+)$")
EXP_SECTION_RE = re.compile(r"工作经历|项目经历|实习经历|实践经历")
HEADER_RE = re.compile(r"^#{1,4}\s*(.+?)\s*$")

# 日期格式签名
DATE_SIGS = [
    ("slash", re.compile(r"\d{4}[./-]\d{1,2}")),
    ("cnym", re.compile(r"\d{4}年\d{1,2}月")),
    ("cny", re.compile(r"\d{4}年")),
    ("enm", re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}", re.I)),
]

SECTION_PATTERNS = {
    "教育": re.compile(r"教育背景|学历|毕业院校", re.I),
    "经历": re.compile(r"工作经历|项目经历|实习经历|实践经历", re.I),
    "技能": re.compile(r"专业技能|技能清单|技术栈|核心技能", re.I),
}

STOPWORDS = {
    "the", "and", "for", "with", "you", "our", "are", "will", "from",
    "that", "this", "have", "has", "was", "were", "been", "about",
}


class Finding:
    __slots__ = ("rule_id", "severity", "category", "title", "file", "line", "snippet", "detail")

    def __init__(self, rule_id, severity, category, title, file, line, snippet, detail):
        self.rule_id = rule_id
        self.severity = severity
        self.category = category
        self.title = title
        self.file = file
        self.line = line
        self.snippet = snippet
        self.detail = detail

    def to_dict(self):
        return {
            "rule_id": self.rule_id, "severity": self.severity,
            "category": self.category, "title": self.title,
            "file": self.file, "line": self.line,
            "snippet": self.snippet, "detail": self.detail,
        }


RULES = []
_RULE_BY_ID = {}


def rule(rule_id, severity, category, title, detail):
    def deco(fn):
        r = {"id": rule_id, "severity": severity,
             "category": category, "title": title, "detail": detail}
        _RULE_BY_ID[rule_id] = r
        r["check"] = fn
        RULES.append(r)
        return fn
    return deco


def _finding(rule_id, path, line, snippet):
    r = _RULE_BY_ID[rule_id]
    return Finding(r["id"], r["severity"], r["category"], r["title"],
                   path, line, snippet[:160], r["detail"])


def _bullets(lines, exp_only=True):
    """返回 [(行号, bullet正文)]。

    exp_only=True 时只取"经历类"章节（工作经历/项目经历/实习经历）下的 bullet，
    技能清单等处的条目不算 STAR bullet，避免误伤。
    """
    out = []
    in_exp = False
    for i, ln in enumerate(lines):
        hm = HEADER_RE.match(ln)
        if hm:
            in_exp = bool(EXP_SECTION_RE.search(hm.group(1)))
            continue
        if exp_only and not in_exp:
            continue
        m = BULLET_RE.match(ln)
        if m:
            out.append((i + 1, m.group(1).strip()))
    return out


def _starts_with_verb(text):
    t = text.strip()
    for v in VERBS:
        if t.startswith(v):
            return True
    m = re.match(r"[A-Za-z]+", t)
    if m and m.group(0).lower() in EN_VERBS:
        return True
    return False


def _has_number(text):
    return bool(re.search(r"\d|%|％|倍|Top\s*\d", text, re.I))


# ---------------- 联系方式与隐私 ----------------

@rule("RES-PII-001", "blocker", "联系方式", "联系方式缺失",
      "没找到手机号或邮箱。ATS/人工第一步就是找联系方式，缺了直接白投。补上手机号+邮箱。")
def r_pii_001(lines, text, path, ctx):
    if not PHONE_RE.search(text) or not EMAIL_RE.search(text):
        missing = []
        if not PHONE_RE.search(text):
            missing.append("手机号")
        if not EMAIL_RE.search(text):
            missing.append("邮箱")
        return [_finding("RES-PII-001", path, 1,
                         "缺失：%s" % "、".join(missing))]
    return []


@rule("RES-PII-002", "warning", "隐私", "含过度个人信息",
      "检测到身份证号/详细家庭住址。简历只写城市即可，过度个人信息有泄露风险，删掉。")
def r_pii_002(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        if ID_RE.search(ln) or OVER_PII_RE.search(ln):
            out.append(_finding("RES-PII-002", path, i + 1, ln.strip()))
    return out


# ---------------- 格式 ----------------

@rule("RES-FMT-001", "warning", "格式", "日期格式混用",
      "全篇检测到多种日期格式（如 2021.06 与 2021年6月混用）。统一成一种，推荐 2021.06–2023.08。")
def r_fmt_001(lines, text, path, ctx):
    seen = {name for name, rx in DATE_SIGS if rx.search(text)}
    # cny 一定是 cnym 的子串：有 cnym 时忽略 cny，避免误判混用
    if "cnym" in seen:
        seen.discard("cny")
    if len(seen) >= 2:
        return [_finding("RES-FMT-001", path, 1,
                         "检测到日期格式：%s" % "、".join(sorted(seen)))]
    return []


@rule("RES-SEC-001", "warning", "结构", "核心章节缺失",
      "缺教育/经历/技能三大件之一。ATS 靠标准章节标题切分内容，标题用标准词。")
def r_sec_001(lines, text, path, ctx):
    headers = " ".join(hm.group(1) for ln in lines
                       for hm in [HEADER_RE.match(ln)] if hm)
    missing = [k for k, rx in SECTION_PATTERNS.items() if not rx.search(headers)]
    if missing:
        return [_finding("RES-SEC-001", path, 1,
                         "缺失章节：%s（只认章节标题，正文提到不算）" % "、".join(missing))]
    return []


# ---------------- bullet 质量 ----------------

@rule("RES-BLT-001", "warning", "表达", "bullet 非强动词开头",
      "bullet 首词不在强动词库（如 主导/优化/提升/带领）。'负责/参与'开头显得像打杂，换强动词。")
def r_blt_001(lines, text, path, ctx):
    out = []
    for lineno, body in _bullets(lines):
        if body and not _starts_with_verb(body):
            out.append(_finding("RES-BLT-001", path, lineno, body))
    return out


@rule("RES-BLT-002", "warning", "表达", "bullet 缺乏量化",
      "bullet 里没数字。招聘者 6 秒扫一条：动词决定看不看，数字决定记不记得。补规模/变化/排名三类数字，编不出就标[待确认]。")
def r_blt_002(lines, text, path, ctx):
    out = []
    for lineno, body in _bullets(lines):
        if body and not _has_number(body) and "[待确认]" not in body:
            out.append(_finding("RES-BLT-002", path, lineno, body))
    return out


@rule("RES-BLT-003", "nit", "表达", "bullet 过长",
      "单条 bullet 超过 80 字。拆成两条或砍细节，一行能读完最好。")
def r_blt_003(lines, text, path, ctx):
    out = []
    for lineno, body in _bullets(lines):
        if len(body) > 80:
            out.append(_finding("RES-BLT-003", path, lineno,
                               body[:60] + "…（%d字）" % len(body)))
    return out


# ---------------- JD 匹配 ----------------

# 中文自动提取时的切分用虚词（启发式，JD 文件可写"关键词："行显式指定）
_CN_SPLIT_CHARS = "的了与和或在对将被人把由从到为以用及等并"


def _dedupe(seq):
    seen, out = set(), []
    for k in seq:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _jd_keywords(jd_text):
    # 优先用 JD 文件里的显式关键词行：关键词：a, b, c
    for ln in jd_text.split("\n"):
        m = re.match(r"\s*(?:关键词|Keywords)\s*[:：]\s*(.+?)\s*$", ln, re.I)
        if m:
            parts = [p.strip() for p in re.split(r"[，,、；;\s]+", m.group(1)) if p.strip()]
            return _dedupe(parts)
    # 回退：自动提取（启发式）
    kws = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9+#.]{2,}", jd_text):
        wl = w.lower().strip("#.")
        if wl not in STOPWORDS and len(wl) >= 3:
            kws.append(wl)
    for clause in re.split(r"[，。：；、\n（）()]", jd_text):
        c = re.sub(r"[A-Za-z0-9]", "", clause)
        for part in re.split("[" + _CN_SPLIT_CHARS + "]", c):
            p = part.strip()
            if 2 <= len(p) <= 6:
                kws.append(p)
    return _dedupe(kws)


@rule("RES-JD-001", "warning", "JD匹配", "JD 关键词覆盖率低",
      "JD 硬技能词在简历里命中不足 40%。把关键词自然嵌进经历 bullet，不要堆在技能栏凑数。")
def r_jd_001(lines, text, path, ctx):
    jd = ctx.get("jd_text", "")
    if not jd:
        return []
    kws = _jd_keywords(jd)
    if not kws:
        return []
    low_text = text.lower()
    hits = [k for k in kws if k.lower() in low_text]
    rate = len(hits) / len(kws)
    ctx["jd_coverage"] = (len(hits), len(kws), rate)
    if rate < 0.40:
        return [_finding("RES-JD-001", path, 1,
                         "覆盖率 %.0f%%（命中 %d/%d），缺失如：%s"
                         % (rate * 100, len(hits), len(kws),
                            "、".join([k for k in kws if k.lower() not in low_text][:6])))]
    return []


@rule("RES-JD-002", "warning", "JD匹配", "关键词疑似堆砌",
      "某 JD 关键词出现 ≥8 次。堆砌会被人工一眼识破，删到自然为止。")
def r_jd_002(lines, text, path, ctx):
    jd = ctx.get("jd_text", "")
    if not jd:
        return []
    out = []
    low_text = text.lower()
    for k in _jd_keywords(jd):
        c = low_text.count(k.lower())
        if c >= 8:
            out.append(_finding("RES-JD-002", path, 1,
                               "关键词「%s」出现 %d 次" % (k, c)))
    return out


# ---------------- 篇幅 ----------------

@rule("RES-LEN-001", "nit", "篇幅", "简历过长",
      "全文超 1500 字（约 2 页）。优先砍自我评价空话，再砍最久远的经历。")
def r_len_001(lines, text, path, ctx):
    n = len(re.sub(r"\s", "", text))
    if n > 1500:
        return [_finding("RES-LEN-001", path, 1, "全文约 %d 字" % n)]
    return []


# ---------------------------------------------------------------- 运行器

def collect_files(target):
    if os.path.isfile(target):
        return [target]
    out = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in SCAN_EXTS:
                out.append(os.path.join(root, f))
    return sorted(out)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def run(target, jd_text=""):
    files = collect_files(target)
    ctx = {"target": target, "jd_text": jd_text or ""}
    findings = []
    for path in files:
        text = read_text(path)
        lines = text.split("\n")
        rel = os.path.relpath(path, target) if os.path.isdir(target) else os.path.basename(path)
        for r in RULES:
            try:
                for f in r["check"](lines, text, path, ctx) or []:
                    f.file = rel
                    findings.append(f)
            except Exception:
                continue
    return files, findings, ctx


def main(argv=None):
    ap = argparse.ArgumentParser(description="lhg-resume 确定性简历审计")
    ap.add_argument("--target", default=".", help="简历文件或目录")
    ap.add_argument("--jd", default="", help="JD 文件（可选，给了才跑关键词规则）")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    ap.add_argument("--fail-on", choices=["blocker", "warning", "nit"], default="blocker")
    args = ap.parse_args(argv)

    target = os.path.abspath(args.target)
    if not (os.path.isfile(target) or os.path.isdir(target)):
        print("target 不存在：%s" % args.target, file=sys.stderr)
        return 1

    jd_text = read_text(os.path.abspath(args.jd)) if args.jd else ""

    files, findings, ctx = run(target, jd_text)

    sev_rank = {"blocker": 3, "warning": 2, "nit": 1}
    counts = {"blocker": 0, "warning": 0, "nit": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    result = {
        "tool": TOOL,
        "version": VERSION,
        "target": args.target,
        "summary": {
            "files_scanned": len(files),
            "rules_run": len(RULES),
            "blocker": counts["blocker"],
            "warning": counts["warning"],
            "nit": counts["nit"],
        },
        "findings": [f.to_dict() for f in sorted(
            findings, key=lambda x: (-sev_rank.get(x.severity, 0), x.file, x.line))],
    }
    cov = ctx.get("jd_coverage")
    if cov:
        result["summary"]["jd_coverage"] = {
            "hits": cov[0], "total": cov[1], "rate": round(cov[2], 3)}

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["summary"]
        print("简历审计：扫描 %d 文件，运行 %d 条规则" % (s["files_scanned"], s["rules_run"]))
        if cov:
            print("JD 关键词覆盖率：%.0f%%（%d/%d）" % (cov[2] * 100, cov[0], cov[1]))
        print("blocker=%d warning=%d nit=%d" % (s["blocker"], s["warning"], s["nit"]))
        for f in result["findings"]:
            print("[%s][%s] %s:%d %s" % (
                f["severity"].upper(), f["rule_id"], f["file"], f["line"], f["title"]))
            print("    %s" % f["detail"])
            if f["snippet"]:
                print("    → %s" % f["snippet"])

    level = sev_rank[args.fail_on]
    bad = any(sev_rank.get(f.severity, 0) >= level for f in findings)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
