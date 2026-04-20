"""Blaze S2 'Carnage' — instant AOE physical burst to all in-range enemies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.blaze import make_blaze, _S2_ATK_MULTIPLIER, CENTURION_RANGE
from data.enemies import make_originium_slug


def _world(w=6, h=4) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 0), hp=500, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 10)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp
    e.hp = hp
    e.defence = defence
    e.atk_cd = 999.0
    e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: S2 config
# ---------------------------------------------------------------------------

def test_s2_config():
    blaze = make_blaze("S2")
    sk = blaze.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.duration == 0.0, "Carnage must be instant (duration=0)"
    assert sk.sp_cost == 25


# ---------------------------------------------------------------------------
# Test 2: Enemy in range takes damage when S2 fires
# ---------------------------------------------------------------------------

def test_s2_hits_enemy_in_range():
    """S2 deals damage to an enemy within Blaze's range."""
    w = _world()
    blaze = make_blaze("S2")
    blaze.deployed = True
    blaze.position = (0.0, 0.0)
    blaze.atk_cd = 999.0
    blaze.skill.sp = float(blaze.skill.sp_cost)
    w.add_unit(blaze)

    slug = _slug(pos=(1, 0), hp=9999)
    w.add_unit(slug)

    hp_before = slug.hp
    manual_trigger(w, blaze)

    assert slug.hp < hp_before, f"Enemy in range must take damage; hp={slug.hp}"


# ---------------------------------------------------------------------------
# Test 3: Enemy outside range takes no damage
# ---------------------------------------------------------------------------

def test_s2_misses_enemy_out_of_range():
    """S2 must not damage enemies outside Blaze's range_shape."""
    w = _world()
    blaze = make_blaze("S2")
    blaze.deployed = True
    blaze.position = (0.0, 0.0)
    blaze.atk_cd = 999.0
    blaze.skill.sp = float(blaze.skill.sp_cost)
    w.add_unit(blaze)

    # dx=3 is not in CENTURION_RANGE {(0,0),(1,0)}
    slug = _slug(pos=(3, 0), hp=9999)
    w.add_unit(slug)

    hp_before = slug.hp
    manual_trigger(w, blaze)

    assert slug.hp == hp_before, f"Enemy out of range must be unaffected; hp={slug.hp}"


# ---------------------------------------------------------------------------
# Test 4: Damage equals 190% ATK (base + 90% bonus), enemy def=0
# ---------------------------------------------------------------------------

def test_s2_damage_value():
    """Carnage deals int(blaze.effective_atk × 1.90) physical damage (def=0)."""
    w = _world()
    blaze = make_blaze("S2")
    blaze.deployed = True
    blaze.position = (0.0, 0.0)
    blaze.atk_cd = 999.0
    blaze.skill.sp = float(blaze.skill.sp_cost)
    w.add_unit(blaze)

    slug = _slug(pos=(1, 0), hp=99999, defence=0)
    w.add_unit(slug)

    hp_before = slug.hp
    manual_trigger(w, blaze)

    expected = int(blaze.effective_atk * _S2_ATK_MULTIPLIER)
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected, (
        f"Carnage damage must be {expected} (190% ATK); got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 5: Multiple enemies in range all take damage
# ---------------------------------------------------------------------------

def test_s2_hits_multiple_enemies():
    """Carnage hits all in-range enemies simultaneously."""
    w = _world()
    blaze = make_blaze("S2")
    blaze.deployed = True
    blaze.position = (0.0, 0.0)
    blaze.atk_cd = 999.0
    blaze.skill.sp = float(blaze.skill.sp_cost)
    w.add_unit(blaze)

    slug1 = _slug(pos=(0, 0), hp=9999)   # in range: (0,0)
    slug2 = _slug(pos=(1, 0), hp=9999)   # in range: (1,0)
    slug3 = _slug(pos=(3, 0), hp=9999)   # out of range
    w.add_unit(slug1)
    w.add_unit(slug2)
    w.add_unit(slug3)

    manual_trigger(w, blaze)

    assert slug1.hp < 9999, "Slug1 at (0,0) must take damage"
    assert slug2.hp < 9999, "Slug2 at (1,0) must take damage"
    assert slug3.hp == 9999, "Slug3 at (3,0) must be untouched"
