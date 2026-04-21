"""Kal'tsit S3 "All-Out" — ATK+80%, 40s, AUTO trigger.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, initial_sp=20, AUTO)
  - ATK buff (+80%) active during skill
  - ATK buff removed on skill end
  - Mon3tr auto-deploys on battle start (talent regression)
  - Mon3tr death burst deals True damage to nearby enemies (regression)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, BuffAxis, StatusKind
from core.systems import register_default_systems
from data.characters.kal_tsit import (
    make_kal_tsit,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DURATION,
    _MON3TR_TRUE_DAMAGE, _MON3TR_STUN_DURATION, _MON3TR_BURST_TAG,
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
    k = make_kal_tsit(slot="S3")
    sk = k.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "All-Out"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff active during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    world = _world()
    k = make_kal_tsit(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    world.add_unit(k)

    base_atk = k.atk
    k.skill.sp = float(k.skill.sp_cost)
    _ticks(world, 0.1)

    assert k.skill.active_remaining > 0.0, "S3 must be active"
    buffs = [b for b in k.buffs if b.source_tag == _S3_ATK_BUFF_TAG and b.axis == BuffAxis.ATK]
    assert len(buffs) == 1, "Must have exactly one S3 ATK buff"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(k.effective_atk - expected_atk) <= 2, (
        f"Expected effective ATK ~{expected_atk}, got {k.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff removed on skill end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_removed_on_end():
    world = _world()
    k = make_kal_tsit(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    world.add_unit(k)

    k.skill.sp = float(k.skill.sp_cost)
    _ticks(world, 0.1)
    assert k.skill.active_remaining > 0.0

    _ticks(world, _S3_DURATION + 0.5)

    buffs = [b for b in k.buffs if b.source_tag == _S3_ATK_BUFF_TAG]
    assert len(buffs) == 0, "ATK buff must be removed after S3 ends"


# ---------------------------------------------------------------------------
# Test 4: Mon3tr auto-deploys on battle start (talent regression)
# ---------------------------------------------------------------------------

def test_mon3tr_auto_deploys():
    world = _world()
    k = make_kal_tsit(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    world.add_unit(k)  # fires on_battle_start → deploys Mon3tr

    allies = [u for u in world.allies() if u.name == "Mon3tr" and u.alive]
    assert len(allies) == 1, "Mon3tr must auto-deploy on battle start"


# ---------------------------------------------------------------------------
# Test 5: Mon3tr death burst applies True damage + Stun (regression)
# ---------------------------------------------------------------------------

def test_mon3tr_death_burst():
    world = _world()
    k = make_kal_tsit(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    world.add_unit(k)  # fires on_battle_start → deploys Mon3tr

    allies = [u for u in world.allies() if u.name == "Mon3tr" and u.alive]
    assert allies, "Mon3tr must exist"
    mon3tr = allies[0]

    # Place enemy adjacent to Mon3tr (Chebyshev ≤ 1)
    mon3tr.position = (3.0, 1.0)
    e = _enemy(world, x=3.0, y=2.0, hp=99999)
    e.defence = 0

    hp_before = e.hp
    from core.systems.talent_registry import fire_on_death
    fire_on_death(world, mon3tr)

    assert e.hp < hp_before, "Mon3tr death must deal True damage to adjacent enemies"
    expected_dmg = hp_before - _MON3TR_TRUE_DAMAGE
    assert e.hp == expected_dmg, f"Expected HP={expected_dmg}, got {e.hp}"
    stun = [s for s in e.statuses if s.kind == StatusKind.STUN and s.source_tag == _MON3TR_BURST_TAG]
    assert len(stun) == 1, "Adjacent enemy must be Stunned after Mon3tr death"
