"""Append-only activity log, so a coach (you, later, or an agent) can review how problems were solved.

One JSON object per line in DATA_DIR/<course>.activity.jsonl:
    {"ts": "...", "sid": "<session>", "ev": "<event>", "pid": "0.1-03", ...fields}

Events: start, quit, open, lesson, run, submit, answer, hint, solution, reset, editor.
`run`/`submit` carry the code (only when it changed since the last snapshot of that problem) and
the result; `editor` carries a run-length-encoded stream of vim normal-mode commands.
Everything stays local; nothing is sent anywhere.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import datetime

from . import config


class Activity:
    def __init__(self, course_id: str):
        self.path = config.DATA_DIR / f"{course_id}.activity.jsonl"
        self.sid = uuid.uuid4().hex[:8]
        self._code_hash: dict[str, str] = {}
        self._opened: dict[str, float] = {}
        self._last_open: str | None = None

    def log(self, ev: str, pid: str | None = None, **fields) -> None:
        if os.environ.get("FORGE_NO_ACTIVITY"):
            return
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "sid": self.sid, "ev": ev}
        if pid:
            rec["pid"] = pid
        rec.update(fields)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass  # never let logging break the app

    def opened(self, pid: str) -> None:
        if self._last_open == pid:
            return
        self._last_open = pid
        self._opened[pid] = time.monotonic()
        self.log("open", pid)

    def seconds_on(self, pid: str) -> int | None:
        t = self._opened.get(pid)
        return round(time.monotonic() - t) if t is not None else None

    def code_if_changed(self, pid: str, files: dict[str, str]) -> dict[str, str] | None:
        h = hashlib.sha1(json.dumps(files, sort_keys=True).encode()).hexdigest()
        if self._code_hash.get(pid) == h:
            return None
        self._code_hash[pid] = h
        return files
