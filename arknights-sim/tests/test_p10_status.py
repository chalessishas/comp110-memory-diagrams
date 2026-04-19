"""P10 — Stun / Slow status effect tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.battle import Battle, DT, TICK_RATE
from core.status_effect import StatusEffect
from data.operators import make_liskarm
from data.enemies import make_originium_slug as make_slug


def test_stun_prevents_attack():
    enemy = make_slug()
    enemy.apply_status(StatusEffect(kind="stun", duration=2.0))

    fired = False
    for _ in range(TICK_RATE * 2):   # 2 seconds — within stun window
        if enemy.tick(DT):
            fired = True
            break
        enemy.tick_status(DT)

    assert not fired, "Stunned enemy must not fire any attacks"


def test_stun_expires_and_resumes_attacks():
    enemy = make_slug()
    enemy.apply_status(StatusEffect(kind="stun", duration=0.5))

    # Tick through stun (0.5s = 5 ticks)
    for _ in range(5):
        enemy.tick_status(DT)

    assert not enemy.is_stunned, "Stun must expire after duration"

    # After stun, attacks should resume
    fired = False
    for _ in range(TICK_RATE * 4):   # slug atk_interval ~3s
        enemy.tick_status(DT)
        if enemy.tick(DT):
            fired = True
            break

    assert fired, "Enemy must resume attacking after stun expires"


def test_slow_reduces_attack_frequency():
    op = make_liskarm()   # atk_interval=1.05s
    op_slow = make_liskarm()
    op_slow.apply_status(StatusEffect(kind="slow", duration=30.0, slow_factor=2.0))

    ticks = TICK_RATE * 10   # 10 seconds
    normal_attacks = sum(1 for _ in range(ticks) if op.tick(DT))
    slow_attacks   = sum(1 for _ in range(ticks) if op_slow.tick(DT))

    # With 2× slow, op_slow should fire roughly half as often
    assert slow_attacks < normal_attacks, "Slowed operator must attack less frequently"
    assert slow_attacks <= normal_attacks // 2 + 1, "Attack frequency should be ~halved"


def test_multiple_effects_stack():
    enemy = make_slug()
    enemy.apply_status(StatusEffect(kind="slow", duration=5.0, slow_factor=1.5))
    enemy.apply_status(StatusEffect(kind="stun", duration=1.0))

    assert enemy.is_stunned
    assert enemy.slow_factor == 1.5

    # After stun expires (1s), only slow remains
    for _ in range(TICK_RATE * 1):
        enemy.tick_status(DT)

    assert not enemy.is_stunned
    assert enemy.slow_factor == 1.5, "Slow must persist after stun expires"
