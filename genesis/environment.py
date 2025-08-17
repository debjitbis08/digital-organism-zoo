"""
Simple-rule environmental substrate (Task 10)

This module implements a minimal grid world with resource patches and
very lightweight local rules. It is intentionally simple and self‑contained
so it can be used as a default substrate or embedded under the existing
organism system later.

Core ideas
- Grid of resource patches with logistic regrowth and light noise
- Simple organisms with energy, local memory, exploration vs exploitation
- Optional costly signaling that redirects nearby neighbors
- Metabolic costs including a memory-size penalty
- Reproduction with small mutations; death on energy depletion

The goal is to let selection pressure emerge from local rules (e.g.,
memory size trades off cost vs. benefit depending on stability), while
remaining deterministic under a provided RNG seed for tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math
import random

from .stream import doom_feed
from .data_source import DataChunk, DataSource, OfflineSampleDataSource


Coord = Tuple[int, int]


@dataclass
class PatchGrid:
    """2D grid of resource patches with logistic regrowth.

    Stock S(i,j) obeys: S <- S + r*S*(1 - S/K) + noise, then clipped to [0,K].
    """

    width: int
    height: int
    K: float = 10.0
    r: float = 0.2
    noise_std: float = 0.0
    rng: random.Random = field(default_factory=random.Random)
    # Optional data source: when set, stock increments are mapped to data chunks
    data_source: Optional[DataSource] = None

    def __post_init__(self):
        # Start half-full by default
        self.S: List[List[float]] = [
            [self.K * 0.5 for _ in range(self.width)] for _ in range(self.height)
        ]
        # Per-cell data buffers if a data source is attached
        self._buffers: Optional[List[List[List[DataChunk]]]] = None
        if self.data_source is not None:
            self._buffers = [[[] for _ in range(self.width)] for _ in range(self.height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> float:
        return self.S[y][x]

    def set(self, x: int, y: int, val: float) -> None:
        self.S[y][x] = max(0.0, min(self.K, val))

    def neighbors(self, x: int, y: int, R: int = 1) -> List[Coord]:
        coords: List[Coord] = []
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not self.in_bounds(nx, ny):
                    continue
                coords.append((nx, ny))
        return coords

    def step_regrow(self) -> None:
        """Legacy regrow using grid-global parameters.

        Note: SimpleEnvironment overrides this with region-aware regrowth.
        """
        for y in range(self.height):
            row = self.S[y]
            for x in range(self.width):
                S = row[x]
                growth = self.r * S * (1.0 - S / self.K)
                noise = self.rng.gauss(0.0, self.noise_std) if self.noise_std > 0 else 0.0
                S_next = S + growth + noise
                if S_next < 0.0:
                    S_next = 0.0
                if S_next > self.K:
                    S_next = self.K
                # Interpret positive delta as new data arrival if buffers active
                if self._buffers is not None and S_next > S:
                    self._refill_data(x, y, S_next - S)
                row[x] = S_next

    # -------------------- Optional data buffers --------------------
    def _refill_data(self, x: int, y: int, delta_units: float) -> None:
        if self._buffers is None or self.data_source is None:
            return
        n = int(max(0, math.floor(delta_units)))
        if n <= 0:
            return
        chunks = self.data_source.provide(n=n, rng=self.rng)
        self._buffers[y][x].extend(chunks)

    def consume_data(self, x: int, y: int, n: int) -> List[DataChunk]:
        if self._buffers is None or n <= 0:
            return []
        buf = self._buffers[y][x]
        if not buf:
            return []
        k = min(n, len(buf))
        taken = buf[-k:]
        del buf[-k:]
        return taken

    def buffer_type_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        if self._buffers is None:
            return counts
        for y in range(self.height):
            for x in range(self.width):
                for ch in self._buffers[y][x]:
                    counts[ch.kind] = counts.get(ch.kind, 0) + 1
        return counts


@dataclass
class SimpleOrganism:
    """A minimal organism following simple local rules."""

    id: int
    x: int
    y: int
    energy: float
    M: int = 3  # memory size (FIFO capacity)
    epsilon: float = 0.2  # exploration probability
    honesty: float = 0.8  # probability to signal when conditions are met

    # Internal memory of cell->last observed return (FIFO capped by M)
    memory: Dict[Coord, float] = field(default_factory=dict)
    memory_order: List[Coord] = field(default_factory=list)
    # Optional: count ingested data items by type when data source is active
    ingested_counts: Dict[str, int] = field(default_factory=dict)

    def remember(self, coord: Coord, value: float) -> None:
        if coord in self.memory:
            self.memory[coord] = value
            # Move to end (most recent)
            try:
                self.memory_order.remove(coord)
            except ValueError:
                pass
            self.memory_order.append(coord)
            return
        # New entry
        self.memory[coord] = value
        self.memory_order.append(coord)
        # Evict if over capacity
        while len(self.memory_order) > max(0, self.M):
            old = self.memory_order.pop(0)
            self.memory.pop(old, None)


class SimpleEnvironment:
    """Minimal environment substrate coordinating grid and organisms.

    This class is designed to be deterministic for tests when a seeded RNG
    is provided. It emits human-friendly events to the doom feed.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        K: float = 10.0,
        r: float = 0.2,
        noise_std: float = 0.0,
        bite: float = 1.0,
        sense_radius: int = 1,
        base_cost: float = 0.1,
        mem_cost: float = 0.02,
        signal_cost: float = 0.05,
        signal_threshold: float = 1.0,
        reproduce_threshold: float = 20.0,
        rng: Optional[random.Random] = None,
        data_source: Optional[DataSource] = None,
    ):
        self.rng = rng or random.Random()
        self.grid = PatchGrid(
            width,
            height,
            K=K,
            r=r,
            noise_std=noise_std,
            rng=self.rng,
            data_source=data_source,
        )
        self.bite = bite
        self.R = sense_radius
        self.base_cost = base_cost
        self.mem_cost = mem_cost
        self.signal_cost = signal_cost
        self.signal_threshold = signal_threshold
        self.reproduce_threshold = reproduce_threshold
        self.organisms: List[SimpleOrganism] = []
        # Active signals as list of (x,y). Very short-lived (consumed in same tick)
        self._signals: List[Coord] = []
        # Stats last tick
        self.last_redirected: int = 0
        self._next_id: int = 1
        # Regions: name -> (x0, y0, x1, y1) half-open rectangles
        self.regions: Dict[str, Tuple[int, int, int, int]] = {}
        # Region-specific parameters (overrides). name -> {K, r, noise_std}
        self.region_params: Dict[str, Dict[str, float]] = {}

    def add_organism(
        self,
        x: int,
        y: int,
        *,
        energy: float = 5.0,
        M: int = 3,
        epsilon: float = 0.2,
        honesty: float = 0.8,
    ) -> SimpleOrganism:
        org = SimpleOrganism(
            id=self._next_id,
            x=x,
            y=y,
            energy=energy,
            M=max(0, int(M)),
            epsilon=float(min(1.0, max(0.0, epsilon))),
            honesty=float(min(1.0, max(0.0, honesty))),
        )
        self._next_id += 1
        self.organisms.append(org)
        return org

    def _sense_best_neighbor(self, org: SimpleOrganism) -> Coord:
        # Use memory when exploiting, fallback to best current S in neighborhood
        candidates = [(org.x, org.y)] + self.grid.neighbors(org.x, org.y, self.R)
        # Prefer remembered returns; fallback current stock
        best_coord = candidates[0]
        best_val = -math.inf
        for c in candidates:
            remembered = org.memory.get(c)
            val = remembered if remembered is not None else self.grid.get(*c)
            if val > best_val:
                best_val = val
                best_coord = c
        return best_coord

    def _explore_neighbor(self, org: SimpleOrganism) -> Coord:
        candidates = [(org.x, org.y)] + self.grid.neighbors(org.x, org.y, self.R)
        return self.rng.choice(candidates)

    def _apply_signals_bias(self, org: SimpleOrganism, chosen: Coord) -> Tuple[Coord, bool]:
        # If there is a signal in the local neighborhood, bias towards it
        redirected = False
        if not self._signals:
            return chosen, redirected
        # Pick the closest recent signal
        def dist2(a: Coord, b: Coord) -> int:
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        here = (org.x, org.y)
        signal = min(self._signals, key=lambda s: dist2(s, here))
        # Redirect if signal is within 2*R neighborhood and not already chosen
        if dist2(signal, here) <= (2 * self.R) ** 2:
            # Step one move in direction of signal if possible
            dx = 0 if signal[0] == org.x else (1 if signal[0] > org.x else -1)
            dy = 0 if signal[1] == org.y else (1 if signal[1] > org.y else -1)
            target = (org.x + dx, org.y + dy)
            if self.grid.in_bounds(*target):
                if target != chosen:
                    redirected = True
                return target, redirected
        return chosen, redirected

    def _maybe_signal(self, org: SimpleOrganism, bite_gain: float) -> None:
        if bite_gain > self.signal_threshold and self.rng.random() < org.honesty:
            self._signals.append((org.x, org.y))
            org.energy -= self.signal_cost
            doom_feed.add(
                'signal',
                f"Organism {org.id} signaled abundance at ({org.x},{org.y}).",
                importance=1,
                meta={'org_id': org.id, 'x': org.x, 'y': org.y},
            )

    def step(self) -> None:
        # Regrow patches first (region-aware)
        self._regrow_region_aware()
        self.last_redirected = 0
        # Process organisms
        newborns: List[SimpleOrganism] = []
        self._signals = []  # reset signals each tick before any action
        depleted: List[Coord] = []

        for org in list(self.organisms):
            if org.energy <= 0:
                continue

            # Choose movement: explore vs exploit
            if self.rng.random() < org.epsilon:
                target = self._explore_neighbor(org)
            else:
                target = self._sense_best_neighbor(org)
            # Apply signaling bias (may redirect)
            target, redirected = self._apply_signals_bias(org, target)
            if redirected:
                self.last_redirected += 1

            # Move
            org.x, org.y = target

            # Eat
            stock = self.grid.get(org.x, org.y)
            bite_gain = min(self.bite, stock)
            if bite_gain > 0:
                new_stock = stock - bite_gain
                self.grid.set(org.x, org.y, new_stock)
                # If the grid tracks internet data, ingest corresponding items
                n_items = int(max(0, math.floor(bite_gain)))
                if n_items > 0:
                    items = self.grid.consume_data(org.x, org.y, n_items)
                    if items:
                        for it in items:
                            org.ingested_counts[it.kind] = org.ingested_counts.get(it.kind, 0) + 1
                if stock > 0 and new_stock <= 0:
                    # Track depleted patch for low-noise logging
                    depleted.append((org.x, org.y))
            org.energy += bite_gain

            # Remember observed return for this cell
            org.remember((org.x, org.y), bite_gain)

            # Optional costly signal
            self._maybe_signal(org, bite_gain)

            # Metabolism
            org.energy -= (self.base_cost + self.mem_cost * max(0, org.M))

            # Reproduce
            if org.energy >= self.reproduce_threshold:
                child = self._reproduce(org)
                newborns.append(child)

        # Remove the dead
        self.organisms = [o for o in self.organisms if o.energy > 0]
        # Add newborns at end of tick
        self.organisms.extend(newborns)

        # Emit a compact summary occasionally (low noise)
        if self.last_redirected > 0:
            doom_feed.add(
                'signals',
                f"{self.last_redirected} organisms redirected by signals this tick.",
                importance=1,
                meta={'redirected': self.last_redirected},
            )
        # Depletion notice (low-noise): aggregate unique coords
        if depleted:
            uniq = []
            seen = set()
            for c in depleted:
                if c not in seen:
                    seen.add(c)
                    uniq.append(c)
            desc = ", ".join(f"({x},{y})" for x, y in uniq[:3])
            extra = f" (+{len(uniq)-3} more)" if len(uniq) > 3 else ""
            doom_feed.add('deplete', f"Patch {desc} depleted; local crowd disperses.{extra}", 1,
                          {'count': len(uniq)})

    def _reproduce(self, org: SimpleOrganism) -> SimpleOrganism:
        # Split energy
        child_energy = org.energy * 0.5
        org.energy *= 0.5

        # Mutate M by ±1 with equal prob, clamp >=0
        delta_M = self.rng.choice([-1, 1]) if org.M > 0 else 1
        child_M = max(0, org.M + delta_M)

        # Small jitters for epsilon and honesty
        def jitter(v: float, scale: float = 0.05) -> float:
            return min(1.0, max(0.0, v + self.rng.uniform(-scale, scale)))

        child = SimpleOrganism(
            id=self._next_id,
            x=org.x,
            y=org.y,
            energy=child_energy,
            M=child_M,
            epsilon=jitter(org.epsilon),
            honesty=jitter(org.honesty),
        )
        self._next_id += 1

        msg = f"Organism {org.id} reproduced -> child {child.id}; M: {org.M} -> {child.M}."
        if child.M > org.M:
            msg += " Metabolism cost up."
        doom_feed.add(
            'reproduce',
            msg,
            importance=1,
            meta={'parent_id': org.id, 'child_id': child.id, 'M_parent': org.M, 'M_child': child.M},
        )
        return child

    # -------------------- Region support and modulation --------------------
    def set_regions(self, regions: Dict[str, Tuple[int, int, int, int]]) -> None:
        """Define named rectangular regions as half-open boxes [x0,x1), [y0,y1)."""
        self.regions = dict(regions)

    def region_of(self, x: int, y: int) -> Optional[str]:
        for name, (x0, y0, x1, y1) in self.regions.items():
            if x0 <= x < x1 and y0 <= y < y1:
                return name
        return None

    def set_region_params(self, name: str, *, K: Optional[float] = None, r: Optional[float] = None, noise_std: Optional[float] = None) -> None:
        cfg = self.region_params.get(name, {}).copy()
        if K is not None:
            cfg['K'] = float(K)
        if r is not None:
            cfg['r'] = float(r)
        if noise_std is not None:
            cfg['noise_std'] = float(noise_std)
        self.region_params[name] = cfg

    def get_region_params(self, x: int, y: int) -> Tuple[float, float, float]:
        """Return (K, r, noise_std) effective at (x,y)."""
        name = self.region_of(x, y)
        if not name:
            return (self.grid.K, self.grid.r, self.grid.noise_std)
        cfg = self.region_params.get(name, {})
        K = cfg.get('K', self.grid.K)
        r = cfg.get('r', self.grid.r)
        noise = cfg.get('noise_std', self.grid.noise_std)
        return (K, r, noise)

    def get_region_params_by_name(self, name: str) -> Dict[str, float]:
        base = {'K': self.grid.K, 'r': self.grid.r, 'noise_std': self.grid.noise_std}
        base.update(self.region_params.get(name, {}))
        return base

    def apply_teacher_modulation(self, modulation: Dict[str, Dict[str, float]]) -> None:
        """Update region parameters based on teacher-provided modulation.

        Example modulation dict: {'north': {'r': 0.25}, 'south': {'K': 20.0, 'noise_std': 0.1}}
        """
        changed = []
        for region, params in modulation.items():
            self.set_region_params(region, K=params.get('K'), r=params.get('r'), noise_std=params.get('noise_std'))
            changed.append((region, self.region_params.get(region, {})))
        if changed:
            try:
                desc = ", ".join(f"{n}:{p}" for n, p in changed[:3])
                if len(changed) > 3:
                    desc += f" (+{len(changed)-3} more)"
                doom_feed.add('env_mod', f"Teacher modulation applied: {desc}", 1)
            except Exception:
                pass

    def _regrow_region_aware(self) -> None:
        S = self.grid.S
        rng = self.grid.rng
        for y in range(self.grid.height):
            row = S[y]
            for x in range(self.grid.width):
                K, r, noise_std = self.get_region_params(x, y)
                s = row[x]
                growth = r * s * (1.0 - s / K) if K > 0 else 0.0
                noise = rng.gauss(0.0, noise_std) if noise_std > 0 else 0.0
                s_next = s + growth + noise
                if s_next < 0.0:
                    s_next = 0.0
                if s_next > K:
                    s_next = K
                if hasattr(self.grid, '_refill_data') and s_next > s:
                    # Map positive delta to new data chunks for this cell
                    try:
                        self.grid._refill_data(x, y, s_next - s)
                    except Exception:
                        # Avoid breaking regrowth if data source misbehaves
                        pass
                row[x] = s_next

    # -------------------- Coarse teacher feedback --------------------
    def apply_coarse_feedback(self, energy_bonus: Dict[int, float]) -> None:
        """Apply tiny energy bonuses to organisms as coarse evaluative feedback.

        The teacher can call this to reward optional micro-tasks without
        prescribing behavior. Keys are organism IDs (SimpleOrganism.id),
        values are small energy deltas to add (can be negative for penalties).
        Emits a compact doom_feed event describing the bonuses applied.
        """
        if not energy_bonus:
            return
        applied = []
        for org in self.organisms:
            delta = energy_bonus.get(org.id)
            if not delta:
                continue
            org.energy += float(delta)
            applied.append((org.id, float(delta)))
        if applied:
            try:
                sample = ", ".join(f"{oid}:{d:+.2f}" for oid, d in applied[:3])
                more = f" (+{len(applied)-3} more)" if len(applied) > 3 else ""
                doom_feed.add('feedback', f"Coarse feedback: {sample}{more}", 1)
            except Exception:
                pass


