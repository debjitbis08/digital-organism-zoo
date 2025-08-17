import types
import pytest

from genesis.self_modify import SelfModifyManager, safe_exec, SelfModifyError
from genesis.evolution import Organism, Capability


def test_param_tweak_and_log():
    class Obj:
        def __init__(self):
            self.alpha = 0.5

    o = Obj()
    sm = SelfModifyManager()
    ok = sm.try_adjust_param(o, 'alpha', 1.1, min_value=0.0, max_value=1.0)
    assert ok is True
    assert 0.5 < o.alpha <= 1.0
    assert len(sm.param_log) == 1


def test_safe_exec_allows_and_blocks():
    # Allowed simple math and print
    res = safe_exec('x = 1 + 2\nprint("hi")')
    assert res.get('x') == 3
    assert 'hi' in res.get('__stdout__', '')

    # Disallow imports due to missing __import__
    with pytest.raises(Exception):
        safe_exec('import os\ny=5')


def test_shadow_patch_accepts_and_rejects():
    sm = SelfModifyManager()

    # Safe: append a comment to data_processor
    patch = sm.prepare_patch('genesis.stream', lambda s: s + '\n# trial_patch\n')
    bv = sm.apply_patch_shadow(patch)
    assert hasattr(bv, 'version_id') and bv.version_id
    assert isinstance(bv.module, types.ModuleType)

    # Unsafe: attempt to inject an os import
    bad_patch = sm.prepare_patch('genesis.stream', lambda s: 'import os\n' + s)
    with pytest.raises(SelfModifyError):
        sm.apply_patch_shadow(bad_patch)


def test_apply_patch_rollback_smoketest():
    sm = SelfModifyManager()
    # Prepare a reversible change
    patch = sm.prepare_patch('genesis.stream', lambda s: s + '\n# will_rollback\n')
    # Force rollback via failing smoke test
    ok = sm.apply_patch(patch, smoke_test=lambda: False)
    assert ok is False
    # Ensure file content restored
    _, after = sm.snapshot_module_source('genesis.stream')
    assert after == patch.original


def test_organism_self_tune_and_introspect():
    o = Organism(generation=0)
    # Self-tune parameter when unlocked
    o.capabilities.add(Capability.MODIFY_PARAM)
    lr0 = o.traits.learning_rate
    ok = o.self_tune_parameters('learning_rate', factor=1.2, min_value=0.0, max_value=10.0)
    assert ok is True
    assert o.traits.learning_rate > lr0

    # Introspection attempts when unlocked
    o.capabilities.add(Capability.READ_SELF)
    before = o.introspection_attempts
    o._maybe_self_introspect()
    assert o.introspection_attempts == before + 1
