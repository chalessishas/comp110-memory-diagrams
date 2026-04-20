"""Surtr S2 Radiant Phoenix — ATK+70% for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.surtr import (
    make_surtr, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)
from data.enemies import make_originium_slug


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(0, 1), hp=999999):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    return e


def test_surtr_s2_config():
    s = make_surtr(slot="S2")
    sk = s.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Radiant Phoenix"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+70% buff while active."""
    w = _world()
    s = make_surtr(slot="S2")
    base_atk = s.effective_atk
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert s.skill.active_remaining > 0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert s.effective_atk == expected_atk, (
        f"S2 ATK: expected {expected_atk}, got {s.effective_atk}"
    )


def test_s2_buff_removed_on_end():
    """ATK buff must be stripped when S2 expires."""
    s = make_surtr(slot="S2")
    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)

    w = _world()
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in s.buffs), "Buff must be removed"
    assert s.effective_atk == base_atk


def test_s3_regression():
    s = make_surtr(slot="S3")
    assert s.skill is not None and s.skill.slot == "S3"
    assert s.skill.name == "Tyrant of the Undying Flames"
