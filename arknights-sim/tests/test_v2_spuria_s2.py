"""Spuria S2 Puppet Control — ATK+120% + substitute charge restoration."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.spuria import (
    make_spuria,
    _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_spuria_s2_config():
    s = make_spuria(slot="S2")
    sk = s.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Puppet Control"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied when S2 fires
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 must apply ATK+120% while active."""
    w = _world()
    s = make_spuria(slot="S2")
    base_atk = s.effective_atk
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert s.skill.active_remaining > 0, "S2 should be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert s.effective_atk == expected_atk, (
        f"S2 ATK: expected {expected_atk}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Substitute charge restored when spent
# ---------------------------------------------------------------------------

def test_s2_restores_substitute_charge():
    """S2 must restore undying_charges=1 when it fires with 0 charges."""
    w = _world()
    s = make_spuria(slot="S2")
    s.undying_charges = 0  # simulate substitute already spent
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert s.undying_charges == 1, (
        f"S2 must restore substitute charge; got undying_charges={s.undying_charges}"
    )


# ---------------------------------------------------------------------------
# Test 4: Substitute charge NOT doubled when already full
# ---------------------------------------------------------------------------

def test_s2_no_double_charge():
    """S2 must NOT add extra charge if substitute is still available."""
    w = _world()
    s = make_spuria(slot="S2")
    s.undying_charges = 1  # substitute still available
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert s.undying_charges == 1, (
        f"S2 must NOT over-add substitute; got undying_charges={s.undying_charges}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff removed on S2 end
# ---------------------------------------------------------------------------

def test_s2_buff_removed_on_end():
    """ATK buff must be stripped when S2 expires."""
    s = make_spuria(slot="S2")
    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)

    w = _world()
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in s.buffs), "Buff must be removed"
    assert s.effective_atk == base_atk, f"ATK must return to {base_atk}"
