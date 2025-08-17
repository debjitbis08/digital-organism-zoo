"""
Evolvable body parts (limbs) system.

Design goals
- Data-driven: parts loaded from a JSON registry when available.
- Evolvable: genomes encode which parts are present and their levels.
- Lightweight effects: parts bias foraging preferences and digestion metrics.

This keeps the integration optional and non-invasive: if the registry is
missing or parsing fails, organisms simply run without special limbs.
"""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------- Registry -------------------------------

DEFAULT_PARTS: Dict[str, Dict[str, Any]] = {
    # Sensors improve discovery and freshness thresholds
    "probe_antenna": {
        "slot": "sensor",
        "effects": {
            "foraging": {
                "freshness_bias": +0.05,       # raises min freshness a bit
                "structured_pref": +0.10,      # prefers structured when set
            },
            "digestion": {
                "K": +0.05,                    # slightly clearer activations
            },
        },
    },
    # Manipulators reduce operational costs and increase stability
    "manipulator_claw": {
        "slot": "manipulator",
        "effects": {
            "foraging": {
                "difficulty_bias": -0.05,      # prefers easier items slightly
            },
            "digestion": {
                "S": +0.08,                    # more stable processing
                "cpu_cost": -0.2,              # small CPU cost reduction
            },
        },
    },
    # Stability fins increase robustness of digestion
    "stabilizer_fins": {
        "slot": "stability",
        "effects": {
            "digestion": {
                "S": +0.12,
            },
        },
    },
    # Compression gland increases C (compressibility)
    "compressor_gland": {
        "slot": "processor",
        "effects": {
            "digestion": {
                "C": +0.10,
                "token_cost": -0.2,
            },
        },
    },
    # Recaller array increases recall overlap
    "recaller_array": {
        "slot": "memory",
        "effects": {
            "digestion": {
                "R": +0.10,
            },
        },
    },
    # Novelty scanner encourages exploring new types
    "novelty_scanner": {
        "slot": "explore",
        "effects": {
            "foraging": {
                "novelty_bias": +0.15,
            },
            "digestion": {
                "N": +0.05,
            },
        },
    },
}


