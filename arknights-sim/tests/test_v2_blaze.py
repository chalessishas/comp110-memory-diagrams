"""Blaze — Centurion AoE (all-blocked attack) + Passion talent + S3."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.blaze import make_blaze, _PASSION_ATK_RATIO, _S3_ATK_RATIO
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(0, 1), hp=99999, atk=0):
    """Enemy at exact tile so Blaze blocks it."""
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_blaze_talent_registered():
    b = make_blaze()
    assert len(b.talents) == 1
    assert b.talents[0].name == "Passion"


# ---------------------------------------------------------------------------
# Test 2: Centurion attacks all blocked enemies simultaneously
# ---------------------------------------------------------------------------

def test_centurion_attacks_all_blocked():
    """Blaze with 2 enemies at her tile should deal damage to BOTH in one attack."""
    w = _world()
    b = make_blaze()
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 0.0
    w.add_unit(b)

    # Two enemies at Blaze's tile — both get blocked (block=3 capacity)
    slug1 = _slug((0, 1), hp=99999)
    slug2 = _slug((0, 1), hp=99999)
    w.add_unit(slug1)
    w.add_unit(slug2)

    hp1_before = slug1.hp
    hp2_before = slug2.hp

    for _ in range(5):
        w.tick()

    assert slug1.hp < hp1_before, "Centurion must damage first blocked enemy"
    assert slug2.hp < hp2_before, "Centurion must damage SECOND blocked enemy too"


# ---------------------------------------------------------------------------
# Test 3: Centurion single-target fallback when no blocked enemies
# ---------------------------------------------------------------------------

def test_centurion_falls_back_to_single_target():
    """When Blaze isn't blocking anyone, she targets the nearest enemy in range."""
    w = _world()
    b = make_blaze()
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 0.0
    w.add_unit(b)

    # Enemy in range but NOT at Blaze's tile → not blocked
    slug = _slug((1, 1), hp=99999)
    w.add_unit(slug)

    hp_before = slug.hp
    for _ in range(5):
        w.tick()

    assert slug.hp < hp_before, "Blaze must still attack in-range enemies when not blocking"


# ---------------------------------------------------------------------------
# Test 4: Passion talent ATK+15% when blocking
# ---------------------------------------------------------------------------

def test_passion_atk_when_blocking():
    """Passion: ATK +15% while blocking ≥1 enemy."""
    w = _world()
    b = make_blaze()
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    slug = _slug((0, 1))  # same tile — gets blocked
    w.add_unit(slug)

    atk_base = b.atk
    w.tick()

    expected = int(atk_base * (1.0 + _PASSION_ATK_RATIO))
    assert b.effective_atk == expected, (
        f"Passion must give ATK {expected} when blocking; got {b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: Passion suppressed when not blocking
# ---------------------------------------------------------------------------

def test_passion_suppressed_when_not_blocking():
    """Passion must NOT apply when Blaze has no blocked enemies."""
    w = _world()
    b = make_blaze()
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    # No enemies

    w.tick()

    assert b.effective_atk == b.atk, "Passion must not apply when not blocking"


# ---------------------------------------------------------------------------
# Test 6: S3 ATK buff activates
# ---------------------------------------------------------------------------

def test_blaze_s3_atk_buff():
    """S3 Blazing Sun: ATK +220% (Passion suppressed — slug at same tile)."""
    w = _world()
    b = make_blaze(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    slug = _slug((0, 1))  # blocking → suppresses Passion for clean S3 check
    w.add_unit(slug)

    atk_base = b.effective_atk
    b.skill.sp = b.skill.sp_cost
    w.tick()

    # After skill fires, Passion also activates (blocked). Account for both.
    expected = int(atk_base * (1.0 + _S3_ATK_RATIO + _PASSION_ATK_RATIO))
    assert b.effective_atk == expected, (
        f"S3 + Passion must give ATK {expected}; got {b.effective_atk}"
    )
