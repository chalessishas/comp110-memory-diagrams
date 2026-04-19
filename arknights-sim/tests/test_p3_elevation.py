"""P3 acceptance tests: elevation (ranged hits over melee) + block count limit."""
from __future__ import annotations
import pytest
from core.battle import Battle, SpawnEvent, DT
from core.operator import Operator
from core.enemy import Enemy
from data.operators import make_liskarm, make_hoshiguma, make_exusiai


def make_heavy_enemy(path=None) -> Enemy:
    """A durable enemy that Hoshiguma alone cannot kill in 30s.

    Hoshiguma DPS vs 0-DEF = 436/1.15 ≈ 379/s → needs >11,374 HP for 30s.
    With Exusiai added (DPS ≈ 1200/s), combined clears in ~10s.
    """
    return Enemy(
        name="Heavy Defender",
        max_hp=15000, atk=300, defence=0, res=0,
        atk_interval=2.0, attack_type="physical",
        path=path or [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2)],
        speed=0.5,
    )


def make_fast_slug(path=None) -> Enemy:
    """Light enemy that traverses path in 0.5s (speed=2.0)."""
    return Enemy(
        name="Fast Slug",
        max_hp=100, atk=10, defence=0, res=0,
        atk_interval=2.0, attack_type="physical",
        path=path or [(0, 0), (1, 0)],
        speed=2.0,
    )


# --- Ranged targeting tests --------------------------------------------------


def test_exusiai_hits_blocked_enemy():
    """Exusiai (ranged) and Hoshiguma (melee) should both attack the same enemy."""
    hoshiguma = make_hoshiguma()   # melee, block=3
    exusiai = make_exusiai()       # ranged, block=0

    heavy = make_heavy_enemy()
    battle = Battle(operators=[hoshiguma, exusiai], enemies=[heavy], max_lives=3)
    result = battle.run(max_seconds=60.0)

    assert result == "win", f"Expected win, got {result}\n{battle.log.dump()}"
    hoshi_hits = [e for e in battle.log.entries if "Hoshiguma →" in e]
    exusiai_hits = [e for e in battle.log.entries if "Exusiai →" in e]
    assert hoshi_hits, "Hoshiguma should have attacked the heavy enemy"
    assert exusiai_hits, "Exusiai should have attacked the heavy enemy"


def test_ranged_op_alone_kills_enemy():
    """Ranged operator without any melee op still attacks first live enemy."""
    exusiai = make_exusiai()
    slug = Enemy(
        name="Slug", max_hp=1300, atk=280, defence=0, res=0,
        atk_interval=1.5, attack_type="physical", path=[], speed=1.0,
    )
    battle = Battle(operators=[exusiai], enemies=[slug], max_lives=3)
    result = battle.run(max_seconds=30.0)

    assert result == "win", f"Expected win, got {result}\n{battle.log.dump()}"


def test_heavy_requires_combined_arms():
    """Heavy enemy survives if only Hoshiguma fights, dies with Exusiai added."""
    # Verify it's actually load-bearing: Hoshiguma alone loses to heavy in 60s
    hoshi_only = make_hoshiguma()
    heavy1 = make_heavy_enemy()
    battle_alone = Battle(operators=[hoshi_only], enemies=[heavy1], max_lives=3)
    result_alone = battle_alone.run(max_seconds=30.0)
    assert result_alone != "win", (
        "Hoshiguma alone should not win in 30s — test is not load-bearing"
    )

    # With Exusiai, win within 30s
    hoshi = make_hoshiguma()
    exu = make_exusiai()
    heavy2 = make_heavy_enemy()
    battle_combined = Battle(operators=[hoshi, exu], enemies=[heavy2], max_lives=3)
    result_combined = battle_combined.run(max_seconds=30.0)
    assert result_combined == "win", (
        f"Combined arms should win in 30s\n{battle_combined.log.dump()}"
    )


# --- Block count enforcement tests ------------------------------------------


def test_block_count_limit_overflow():
    """Op with block=1 can hold only 1 enemy; 2nd enemy must advance to goal."""
    path = [(0, 0), (1, 0), (2, 0)]  # 2 tiles, speed=0.1 → 20s to reach goal

    tank = Operator(
        name="Tank", max_hp=9999, atk=1, defence=9999, res=0,
        atk_interval=9999.0, block=1, attack_type="physical",
    )
    enemy1 = Enemy(
        name="E1", max_hp=9999, atk=1, defence=0, res=0,
        atk_interval=9999.0, attack_type="physical",
        path=list(path), speed=0.1,
    )
    enemy2 = Enemy(
        name="E2", max_hp=9999, atk=1, defence=0, res=0,
        atk_interval=9999.0, attack_type="physical",
        path=list(path), speed=0.1,
    )
    battle = Battle(
        operators=[tank], enemies=[enemy1, enemy2],
        max_lives=2,
    )
    result = battle.run(max_seconds=30.0)

    # E1 is blocked (never reaches goal), E2 is unblocked (reaches goal → lives=1)
    assert battle.lives == 1, (
        f"E2 should slip through (block=1 can't hold 2 enemies). Lives={battle.lives}\n"
        f"{battle.log.dump()}"
    )


def test_block_count_adequate():
    """Op with block=2 holds both enemies; neither reaches goal."""
    path = [(0, 0), (1, 0), (2, 0)]

    tank = Operator(
        name="Tank2", max_hp=9999, atk=1000, defence=0, res=0,
        atk_interval=0.5, block=2, attack_type="physical",
    )
    enemies = [
        Enemy(name=f"E{i}", max_hp=500, atk=1, defence=0, res=0,
              atk_interval=9999.0, attack_type="physical",
              path=list(path), speed=0.1)
        for i in range(2)
    ]
    battle = Battle(operators=[tank], enemies=enemies, max_lives=3)
    result = battle.run(max_seconds=30.0)

    assert result == "win", f"block=2 should hold 2 enemies\n{battle.log.dump()}"
    assert battle.lives == 3, "No lives should be lost"
