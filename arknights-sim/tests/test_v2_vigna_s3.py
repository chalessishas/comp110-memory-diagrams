"""Tests for Vigna S3 "Fierce Overdrive" — ATK +300%, crit_chance 50%, 25s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.vigna import make_vigna, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_TAG, _CRIT_S3


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


def test_s3_config():
    op = make_vigna(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 40
    assert op.skill.initial_sp == 15
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_vigna(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(base_atk * (1 + _S3_ATK_RATIO))


def test_s3_crit_chance_50pct_during_skill():
    w = _world()
    op = make_vigna(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    # Tick once so talent on_tick sets the crit_chance
    _ticks(w, 0.1)
    assert op.crit_chance == _CRIT_S3


def test_s3_crit_chance_restored_on_end():
    from data.characters.vigna import _CRIT_BASE
    w = _world()
    op = make_vigna(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.2)
    assert op.crit_chance == _CRIT_BASE


def test_s3_higher_crit_than_s2():
    from data.characters.vigna import _CRIT_SKILL
    assert _CRIT_S3 > _CRIT_SKILL


def test_s3_atk_buff_cleared_on_end():
    w = _world()
    op = make_vigna(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.1)
    assert op.effective_atk == base_atk
    assert not any(b.source_tag == _S3_ATK_TAG for b in op.buffs)


def test_s3_s2_regression():
    op = make_vigna(slot="S2")
    assert op.skill.slot == "S2"
    assert op.skill.sp_cost == 25
    assert op.skill.duration == 30.0