class SimpleEnvAdapter:
    """Adapter to expose SimpleEnvironment via a DataEcosystem-like API.

    This enables reuse of some organism foraging logic that expects a
    get_ecosystem_stats() call. It is intentionally minimal.
    """

    def __init__(self, env: SimpleEnvironment):
        self.env = env

    def get_ecosystem_stats(self) -> Dict[str, float]:
        # Aggregate total stock and normalize to [0,1] by carrying capacity
        total = 0.0
        K_total = 0.0
        for y in range(self.env.grid.height):
            for x in range(self.env.grid.width):
                s = self.env.grid.get(x, y)
                K, _, _ = self.env.get_region_params(x, y)
                total += s
                K_total += K
        avg_freshness = (total / K_total) if K_total > 0 else 0.0
        # food_scarcity here represents abundance fraction in [0,1]
        # Aggregate available data by type if the grid tracks data buffers
        food_by_type = {
            'simple_text': 0,
            'structured_json': 0,
            'xml_data': 0,
            'code': 0,
        }
        try:
            buf_counts = self.env.grid.buffer_type_counts()  # type: ignore[attr-defined]
            for k in list(food_by_type.keys()):
                food_by_type[k] = int(buf_counts.get(k, 0))
        except Exception:
            pass

        stats = {
            'total_food_available': total,
            'average_freshness': avg_freshness,
            'food_scarcity': avg_freshness,
            'food_by_type': food_by_type,
        }
        return stats


__all__ = [
    'PatchGrid',
    'SimpleOrganism',
    'SimpleEnvironment',
]
