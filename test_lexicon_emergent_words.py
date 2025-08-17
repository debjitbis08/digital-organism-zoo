#!/usr/bin/env python3
"""
Tests for the emergent lexicon and naming game.
"""

import random


def test_word_minting_and_reuse():
    from genesis.lexicon import Lexicon

    rng = random.Random(42)
    alphabet = list("abcdefg")
    lex = Lexicon(rng=rng, alphabet=alphabet)

    w1 = lex.get_or_mint("c1")
    w2 = lex.get_or_mint("c1")
    assert w1 == w2
    assert 2 <= len(w1) <= 6
    # bigrams should be reinforced within alphabet
    for a, b in zip(w1, w1[1:]):
        if a in alphabet and b in alphabet:
            assert lex.P[a][b] > 1.0


def test_reinforcement_and_pruning():
    from genesis.lexicon import Lexicon

    lex = Lexicon(rng=random.Random(0), alphabet=list("abcde"))
    concept = "x"
    w = lex.get_or_mint(concept)
    w0 = lex.words[concept]["w"]
    lex.reinforce(concept, True)
    assert lex.words[concept]["w"] > w0
    # apply repeated decay to trigger pruning
    for _ in range(80):
        lex.reinforce(concept, False)
        if concept not in lex.words:
            break
    assert concept not in lex.words


def test_naming_game_alignment():
    from genesis.lexicon import Lexicon, naming_game

    rng1 = random.Random(123)
    rng2 = random.Random(456)
    # distinct alphabets are allowed; adoption stores raw strings
    s = Lexicon(rng1, alphabet=list("klmnopqrstuv"))
    r = Lexicon(rng2, alphabet=list("abcdefghij"))

    cid = ("cluster", 7)
    # play multiple rounds to allow convergence
    for _ in range(12):
        naming_game(s, r, cid)
    assert cid in s.words and cid in r.words
    assert s.words[cid]["form"] == r.words[cid]["form"]
    assert s.words[cid]["w"] > 1.0 and r.words[cid]["w"] > 0.8


def test_phonotactics_evolve_on_usage():
    from genesis.lexicon import Lexicon

    rng = random.Random(7)
    alphabet = list("xyzuvw")
    lex = Lexicon(rng=rng, alphabet=alphabet)
    cid = "c"
    w = lex.get_or_mint(cid)
    # reinforce multiple times to bump bigrams
    for _ in range(5):
        lex.reinforce(cid, True)
    # At least one bigram used by w should have grown above 1.0
    used_pairs = list(zip(w, w[1:]))
    assert any(lex.P[a][b] > 1.0 for a, b in used_pairs if a in alphabet and b in alphabet)
