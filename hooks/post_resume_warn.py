#!/usr/bin/env python3
"""lhg-resume 硬门②（警告级，不拦截）：写入疑似简历文件时提醒跑审计 + 勿外传。

触发：PostToolUse / Write|Edit。只做提醒，永远 exit 0、不拦截写入。

逃生方式：LHG_RESUME_HOOKS_OFF=1（环境变量）可关闭本提醒；
或 /plugin disable lhg-resume 停用整个插件。
零第三方依赖。
"""

import json
import os
import re
import sys

RESUME_FILE_RE = re.compile(r"resume|cv|简历|履历", re.I)
RESUME_DIR_RE = re.compile(r"resume-versions|resume-workspace|resume-master", re.I)
RESUME_EXTS = {".md", ".txt", ".tex", ".pdf", ".docx"}


def looks_like_resume(path: str) -> bool:
    p = path.replace("\\", "/")
    _, ext = os.path.splitext(p)
    if RESUME_DIR_RE.search(p):
        return True
    return bool(RESUME_FILE_RE.search(os.path.basename(p))) and ext.lower() in RESUME_EXTS


def main() -> int:
    if os.environ.get("LHG_RESUME_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path or not looks_like_resume(file_path):
        return 0

    msg = (
        "简历提醒（lhg-resume）：%s 疑似简历文件。\n"
        "1) 投递前先跑 /lhg-resume:resume-audit 体检，blocker 清零再投；\n"
        "2) 隐私红线：不要上传到外部网站/发给陌生 API，只做本地处理。\n"
        "关闭本提醒：export LHG_RESUME_HOOKS_OFF=1（当前会话有效）。"
    ) % file_path
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
