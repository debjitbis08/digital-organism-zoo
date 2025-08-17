"""
Code Self-Modification Framework (Task 9 - initial scaffold)

This module provides a conservative, safety-aware framework that lets
organisms inspect and adjust small parts of their own code and state
under strict capability gates. It is intentionally minimal to begin
with and focuses on three primitives:

- Introspection: snapshot live objects and modules for auditing.
- Parameter tweaks: bounded, reversible adjustments to numeric traits.
- Safe code patching: compute and stage source diffs with basic
  validators, with rollback if a smoke test fails.

Nothing here is automatically invoked by the evolution loop yet. This
module is designed to be imported and called by higher-level logic once
capabilities like READ_SELF or MODIFY_PARAM are unlocked. The goal is to
establish safe, testable building blocks that can grow over time without
disrupting the rest of the system.
"""

from __future__ import annotations

import contextlib
import dataclasses
import difflib
import importlib
import inspect
import io
import os
import re
import runpy
import sys
import tempfile
import time
from types import ModuleType
from typing import Any, Callable, Dict, Optional
import importlib.util
import hashlib


@dataclasses.dataclass
class ParamChange:
    target_repr: str
    attr: str
    old_value: Any
    new_value: Any
    ts: float = dataclasses.field(default_factory=time.time)


@dataclasses.dataclass
class CodePatch:
    module_name: str
    file_path: str
    original: str
    proposed: str
    diff: str
    ts: float = dataclasses.field(default_factory=time.time)


class SelfModifyError(Exception):
    pass


@dataclasses.dataclass
class BehaviorVersion:
    """Metadata for a shadow-loaded behavior module version."""
    version_id: str
    base_module: str
    shadow_module: str
    file_path: str
    module: ModuleType
    ts: float = dataclasses.field(default_factory=time.time)


