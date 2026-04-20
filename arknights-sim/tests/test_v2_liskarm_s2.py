"""Liskarm S2 Voltaic Shield — DEF+80% + periodic Arts pulse in radius."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.liskarm import (
    make_liskarm,
    _S2_TAG, _S2_DEF_RATIO, _S2_PULSE_RADIUS, _S2_PULSE_INTERVAL,
    _S2_SOURCE_TAG,
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


def _slug(pos=(2, 1), hp=999999, atk=0):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_liskarm_s2_config():
    lk = make_liskarm(slot="S2")
    sk = lk.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Voltaic Shield"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: DEF buff applied when S2 active
# ---------------------------------------------------------------------------

def test_s2_def_buff():
    """S2 must apply DEF +80% buff while active."""
    lk = make_liskarm(slot="S2")
    base_def = lk.effective_def
    lk.skill.sp = float(lk.skill.sp_cost)

    w = _world()
    lk.deployed = True; lk.position = (0.0, 1.0); lk.atk_cd = 999.0
    w.add_unit(lk)
    w.tick()  # skill fires

    assert lk.skill.active_remaining > 0, "S2 should be active after firing"
    expected_def = int(base_def * (1 + _S2_DEF_RATIO))
    assert lk.effective_def == expected_def, (
        f"S2 DEF buff: expected {expected_def}, got {lk.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: Pulse damages nearby enemy after 1s
# ---------------------------------------------------------------------------

def test_s2_pulse_damages_nearby():
    """After 1 second of S2, enemy within pulse radius takes Arts damage."""
    w = _world()
    lk = make_liskarm(slot="S2")
    lk.deployed = True; lk.position = (0.0, 1.0); lk.atk_cd = 999.0
    w.add_unit(lk)

    slug = _slug(pos=(1, 1), hp=999999)  # distance 1.0 ≤ pulse radius
    w.add_unit(slug)

    lk.skill.sp = float(lk.skill.sp_cost)
    hp_before = slug.hp

    # Advance slightly over 1 second to guarantee at least one pulse fires
    for _ in range(int(TICK_RATE) + 2):
        w.tick()

    assert slug.hp < hp_before, "Pulse must deal damage to nearby enemy after 1s"


# ---------------------------------------------------------------------------
# Test 4: Enemy outside pulse radius NOT hit
# ---------------------------------------------------------------------------

def test_s2_pulse_no_damage_outside_radius():
    """Enemy beyond _S2_PULSE_RADIUS must NOT be hit by pulse."""
    w = _world()
    lk = make_liskarm(slot="S2")
    lk.deployed = True; lk.position = (0.0, 1.0); lk.atk_cd = 999.0
    w.add_unit(lk)

    # distance = 3.0 > pulse_radius (1.5)
    slug_far = _slug(pos=(3, 1), hp=999999)
    w.add_unit(slug_far)

    lk.skill.sp = float(lk.skill.sp_cost)
    hp_before = slug_far.hp

    for _ in range(int(TICK_RATE)):
        w.tick()

    assert slug_far.hp == hp_before, "Enemy outside pulse radius must NOT be hit"


# ---------------------------------------------------------------------------
# Test 5: DEF buff removed on S2 end
# ---------------------------------------------------------------------------

def test_s2_def_buff_removed_on_end():
    """DEF buff must be cleaned up when S2 expires."""
    lk = make_liskarm(slot="S2")
    base_def = lk.effective_def
    lk.skill.sp = float(lk.skill.sp_cost)

    w = _world()
    lk.deployed = True; lk.position = (0.0, 1.0); lk.atk_cd = 999.0
    w.add_unit(lk)

    # Advance past S2 duration (20s)
    for _ in range(int(TICK_RATE * 22)):
        w.tick()

    assert lk.skill.active_remaining == 0.0, "S2 should have expired"
    assert not any(b.source_tag == _S2_SOURCE_TAG for b in lk.buffs), (
        "DEF buff must be removed after S2 ends"
    )
    assert lk.effective_def == base_def, (
        f"DEF must return to base {base_def} after S2; got {lk.effective_def}"
    )
