"""
Doom Feed: a lightweight event stream for human-friendly logs.

This module centralizes interesting events so they can be
printed now and later streamed to a UI.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class DoomFeed:
    def __init__(self, max_items: int = 2000):
        self.max_items = max_items
        self.events: List[Dict[str, Any]] = []

    def add(self, tag: str, message: str, importance: int = 1, meta: Optional[Dict[str, Any]] = None):
        evt = {
            'ts': time.time(),
            'tag': tag,
            'message': message,
            'importance': importance,
            'meta': meta or {}
        }
        self.events.append(evt)
        if len(self.events) > self.max_items:
            self.events = self.events[-self.max_items:]
        # Immediate console echo for now (later replace with stream push)
        prefix = {
            3: '🌋',
            2: '🔥',
            1: '✨'
        }.get(importance, '✨')
        print(f"{prefix} {tag}: {message}")

    def get_recent(self, n: int = 50) -> List[Dict[str, Any]]:
        return self.events[-n:]

    def export(self) -> List[Dict[str, Any]]:
        return list(self.events)


# Singleton feed instance
doom_feed = DoomFeed()