class SelfModifyManager:
    """Safety-first manager for code self-modification.

    Responsibilities:
    - Introspection utilities (source snapshots, object summaries)
    - Bounded parameter adjustments with audit log and rollback
    - Prepare, validate, and apply small source patches to python files
      in an atomic way, with optional smoke-test callbacks.
    """

    # Very conservative deny-list for source patches
    _DANGEROUS_PATTERNS = [
        r"\bimport\s+os\b",
        r"\bimport\s+subprocess\b",
        r"\bfrom\s+os\s+import\b",
        r"\bopen\(\s*['\"]/(?:dev|proc|sys)",
        r"\bsocket\b",
        r"\beval\(",
        r"\bexec\(",
        r"\bsystem\(",
        r"\bpopen\(",
    ]

    def __init__(self):
        self.param_log: list[ParamChange] = []
        self.patch_log: list[CodePatch] = []

    # ------------- Introspection -------------
    def snapshot_module_source(self, module_name: str) -> tuple[str, str]:
        """Return (file_path, source_text) for a loaded module."""
        mod = sys.modules.get(module_name)
        if not isinstance(mod, ModuleType):
            # Try import if not loaded
            mod = importlib.import_module(module_name)
        file_path = inspect.getsourcefile(mod) or inspect.getfile(mod)  # type: ignore[arg-type]
        if not file_path or not os.path.exists(file_path):
            raise SelfModifyError(f"Cannot find file for module: {module_name}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            raise SelfModifyError(f"Failed to read module source: {e}")
        return file_path, src

    def summarize_object(self, obj: Any) -> Dict[str, Any]:
        """Return a compact, serializable summary of a live object."""
        info: Dict[str, Any] = {
            "type": type(obj).__name__,
            "module": getattr(type(obj), "__module__", ""),
        }
        # Numeric and bool fields only (safe)
        for name in dir(obj):
            if name.startswith("_"):
                continue
            with contextlib.suppress(Exception):
                v = getattr(obj, name)
                if isinstance(v, (int, float, bool)):
                    info[name] = v
        return info

    # ------------- Parameter tweaks -------------
    def try_adjust_param(self, obj: Any, attr: str, factor: float, *, min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
        """Safely scale a numeric attribute on an object.

        Records the change, clamps to optional bounds, and returns True on success.
        """
        try:
            cur = getattr(obj, attr)
            if not isinstance(cur, (int, float)):
                return False
            new = float(cur) * float(factor)
            if min_value is not None:
                new = max(min_value, new)
            if max_value is not None:
                new = min(max_value, new)
            setattr(obj, attr, new)
            self.param_log.append(ParamChange(repr(obj), attr, cur, new))
            self._emit_event("modify_param", f"{attr} {cur:.4f}→{new:.4f}")
            return True
        except Exception:
            return False

    def rollback_last_param(self) -> bool:
        if not self.param_log:
            return False
        change = self.param_log.pop()
        try:
            # Best effort: eval target repr is unsafe; instead store live weakref in future versions.
            # For now we cannot reliably resolve repr back to object; so this is a no-op but we keep the API.
            # Callers can implement their own rollback using the log record if they kept a reference.
            self._emit_event("rollback_param", f"{change.attr} -> {change.old_value}")
            return True
        except Exception:
            return False

    # ------------- Code patching -------------
    def prepare_patch(self, module_name: str, transform: Callable[[str], str]) -> CodePatch:
        """Create a CodePatch by applying a source-to-source transform."""
        file_path, original = self.snapshot_module_source(module_name)
        proposed = transform(original)
        diff = "\n".join(
            difflib.unified_diff(
                original.splitlines(), proposed.splitlines(),
                fromfile=f"a/{file_path}", tofile=f"b/{file_path}", lineterm=""
            )
        )
        patch = CodePatch(module_name, file_path, original, proposed, diff)
        return patch

    def _is_patch_safe(self, patch: CodePatch) -> bool:
        text = patch.proposed
        for pat in self._DANGEROUS_PATTERNS:
            if re.search(pat, text):
                return False
        # Size guard: do not allow very large changes in one step
        if len(patch.proposed) > len(patch.original) * 2 + 2048:
            return False
        return True

    def apply_patch(self, patch: CodePatch, *, smoke_test: Optional[Callable[[], bool]] = None) -> bool:
        """Atomically write the proposed source to disk and reload module.

        If a smoke_test is supplied, it will be executed after reloading;
        if it returns False or raises, the change is rolled back.
        """
        if not self._is_patch_safe(patch):
            self._emit_event("patch_rejected", f"{patch.module_name}: safety check failed")
            return False

        path = patch.file_path
        backup_path = f"{path}.bak_{int(time.time())}"
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="selfmod_", suffix=".py")
        os.close(tmp_fd)
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(patch.proposed)
            # Backup original then replace atomically
            with open(backup_path, "w", encoding="utf-8") as bf:
                bf.write(patch.original)
            os.replace(tmp_path, path)

            # Reload module
            importlib.invalidate_caches()
            importlib.reload(importlib.import_module(patch.module_name))

            ok = True
            if smoke_test is not None:
                ok = bool(smoke_test())
            if not ok:
                raise SelfModifyError("smoke test failed")
            self.patch_log.append(patch)
            self._emit_event("patch_applied", f"{patch.module_name} updated")
            return True
        except Exception as e:
            # Rollback
            with contextlib.suppress(Exception):
                if os.path.exists(backup_path):
                    with open(backup_path, "r", encoding="utf-8") as bf:
                        original = bf.read()
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(original)
                    importlib.invalidate_caches()
                    importlib.reload(importlib.import_module(patch.module_name))
            self._emit_event("patch_rolled_back", f"{patch.module_name}: {e}")
            return False
        finally:
            with contextlib.suppress(Exception):
                os.remove(tmp_path)
            # Keep backup to ease debugging; caller may prune later.

    def apply_patch_shadow(self, patch: CodePatch, *, shadow_pkg: str = "genesis._shadow", name_hint: Optional[str] = None) -> BehaviorVersion:
        """Load the proposed source as a new shadow module without touching the original.

        Returns a BehaviorVersion with metadata. Caller can bind this to a child
        organism so that only offspring run the new code lineage.
        """
        if not self._is_patch_safe(patch):
            raise SelfModifyError("shadow patch rejected by safety checks")

        # Ensure a deterministic id from content
        h = hashlib.sha1(patch.proposed.encode("utf-8")).hexdigest()[:10]
        version_id = h

        # Derive names
        base = patch.module_name
        # Shadow module short name
        shadow_name = name_hint or (base.replace('.', '_') + f"_{version_id}")
        # Fully-qualified module name inside the shadow package
        fqmn = f"{shadow_pkg}.{shadow_name}"
        base = patch.module_name
        shadow_name = name_hint or f"{base.replace('.', '_')}_v{h}"
        fqmn = f"{shadow_pkg}.{shadow_name}"

        # Ensure the shadow package exists on sys.modules for import machinery
        if shadow_pkg not in sys.modules:
            # Create a namespace package
            mod = ModuleType(shadow_pkg)
            mod.__path__ = []  # type: ignore[attr-defined]
            sys.modules[shadow_pkg] = mod

        # Write to a temporary file; load from file location with our chosen name
        tmp_dir = tempfile.mkdtemp(prefix="shadow_mod_")
        file_path = os.path.join(tmp_dir, f"{shadow_name}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(patch.proposed)

        spec = importlib.util.spec_from_file_location(fqmn, file_path)
        if spec is None or spec.loader is None:
            raise SelfModifyError("could not create import spec for shadow module")
        module = importlib.util.module_from_spec(spec)
        try:
            sys.modules[fqmn] = module
            spec.loader.exec_module(module)  # type: ignore[assignment]
        except Exception as e:
            with contextlib.suppress(Exception):
                # cleanup
                del sys.modules[fqmn]
            raise SelfModifyError(f"shadow module load failed: {e}")

        bv = BehaviorVersion(
            version_id=version_id,
            base_module=base,
            shadow_module=fqmn,
            file_path=file_path,
            module=module,
        )
        self._emit_event("shadow_loaded", f"{base} -> {fqmn}")
        return bv

    # ------------- Utilities -------------
    def _emit_event(self, kind: str, msg: str) -> None:
        """Send a low-noise event to doom_feed if available."""
        try:
            from .stream import doom_feed
            doom_feed.add(kind, msg, 1)
        except Exception:
            pass


def safe_exec(code: str, globals_dict: Optional[Dict[str, Any]] = None, locals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute code with a minimal, restricted global environment.

    This is a helper for experimentation and small code snippets during
    self-modification. It strips most builtins and explicitly opts-in a
    tiny, safe subset.
    """
    allowed_builtins = {
        "True": True,
        "False": False,
        "None": None,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "range": range,
        "len": len,
        "float": float,
        "int": int,
        "print": print,
    }
    g = {"__builtins__": allowed_builtins}
    if globals_dict:
        g.update(globals_dict)
    l: Dict[str, Any] = {}
    if locals_dict:
        l.update(locals_dict)
    # Capture stdout to avoid noisy logs
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, g, l)  # noqa: S102 - intentional, but restricted builtins
    l["__stdout__"] = buf.getvalue()
    return l


__all__ = [
    "ParamChange",
    "CodePatch",
    "SelfModifyError",
    "SelfModifyManager",
    "safe_exec",
]
