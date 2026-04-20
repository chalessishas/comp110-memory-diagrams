"""Thorns S2 Thorn Field — ATK+30% + AoE for 25s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.thorns import (
    make_thorns, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_thorns_s2_config():
    t = make_thorns(slot="S2")
    sk = t.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Thorn Field"
    assert sk.sp_cost == 35
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+30% buff."""
    w = _world()
    t = make_thorns(slot="S2")
    base_atk = t.effective_atk
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    w.add_unit(t)

    t.skill.sp = float(t.skill.sp_cost)
    w.tick()

    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert t.effective_atk == expected_atk, f"ATK: expected {expected_atk}, got {t.effective_atk}"


def test_s2_aoe_flag_set():
    """S2 sets _attack_all_in_range flag."""
    w = _world()
    t = make_thorns(slot="S2")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    w.add_unit(t)

    assert not getattr(t, "_attack_all_in_range", False)
    t.skill.sp = float(t.skill.sp_cost)
    w.tick()

    assert getattr(t, "_attack_all_in_range", False), "S2 must set _attack_all_in_range"


def test_s2_buffs_removed_on_end():
    """ATK buff and AoE flag cleared when S2 expires."""
    t = make_thorns(slot="S2")
    base_atk = t.effective_atk
    t.skill.sp = float(t.skill.sp_cost)

    w = _world()
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    w.add_unit(t)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in t.buffs)
    assert t.effective_atk == base_atk
    assert not getattr(t, "_attack_all_in_range", False)


def test_s3_regression():
    t = make_thorns(slot="S3")
    assert t.skill is not None and t.skill.slot == "S3"
    assert t.skill.name == "Annihilation"
