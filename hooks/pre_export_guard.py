#!/usr/bin/env python3
"""lhg-resume 硬门①：拦截疑似把简历（含个人隐私）上传到外部的可疑命令。

触发：PreToolUse / Bash。只拦截"上传简历类文件"的命令模式，
普通命令 0 开销直接放行。

拦截模式（启发式，宁可误拦提醒、不漏放）：
  - curl 带 -F/--data/--upload-file 且命令含 resume/cv/简历/履历 字样
  - scp/rsync/ssh 传送 resume/cv/简历 命名的文件
  - gh release upload 上传简历类附件

逃生方式（按推荐度排序）：
  1. 不要上传简历到外部服务（推荐）。确实要传：先脱敏（删手机号/邮箱）。
  2. 紧急情况：LHG_RESUME_HOOKS_OFF=1 <原命令>（单次豁免本次 hook）。
  3. /plugin disable lhg-resume（整个插件停用，hooks 不再触发）。

设计原则：脚本内部出错 fail-open 直接放行，不因插件自身故障骚扰用户。
零第三方依赖。
"""

import json
import os
import re
import sys

RESUME_NAME_RE = re.compile(r"resume|cv|简历|履历", re.I)

# (描述, 正则)：命中任一即拦截
DENY_PATTERNS = [
    ("curl 上传文件",
     re.compile(r"\bcurl\b.*(-\bF\b|--form\b|--data(?:-binary)?\b|--upload-file\b|\b-T\b)", re.I)),
    ("scp 传送文件",
     re.compile(r"\bscp\b.*", re.I)),
    ("rsync 同步到远端",
     re.compile(r"\brsync\b.*[\w.@-]+:.*", re.I)),
    ("ssh 远端写入",
     re.compile(r"\bssh\b.*", re.I)),
    ("gh release 上传附件",
     re.compile(r"\bgh\b.*\brelease\b.*\bupload\b", re.I)),
]


def main() -> int:
    if os.environ.get("LHG_RESUME_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # fail-open

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command.strip():
        return 0

    # 非简历相关命令：快速放行
    if not RESUME_NAME_RE.search(command):
        # 纯上传动作但文件名不含简历字样也放行（避免误伤正常工作流）
        return 0

    hit = None
    for label, rx in DENY_PATTERNS:
        if rx.search(command):
            hit = label
            break
    if not hit:
        return 0

    reason = (
        "lhg-resume 隐私硬门拦截：检测到疑似上传简历的命令（%s）。\n"
        "简历含手机号、邮箱等个人隐私，按本插件隐私红线只做本地处理、不上传。\n"
        "确实需要外发：先脱敏（删除手机号/邮箱/身份证号），或改用投递版 PDF 手动上传。\n"
        "紧急豁免（单次）：LHG_RESUME_HOOKS_OFF=1 <原命令>"
    ) % hit
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
