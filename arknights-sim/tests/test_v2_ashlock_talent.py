"""Ashlock talent "Bombardment Studies" — permanent ATK+8% ratio on deployment.

Tests cover:
  - Talent configured correctly (name + behavior_tag)
  - No ATK buff before deployment
  - ATK buff applied after add_unit (on_battle_start)
  - effective_atk increases by 8%
  - S2 end does not remove the Bombardment Studies ATK buff
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.ashlock import (
    make_ashlock, _TALENT_TAG, _TALENT_BUFF_TAG, _ATK_RATIO,
)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def test_ashlock_talent_configured():
    a = make_ashlock(slot="S2")
    assert len(a.talents) == 1
    assert a.talents[0].name == "Bombardment Studies"
    assert a.talents[0].behavior_tag == _TALENT_TAG


def test_no_buff_before_deployment():
    a = make_ashlock(slot="S2")
    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG not in buff_tags, (
        "Bombardment Studies ATK buff must NOT exist before add_unit"
    )


def test_bombardment_buff_after_deploy():
    w = _world()
    a = make_ashlock(slot=None)
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG in buff_tags, (
        "Bombardment Studies ATK buff must exist after add_unit"
    )


def test_bombardment_increases_effective_atk():
    base_atk = make_ashlock(slot=None).atk

    w = _world()
    a = make_ashlock(slot=None)
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    expected = int(base_atk * (1 + _ATK_RATIO))
    assert a.effective_atk == expected, (
        f"effective_atk must be {expected}; got {a.effective_atk}"
    )


def test_bombardment_survives_s2():
    w = _world()
    a = make_ashlock(slot="S2")
    a.deployed = True; a.position = (0.0, 1.0)
    a.skill.sp = float(a.skill.sp_cost)
    w.add_unit(a)

    _ticks(w, 26.0)   # let S2 run and expire

    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG in buff_tags, (
        "Bombardment Studies ATK buff must survive S2 end"
    )
