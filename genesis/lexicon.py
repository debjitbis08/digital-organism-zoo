"""
Lightweight emergent lexicon with evolving phonotactics and a simple
"naming game" for alignment between organisms.

This module is intentionally dependency-light and self-contained so it can be
plugged into organisms without introducing strong coupling. It follows the
recipe outlined by the user: per-lineage alphabet, bigram phonotactics that
evolve with usage, word minting on demand, reinforcement and pruning, and a
peer naming game to converge on shared forms.
"""

from __future__ import annotations

from typing import Dict, Any, Iterable, Optional
import random


def _default_alphabet(rng: random.Random, k_range: tuple[int, int] = (12, 24)) -> list[str]:
    """Create a simple default alphabet: pick 12–24 symbols from a safe pool.

    We avoid exotic Unicode by default to keep logs and tests readable, but
    callers can provide any symbol list they like.
    """
    pool = list("abcdefghijklmnopqrstuvwxyz")
    rng.shuffle(pool)
    k = rng.randint(*k_range)
    return pool[:k]


class Lexicon:
    def __init__(
        self,
        rng: Optional[random.Random] = None,
        alphabet: Optional[Iterable[str]] = None,
    ) -> None:
        self.rng = rng or random.Random()
        self.alphabet = list(alphabet) if alphabet is not None else _default_alphabet(self.rng)
        # bigram counts P[next][prev] (using dict-of-dict for mutability and clarity)
        self.P: Dict[str, Dict[str, float]] = {a: {b: 1.0 for b in self.alphabet} for a in self.alphabet}
        # concept_id -> {"form": str, "w": float}
        self.words: Dict[Any, Dict[str, Any]] = {}

    # ---- generation helpers ----
    def _choose_next(self, prev: str) -> str:
        # If prev not in alphabet (e.g., adopting external word), fallback to uniform pick
        if prev not in self.P:
            return self.rng.choice(self.alphabet)
        probs = self.P[prev]
        total = sum(probs.values())
        r = self.rng.random() * total
        acc = 0.0
        for b, w in probs.items():
            acc += w
            if r <= acc:
                return b
        # Fallback (shouldn't happen): last key
        return next(iter(probs))

    def _mutate_form(self, form: str) -> str:
        """Apply a small mutation with low probability to induce drift.

        Mutations include: substitute, drop, duplicate, swap-adjacent.
        """
        if len(form) < 2:
            return form
        if self.rng.random() >= 0.2:
            return form
        op = self.rng.choice(["sub", "drop", "dup", "swap"])  # type: ignore[no-any-return]
        i = self.rng.randrange(len(form))
        if op == "sub":
            c = self.rng.choice(self.alphabet)
            return form[:i] + c + form[i + 1 :]
        if op == "drop" and len(form) > 2:
            return form[:i] + form[i + 1 :]
        if op == "dup":
            return form[: i + 1] + form[i] + form[i + 1 :]
        if op == "swap" and len(form) > 2:
            j = i + 1 if i + 1 < len(form) else i - 1
            a, b = form[min(i, j)], form[max(i, j)]
            return form[: min(i, j)] + b + a + form[max(i, j) + 1 :]
        return form

    def _sample_form(self, L: tuple[int, int] = (2, 6)) -> str:
        n = self.rng.randint(*L)
        s = [self.rng.choice(self.alphabet)]
        for _ in range(n - 1):
            s.append(self._choose_next(s[-1]))
        form = "".join(s)
        return self._mutate_form(form)

    # ---- public API ----
    def get_or_mint(self, concept_id: Any) -> str:
        if concept_id not in self.words:
            form = self._sample_form()
            self.words[concept_id] = {"form": form, "w": 1.0}
            self._reinforce_bigrams(form, +1.0)
        return self.words[concept_id]["form"]

    def reinforce(self, concept_id: Any, success: bool = True, k: float = 0.1) -> None:
        """Reinforce or decay the word weight for a concept.

        - success=True increases weight multiplicatively
        - success=False decays weight slightly
        - words below a threshold are pruned (and their bigrams decayed)
        """
        if concept_id not in self.words:
            return
        delta = k if success else -k / 2.0
        w0 = float(self.words[concept_id]["w"]) or 1.0
        w = max(0.05, w0 * (1.0 + delta))
        self.words[concept_id]["w"] = w
        if w < 0.07:
            # decay bigrams used before pruning
            self._reinforce_bigrams(self.words[concept_id]["form"], -0.5)
            del self.words[concept_id]

    # ---- phonotactics updates ----
    def _reinforce_bigrams(self, form: str, amount: float) -> None:
        # Only update known alphabet pairs to keep P bounded
        for a, b in zip(form, form[1:]):
            if a in self.P and b in self.P[a]:
                self.P[a][b] = max(0.25, self.P[a][b] + amount)


def naming_game(sender: Lexicon, receiver: Lexicon, concept_id: Any) -> None:
    """Play a single round of the naming game for a concept.

    - Sender transmits its form; receiver adopts if missing (with small mutation chance)
    - If receiver has a different form, pick a winner by relative weight
    - Both sides reinforce on success
    """
    w_s = sender.get_or_mint(concept_id)
    if concept_id not in receiver.words:
        # Chance to adopt a mutated sibling to preserve receiver dialect
        adopted = w_s
        if receiver.rng.random() < 0.2:
            adopted = receiver._sample_form()
        receiver.words[concept_id] = {"form": adopted, "w": 0.9}
        # Reinforce bigrams for the adopted form in receiver's phonotactics
        receiver._reinforce_bigrams(receiver.words[concept_id]["form"], +0.75)
    else:
        w_r = receiver.words[concept_id]["form"]
        if w_s != w_r:
            ws = float(sender.words[concept_id]["w"]) or 1.0
            wr = float(receiver.words[concept_id]["w"]) or 1.0
            p_sender = ws / (ws + wr)
            if sender.rng.random() < p_sender:
                receiver.words[concept_id]["form"] = w_s
                receiver.words[concept_id]["w"] *= 0.9
            else:
                sender.words[concept_id]["form"] = w_r
                sender.words[concept_id]["w"] *= 0.9
    # Successful exchange yields reinforcement on both sides
    sender.reinforce(concept_id, True)
    receiver.reinforce(concept_id, True)

