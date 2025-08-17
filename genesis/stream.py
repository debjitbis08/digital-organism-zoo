"""
Doom Feed: a lightweight event stream for human-friendly logs.

This module centralizes interesting events so they can be
printed now and later streamed to a UI.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Iterable
import threading


class DoomFeed:
    def __init__(self, max_items: int = 2000):
        self.max_items = max_items
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._seq = 0  # monotonically increasing event id

    def add(self, tag: str, message: str, importance: int = 1, meta: Optional[Dict[str, Any]] = None):
        with self._lock:
            self._seq += 1
            evt = {
                'id': self._seq,
                'ts': time.time(),
                'tag': tag,
                'message': message,
                'importance': importance,
                'meta': meta or {}
            }
            self.events.append(evt)
            if len(self.events) > self.max_items:
                self.events = self.events[-self.max_items:]
            self._cv.notify_all()
        # Immediate console echo for now (later replace with stream push)
        prefix = {
            3: '🌋',
            2: '🔥',
            1: '✨'
        }.get(importance, '✨')
        print(f"{prefix} {tag}: {message}")

    def get_recent(self, n: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.events[-n:])

    def export(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.events)

    def get_since(self, last_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Return events with id > last_id, up to limit.
        """
        with self._lock:
            if last_id <= 0:
                return list(self.events[-limit:])
            idx = 0
            for i, evt in enumerate(self.events):
                if evt.get('id', 0) > last_id:
                    idx = i
                    break
            return list(self.events[idx:idx + limit])

    def wait_for(self, last_id: int, timeout: float = 25.0, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Long-poll helper: waits up to timeout seconds for new events after last_id,
        then returns available events (possibly empty on timeout).
        """
        end_time = time.time() + timeout
        with self._lock:
            def _slice_since_locked() -> List[Dict[str, Any]]:
                if last_id <= 0:
                    return list(self.events[-limit:])
                idx = 0
                for i, evt in enumerate(self.events):
                    if evt.get('id', 0) > last_id:
                        idx = i
                        break
                return list(self.events[idx:idx + limit])

            if self._seq > last_id:
                return _slice_since_locked()
            remaining = end_time - time.time()
            while remaining > 0:
                self._cv.wait(timeout=remaining)
                if self._seq > last_id:
                    return _slice_since_locked()
                remaining = end_time - time.time()
            return []

    def stream(self, start_id: int = 0) -> Iterable[Dict[str, Any]]:
        """
        Infinite generator yielding events starting after start_id.
        """
        current = start_id
        while True:
            batch = self.wait_for(current, timeout=60.0)
            for evt in batch:
                current = evt.get('id', current)
                yield evt


# Singleton feed instance
doom_feed = DoomFeed()
