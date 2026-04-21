"""Chyue S3 "Colossus Strike" — ammo-based (4 charges), ATK+100%, MANUAL trigger.

Tests cover:
  - S3 configured correctly (slot, sp_cost=30, initial_sp=15, ammo=4, MANUAL)
  - ATK buff (+100%) active on S3 start
  - Ammo count is 4 on activation
  - ATK buff removed when skill ends
  - Stone Aegis talent regression (SP-threshold ATK buff)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.chyue import (
    make_chyue,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_AMMO,
    _TALENT_TAG, _TALENT_SP_THRESHOLD, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG,
)


def _world(w: int = 6, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(world: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        world.tick()


def _enemy(world: World, x: float, y: float, hp: int = 99999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    c = make_chyue(slot="S3")
    sk = c.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Colossus Strike"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.ammo_count == _S3_AMMO
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on S3 activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    world = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    world.add_unit(c)
    _enemy(world, x=1.0, y=1.0)

    base_atk = c.atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(world, c)

    buffs = [b for b in c.buffs if b.source_tag == _S3_BUFF_TAG and b.axis == BuffAxis.ATK]
    assert len(buffs) == 1, "S3 must apply exactly one ATK buff"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(c.effective_atk - expected_atk) <= 2, (
        f"Expected effective ATK ~{expected_atk}, got {c.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Ammo count is 4 on activation
# ---------------------------------------------------------------------------

def test_s3_ammo_count():
    c = make_chyue(slot="S3")
    sk = c.skill
    assert sk.ammo_count == _S3_AMMO, f"ammo_count must be {_S3_AMMO}, got {sk.ammo_count}"


# ---------------------------------------------------------------------------
# Test 4: ATK buff removed on skill end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_removed_on_end():
    world = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0)
    world.add_unit(c)
    # Enemy in range so attacks fire and consume ammo
    e = _enemy(world, x=1.0, y=1.0, hp=99999)
    e.defence = 0

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(world, c)
    assert any(b.source_tag == _S3_BUFF_TAG for b in c.buffs), "S3 buff must be active"

    # atk_interval=0.78s, 4 ammo → ~4s to exhaust all charges
    _ticks(world, 6.0)

    remaining = [b for b in c.buffs if b.source_tag == _S3_BUFF_TAG]
    assert len(remaining) == 0, "ATK buff must be removed when ammo is exhausted"


# ---------------------------------------------------------------------------
# Test 5: Stone Aegis talent regression — SP-threshold ATK buff
# ---------------------------------------------------------------------------

def test_talent_stone_aegis_activates_above_threshold():
    world = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    world.add_unit(c)

    # Force SP above threshold
    c.skill.sp = _TALENT_SP_THRESHOLD + 1.0

    # Tick once to let talent on_tick fire
    from core.systems.talent_registry import fire_on_tick
    fire_on_tick(world, c, dt=0.016)

    talent_buffs = [b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(talent_buffs) == 1, "Stone Aegis must activate when SP ≥ threshold"


def test_talent_stone_aegis_deactivates_below_threshold():
    world = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    world.add_unit(c)

    from core.state.unit_state import Buff
    from core.types import BuffAxis, BuffStack

    # Manually apply the buff (as if threshold was met)
    c.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                        value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG))

    # Drop SP below threshold
    c.skill.sp = _TALENT_SP_THRESHOLD - 1.0

    from core.systems.talent_registry import fire_on_tick
    fire_on_tick(world, c, dt=0.016)

    talent_buffs = [b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(talent_buffs) == 0, "Stone Aegis must deactivate when SP < threshold"
