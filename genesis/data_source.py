"""
Pluggable data source abstraction to interpret grid "stock" as internet data units.

Default implementation is deterministic and offline, producing small mock
data chunks with types like 'simple_text', 'structured_json', and 'xml_data'.

When real internet access is desired, a RequestsDataSource can be introduced
outside of tests to fetch live content and wrap it into DataChunk items.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import random


@dataclass
class DataChunk:
    """A tiny unit of consumable data.

    kind: a coarse type/category of the item (e.g., 'simple_text').
    content: the payload (kept small to avoid heavy memory use).
    """
    kind: str
    content: str


class DataSource:
    """Interface for providing data chunks to fill the grid.

    Implementations must be deterministic under a provided RNG for tests.
    """

    def provide(self, n: int, rng: Optional[random.Random] = None) -> List[DataChunk]:  # pragma: no cover - interface
        raise NotImplementedError


class OfflineSampleDataSource(DataSource):
    """Deterministic offline data source.

    Generates small synthetic items resembling internet data with fixed
    exemplars but RNG-chosen composition.
    """

    SIMPLE_TEXT = [
        "Hello, world!",
        "Breaking news: sample event.",
        "Tip: write tests first.",
        "Quote: simplicity scales.",
    ]
    STRUCTURED_JSON = [
        '{"type":"news","ok":true}',
        '{"sensor":1,"value":42}',
        '{"user":"alice","roles":["reader"]}',
    ]
    XML_DATA = [
        '<note><to>T</to><body>Hi</body></note>',
        '<data ok="1"/>',
    ]

    KINDS = (
        ("simple_text", SIMPLE_TEXT, 0.6),
        ("structured_json", STRUCTURED_JSON, 0.3),
        ("xml_data", XML_DATA, 0.1),
    )

    def provide(self, n: int, rng: Optional[random.Random] = None) -> List[DataChunk]:
        rng = rng or random.Random()
        out: List[DataChunk] = []
        # Precompute cumulative weights for kinds
        kinds = [k for k, _, _ in self.KINDS]
        pools = {k: v for k, v, _ in self.KINDS}
        weights = [w for _, _, w in self.KINDS]
        total_w = sum(weights)
        cum = []
        acc = 0.0
        for w in weights:
            acc += w
            cum.append(acc / total_w)
        for i in range(max(0, n)):
            r = rng.random()
            idx = 0
            while idx < len(cum) and r > cum[idx]:
                idx += 1
            idx = min(idx, len(kinds) - 1)
            kind = kinds[idx]
            pool = pools[kind]
            content = pool[rng.randrange(len(pool))]
            out.append(DataChunk(kind=kind, content=content))
        return out