def load_registry(path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Load registry from JSON file; fallback to DEFAULT_PARTS."""
    paths: List[str] = []
    if path:
        paths.append(path)
    # Conventional location relative to repo root
    paths.append(os.path.join(os.path.dirname(__file__), '..', 'body_parts_registry.json'))
    for p in paths:
        try:
            full = os.path.abspath(p)
            if os.path.exists(full):
                with open(full, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except Exception:
            continue
    return DEFAULT_PARTS


# ------------------------------- Genotype -------------------------------

@dataclass
class PartGene:
    """A reference to a part in the registry with a simple level scalar."""
    part_id: str
    level: int = 1


class BodyPartGenome:
    """Genome: a small set of part genes. Evolves by small edits."""

    def __init__(self, genes: Optional[List[PartGene]] = None, *, registry: Optional[Dict[str, Any]] = None):
        self.genes: List[PartGene] = genes or []
        self.registry = registry or load_registry()

    @staticmethod
    def random(max_parts: int = 3) -> "BodyPartGenome":
        reg = load_registry()
        keys = list(reg.keys())
        n = random.randint(1, min(max_parts, len(keys)))
        picks = random.sample(keys, n)
        genes = [PartGene(part_id=k, level=1) for k in picks]
        return BodyPartGenome(genes, registry=reg)

    def mutate(self, rate: float = 0.2, max_parts: int = 4) -> None:
        reg = self.registry
        keys = list(reg.keys())
        # Slightly change levels
        for g in list(self.genes):
            if random.random() < rate:
                g.level = max(1, min(5, g.level + random.choice([-1, 1])))
        # Occasionally add a new part
        if random.random() < rate and len(self.genes) < max_parts:
            candidates = [k for k in keys if k not in [g.part_id for g in self.genes]]
            if candidates:
                self.genes.append(PartGene(part_id=random.choice(candidates), level=1))
        # Occasionally remove a part
        if random.random() < rate and len(self.genes) > 1:
            self.genes.pop(random.randrange(len(self.genes)))

    def to_dict(self) -> Dict[str, Any]:
        return {"genes": [{"part_id": g.part_id, "level": g.level} for g in self.genes]}

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "BodyPartGenome":
        reg = load_registry()
        genes = [PartGene(part_id=g.get("part_id"), level=int(g.get("level", 1))) for g in obj.get("genes", [])]
        return BodyPartGenome(genes, registry=reg)


# ------------------------------- Phenotype -------------------------------

@dataclass
class BodyPart:
    part_id: str
    slot: str
    level: int
    effects: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def scaled(self, val: float) -> float:
        # Linear scaling with level and gentle attenuation
        return float(val) * (1.0 + 0.25 * (self.level - 1))

    def apply_foraging(self, prefs: Dict[str, Any]) -> None:
        f = self.effects.get("foraging") or {}
        if not f:
            return
        if "freshness_bias" in f:
            prefs["min_freshness"] = max(0.0, min(1.0, float(prefs.get("min_freshness", 0.0)) + self.scaled(f["freshness_bias"])) )
        if "difficulty_bias" in f:
            # Translate bias to preference label when strong
            bias = self.scaled(f["difficulty_bias"])
            if bias <= -0.1:
                prefs["difficulty_preference"] = "low"
            elif bias >= 0.1:
                prefs["difficulty_preference"] = "high"
        if "structured_pref" in f and f["structured_pref"] > 0:
            # Lightly bias toward structured types
            try:
                from data_sources.harvesters import DataType
                cur = list(prefs.get("preferred_types", []))
                bonus = [DataType.STRUCTURED_JSON, DataType.XML_DATA]
                # Merge while preserving order and avoiding duplicates
                for t in bonus:
                    if t not in cur:
                        cur.append(t)
                prefs["preferred_types"] = cur
            except Exception:
                pass
        if "novelty_bias" in f:
            prefs["novelty_bias"] = float(prefs.get("novelty_bias", 0.0)) + self.scaled(f["novelty_bias"])

    def digestion_mods(self) -> Dict[str, float]:
        d = self.effects.get("digestion") or {}
        out: Dict[str, float] = {}
        for k, v in d.items():
            out[k] = self.scaled(float(v))
        return out


class Body:
    def __init__(self, genome: BodyPartGenome):
        self.genome = genome
        self.registry = genome.registry
        self.parts: List[BodyPart] = []
        for g in genome.genes:
            spec = self.registry.get(g.part_id)
            if not spec:
                continue
            self.parts.append(
                BodyPart(
                    part_id=g.part_id,
                    slot=str(spec.get("slot", "other")),
                    level=g.level,
                    effects=dict(spec.get("effects") or {}),
                )
            )

    def mutate(self) -> None:
        self.genome.mutate()
        # Rebuild phenotype
        self.__init__(self.genome)

    def apply_foraging_preferences(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        for p in self.parts:
            p.apply_foraging(prefs)
        return prefs

    def aggregation_digestion_mods(self) -> Dict[str, float]:
        agg: Dict[str, float] = {}
        for p in self.parts:
            mods = p.digestion_mods()
            for k, v in mods.items():
                agg[k] = agg.get(k, 0.0) + v
        # Clip to safe ranges for metric-like keys
        for k in ("C", "R", "N", "K", "S"):
            if k in agg:
                agg[k] = max(-0.4, min(0.4, agg[k]))
        return agg

    # --------------------------- Actions API ---------------------------
    # Limbs expose callable actions; Body routes calls to installed parts.

    def call_action(self, action: str, *, organism, data_ecosystem=None, nutrition_system=None, preferences: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Dispatch an action to the appropriate body part implementation.

        Returns a result dict with at minimum {'ok': bool} and optional fields
        depending on the action.
        """
        # Normalize preferences through body
        prefs = self.apply_foraging_preferences(dict(preferences or {}))
        # Choose handler based on action; prefer the highest-level part supporting it
        candidates: List[BodyPart] = []
        for p in self.parts:
            if self._part_supports_action(p, action):
                candidates.append(p)
        if not candidates:
            return {"ok": False, "error": f"no_part_supports_action:{action}"}
        part = sorted(candidates, key=lambda x: x.level, reverse=True)[0]
        if action == 'probe_scan':
            return self._act_probe_scan(part, organism, data_ecosystem, prefs, **kwargs)
        if action == 'grasp_consume':
            return self._act_grasp_consume(part, organism, data_ecosystem, nutrition_system, prefs, **kwargs)
        if action == 'post_lead':
            return self._act_post_lead(part, organism, **kwargs)
        return {"ok": False, "error": f"unknown_action:{action}"}

    def _part_supports_action(self, part: BodyPart, action: str) -> bool:
        if action == 'probe_scan':
            return part.part_id in ('probe_antenna', 'novelty_scanner')
        if action == 'grasp_consume':
            return part.part_id in ('manipulator_claw',)
        if action == 'post_lead':
            return part.part_id in ('novelty_scanner', 'probe_antenna')
        return False

    def _act_probe_scan(self, part: BodyPart, organism, data_ecosystem, prefs: Dict[str, Any], limit: int = 3, **_):
        if data_ecosystem is None:
            return {"ok": False, "error": "no_ecosystem"}
        try:
            items = data_ecosystem.preview_food_for_organism(organism.capabilities, prefs, limit=max(1, int(limit)))
            # Return summaries only
            out = [{
                'id': getattr(m, 'unique_id', None),
                'type': m.data_type.value,
                'freshness': m.freshness,
                'source': m.source,
                'difficulty': m.difficulty,
            } for m in items]
            return {"ok": True, "items": out, "used": part.part_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _act_grasp_consume(self, part: BodyPart, organism, data_ecosystem, nutrition_system, prefs: Dict[str, Any], **_):
        if data_ecosystem is None or nutrition_system is None:
            return {"ok": False, "error": "missing_world_or_nutrition"}
        try:
            morsel = data_ecosystem.find_food_for_organism(organism.capabilities, prefs)
            if not morsel:
                return {"ok": False, "error": "no_food"}
            from genesis.nutrition import process_organism_feeding
            outcome = process_organism_feeding(organism, morsel, nutrition_system)
            return {"ok": True, "consumed": {
                'id': getattr(morsel, 'unique_id', None),
                'type': morsel.data_type.value,
                'source': morsel.source,
            }, "effects": outcome.get('effects', {}), "used": part.part_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _act_post_lead(self, part: BodyPart, organism, hint: Optional[str] = None, **_):
        try:
            # Choose hint from part bias if not provided
            if hint is None:
                hint = 'prefer_structured' if part.part_id in ('probe_antenna',) else 'prefer_code'
            from genesis.evolution import trade_board
            trade_board.post_lead(organism.id, None, source=part.part_id, score=1.0, hint=hint, region=getattr(organism, 'current_region', None))
            return {"ok": True, "hint": hint, "used": part.part_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}
