"""Erato S2 Killshot — ammo-based ATK+200% (3 heavy rounds)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType
from core.systems import register_default_systems
from data.characters.erato import (
    make_erato,
    _S2_TAG, _S2_ATK_RATIO, _S2_AMMO, _S2_SOURCE_TAG,
)
from data.enemies import make_originium_slug


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 1), hp=999999):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_erato_s2_config():
    e = make_erato(slot="S2")
    sk = e.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Killshot"
    assert sk.sp_cost == 35
    assert sk.ammo_count == _S2_AMMO
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied when S2 fires
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 applies ATK+200% buff while ammo lasts."""
    w = _world()
    e = make_erato(slot="S2")
    base_atk = e.effective_atk
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    e.skill.sp = float(e.skill.sp_cost)
    w.tick()

    assert e.skill.active_remaining > 0 or e.skill.ammo_remaining > 0 or e.skill.ammo_count > 0
    # After skill fires, ATK buff should be present
    assert any(b.source_tag == _S2_SOURCE_TAG for b in e.buffs), "S2 ATK buff must be applied"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert e.effective_atk == expected_atk, (
        f"S2 ATK: expected {expected_atk}, got {e.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Each Killshot hit deals 3× base ATK physical damage
# ---------------------------------------------------------------------------

def test_s2_killshot_damage():
    """Each S2 shot deals ATK×3 physical damage (base ATK × (1 + _S2_ATK_RATIO))."""
    w = _world()
    e = make_erato(slot="S2")
    base_atk = e.effective_atk
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0  # suppress attack on fire tick
    w.add_unit(e)

    slug = _slug(pos=(1, 1), hp=999999)
    w.add_unit(slug)

    e.skill.sp = float(e.skill.sp_cost)
    w.tick()  # SKILL phase fires S2, applies buff; COMBAT phase suppressed (high atk_cd)
    assert any(b.source_tag == _S2_SOURCE_TAG for b in e.buffs), "S2 must be active"

    # Now let Erato attack with S2 buff active
    e.atk_cd = 0.0
    hp_before = slug.hp
    w.tick()  # Killshot fires with ATK+200%

    expected_single = int(base_atk * (1 + _S2_ATK_RATIO))
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_single, (
        f"Killshot single hit: expected {expected_single}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 4: S1 regression — S1 still works
# ---------------------------------------------------------------------------

def test_s1_regression():
    """S1 Strafing Fire must still work after S2 was added."""
    e = make_erato(slot="S1")
    assert e.skill is not None
    assert e.skill.slot == "S1"
    assert e.skill.name == "Strafing Fire"
