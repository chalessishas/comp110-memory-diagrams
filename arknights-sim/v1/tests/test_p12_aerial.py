"""P12 — Aerial enemy trait tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.battle import Battle, TICK_RATE, DT
from data.enemies import make_drone, make_originium_slug
from data.operators import make_hoshiguma, make_exusiai


_PATH = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]


def test_aerial_enemy_not_blocked_by_melee():
    tank = make_hoshiguma()   # melee, block=3
    drone = make_drone(path=_PATH)

    battle = Battle(operators=[tank], enemies=[drone])
    battle._compute_block_assignments()

    # Drone must not appear in any block assignment
    for blocked_list in battle._block_assignments.values():
        assert drone not in blocked_list, "Aerial enemy must not be blocked by melee op"


def test_aerial_enemy_advances_through_melee():
    tank = make_hoshiguma()
    drone = make_drone(path=_PATH)

    battle = Battle(operators=[tank], enemies=[drone], max_lives=3)
    result = battle.run(max_seconds=30.0)

    # Drone passes the melee tank unblocked → reaches goal → lives drain
    assert battle.lives < 3, "Aerial drone must bypass melee and drain lives"


def test_ranged_can_target_aerial():
    sniper = make_exusiai()   # ranged
    drone = make_drone(path=_PATH)

    battle = Battle(operators=[sniper], enemies=[drone])
    target = battle._blocked_enemy(sniper)

    assert target is drone, "Ranged operator must be able to target aerial enemy"


def test_ground_enemy_still_blocked_normally():
    tank = make_hoshiguma()
    slug = make_originium_slug(path=_PATH)

    battle = Battle(operators=[tank], enemies=[slug])
    battle._compute_block_assignments()

    blocked = battle._block_assignments.get(id(tank), [])
    assert slug in blocked, "Ground enemy must still be blocked by melee operator"
