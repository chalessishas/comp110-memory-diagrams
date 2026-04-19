"""P9 — Deployment Point (DP) system tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.battle import Battle, TICK_RATE
from data.operators import make_liskarm, make_hoshiguma


def test_dp_accumulates_over_time():
    battle = Battle(operators=[], enemies=[], dp=0.0, dp_rate=1.0)
    for _ in range(TICK_RATE * 10):   # simulate 10 seconds
        battle._tick()
    assert abs(battle.dp - 10.0) < 0.01, "DP must accumulate at dp_rate per second"


def test_deploy_succeeds_when_dp_sufficient():
    op = make_liskarm()
    op.cost = 15
    battle = Battle(operators=[], enemies=[], dp=20.0)
    result = battle.deploy(op)
    assert result is True
    assert op in battle.operators
    assert abs(battle.dp - 5.0) < 0.01, "DP must be deducted on deploy"


def test_deploy_fails_when_dp_insufficient():
    op = make_hoshiguma()
    op.cost = 30
    battle = Battle(operators=[], enemies=[], dp=10.0)
    result = battle.deploy(op)
    assert result is False
    assert op not in battle.operators
    assert abs(battle.dp - 10.0) < 0.01, "DP must not change on failed deploy"


def test_dp_accumulates_then_deploy_succeeds():
    op = make_liskarm()
    op.cost = 8
    battle = Battle(operators=[], enemies=[], dp=0.0, dp_rate=1.0)
    # After 8 seconds (80 ticks) we should have enough DP
    for _ in range(TICK_RATE * 8):
        battle._tick()
    assert battle.dp >= 7.99   # float accumulation: 80 × 0.1 ≈ 8.0 − ε
    result = battle.deploy(op)
    assert result is True
    assert op in battle.operators
