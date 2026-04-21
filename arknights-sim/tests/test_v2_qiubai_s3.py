"""Qiubai S3 "Soulwind" — ATK+150%, block→3, 30s AUTO.

Tests cover:
  - S3 configured correctly (slot, sp_cost=50, initial_sp=25, AUTO, requires_target=False)
  - ATK buff (+150%) active during skill
  - Block increased to 3 on S3 start
  - ATK buff removed on skill end
  - Block reverts to 2 on skill end
  - Feathered Gale talent regression (3rd-hit True burst)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, BuffAxis
from core.systems import register_default_systems
from data.characters.qiubai import (
    make_qiubai,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_BLOCK, _S3_DURATION,
    _SEAL_TAG,
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
    q = make_qiubai(slot="S3")
    sk = q.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Soulwind"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 25
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    world = _world()
    q = make_qiubai(slot="S3")
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    world.add_unit(q)
    _enemy(world, x=1.0, y=1.0)

    base_atk = q.atk
    q.skill.sp = float(q.skill.sp_cost)
    _ticks(world, 0.1)  # triggers skill

    assert q.skill.active_remaining > 0.0, "S3 must be active"
    atk_buffs = [b for b in q.buffs if b.source_tag == _S3_BUFF_TAG and b.axis == BuffAxis.ATK]
    assert len(atk_buffs) == 1, "Must have exactly one S3 ATK buff"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(q.effective_atk - expected_atk) <= 2, (
        f"Expected effective ATK ~{expected_atk}, got {q.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Block increases to 3 on S3 start
# ---------------------------------------------------------------------------

def test_s3_block_increases():
    world = _world()
    q = make_qiubai(slot="S3")
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    world.add_unit(q)
    _enemy(world, x=1.0, y=1.0)

    assert q.block == 2, "Default block must be 2 before S3"

    q.skill.sp = float(q.skill.sp_cost)
    _ticks(world, 0.1)

    assert q.block == _S3_BLOCK, f"Block must be {_S3_BLOCK} during S3, got {q.block}"


# ---------------------------------------------------------------------------
# Test 4: ATK buff removed on skill end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_removed_on_end():
    world = _world()
    q = make_qiubai(slot="S3")
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    world.add_unit(q)
    _enemy(world, x=1.0, y=1.0)

    q.skill.sp = float(q.skill.sp_cost)
    _ticks(world, 0.1)  # activate
    assert q.skill.active_remaining > 0.0

    _ticks(world, _S3_DURATION + 0.5)  # let skill expire

    atk_buffs = [b for b in q.buffs if b.source_tag == _S3_BUFF_TAG]
    assert len(atk_buffs) == 0, "ATK buff must be removed after S3 ends"


# ---------------------------------------------------------------------------
# Test 5: Block reverts to 2 on skill end
# ---------------------------------------------------------------------------

def test_s3_block_reverts_on_end():
    world = _world()
    q = make_qiubai(slot="S3")
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    world.add_unit(q)
    _enemy(world, x=1.0, y=1.0)

    q.skill.sp = float(q.skill.sp_cost)
    _ticks(world, 0.1)
    assert q.block == _S3_BLOCK

    _ticks(world, _S3_DURATION + 0.5)

    assert q.block == 2, f"Block must revert to 2 after S3 ends, got {q.block}"


# ---------------------------------------------------------------------------
# Test 6: Feathered Gale talent regression — True burst on 3rd hit
# ---------------------------------------------------------------------------

def test_talent_feathered_gale_burst():
    world = _world()
    q = make_qiubai(slot="S3")
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    world.add_unit(q)

    e = _enemy(world, x=1.0, y=1.0, hp=99999)
    e.defence = 0; e.res = 0.0

    # Fire talent callback twice manually — seal count should reach 3 on 3rd hit
    from core.systems.talent_registry import fire_on_attack_hit
    hp_before = e.hp
    fire_on_attack_hit(world, q, e, damage=100)
    fire_on_attack_hit(world, q, e, damage=100)
    hp_after_2 = e.hp
    fire_on_attack_hit(world, q, e, damage=100)
    hp_after_3 = e.hp

    # The 3rd hit should trigger a True burst
    burst_damage = (hp_after_2 - hp_after_3) - (hp_before - hp_after_2)
    assert burst_damage > 0, "3rd hit must trigger Feathered Gale True burst"
