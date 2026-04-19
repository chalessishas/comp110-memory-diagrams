"""P8 — Healer HP recovery tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.battle import Battle
from data.operators import make_warfarin, make_hoshiguma, make_liskarm


def _make_battle_no_enemies(*ops):
    return Battle(operators=list(ops), enemies=[], max_lives=3)


def test_healer_restores_injured_ally():
    warfarin = make_warfarin()
    tank = make_hoshiguma()
    tank.hp = tank.max_hp - 500   # injure tank by 500

    battle = _make_battle_no_enemies(warfarin, tank)
    initial_hp = tank.hp

    # Tick until warfarin fires at least once (atk_interval=2.85s → 29 ticks)
    for _ in range(30):
        battle._tick()

    assert tank.hp > initial_hp, "Healer must restore HP to injured ally"


def test_healer_targets_lowest_hp_ratio():
    warfarin = make_warfarin()
    tank1 = make_hoshiguma()   # max_hp=3200
    tank2 = make_liskarm()     # max_hp=2000

    # tank1 at 25% HP (800/3200), tank2 at 50% HP (1000/2000)
    # tank1 has lower ratio → should be targeted first
    tank1.hp = 800
    tank2.hp = 1000

    battle = _make_battle_no_enemies(warfarin, tank1, tank2)

    # Tick 30 times — one heal should fire targeting tank1
    tank1_before = tank1.hp
    tank2_before = tank2.hp
    for _ in range(30):
        battle._tick()

    assert tank1.hp > tank1_before, "Most-injured by ratio should be healed first"


def test_healer_idles_when_all_full_hp():
    warfarin = make_warfarin()
    tank = make_hoshiguma()
    # tank at full HP

    battle = _make_battle_no_enemies(warfarin, tank)
    for _ in range(30):
        battle._tick()

    assert tank.hp == tank.max_hp, "No overhealing — healer should idle when all full"
    heal_entries = [e for e in battle.log.entries if "heals" in e]
    assert len(heal_entries) == 0, "No heal log entries when all operators are at full HP"
