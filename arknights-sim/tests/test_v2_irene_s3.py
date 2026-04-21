"""Irene S3 "Sword of Vengeance" — ATK+80%, 25s, AUTO trigger.

Tests cover:
  - S3 configured correctly (slot, sp_cost=35, initial_sp=10, 25s, AUTO trigger)
  - ATK+80% buff applied on S3 start
  - ATK buff cleared on S3 end
  - Blade of Judgement talent applies FRAGILE on attack hit
  - FRAGILE duration and amount correct
  - S2 regression (Swift Judgement unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, BuffAxis, StatusKind
from core.systems import register_default_systems
from data.characters.irene import (
    make_irene,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION,
    _TALENT_TAG, _TALENT_FRAGILE_TAG, _TALENT_FRAGILE_AMOUNT, _TALENT_FRAGILE_DURATION,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    i = make_irene(slot="S3")
    sk = i.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Sword of Vengeance"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 10
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is True
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+80% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff_applied():
    world = _world()
    i = make_irene(slot="S3")
    base_atk = i.effective_atk
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    world.add_unit(i)
    e = _enemy(world, x=1.0, y=1.0)  # requires_target=True needs a target

    i.skill.sp = float(i.skill.sp_cost)
    world.tick()  # targeting system sets __target__, then AUTO fires

    assert i.skill.active_remaining > 0.0, "S3 must be active"
    buff = next((b for b in i.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be present"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO

    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(i.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {i.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    world = _world()
    i = make_irene(slot="S3")
    base_atk = i.effective_atk
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    world.add_unit(i)
    _enemy(world, x=1.0, y=1.0)  # target needed to trigger AUTO

    i.skill.sp = float(i.skill.sp_cost)
    _ticks(world, _S3_DURATION + 2.0)

    assert i.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in i.buffs), "S3 buff must be cleared on end"
    assert abs(i.effective_atk - base_atk) <= 2, "ATK must revert to base after S3"


# ---------------------------------------------------------------------------
# Test 4: Blade of Judgement talent applies FRAGILE on attack hit
# ---------------------------------------------------------------------------

def test_talent_fragile_on_hit():
    world = _world()
    i = make_irene(slot="S3")
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    world.add_unit(i)

    e = _enemy(world, x=1.0, y=1.0)

    from core.systems.talent_registry import fire_on_attack_hit
    fire_on_attack_hit(world, i, e, damage=100)

    fragile = [s for s in e.statuses if s.kind == StatusKind.FRAGILE and s.source_tag == _TALENT_FRAGILE_TAG]
    assert len(fragile) == 1, "Enemy must have FRAGILE after talent fires"
    assert fragile[0].params.get("amount") == _TALENT_FRAGILE_AMOUNT
    assert abs(fragile[0].expires_at - (world.global_state.elapsed + _TALENT_FRAGILE_DURATION)) < 0.1


# ---------------------------------------------------------------------------
# Test 5: FRAGILE refreshes on repeated hits (source tag unique, no stacking)
# ---------------------------------------------------------------------------

def test_talent_fragile_refreshes():
    world = _world()
    i = make_irene(slot="S3")
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    world.add_unit(i)

    e = _enemy(world, x=1.0, y=1.0)

    from core.systems.talent_registry import fire_on_attack_hit
    fire_on_attack_hit(world, i, e, damage=100)
    _ticks(world, 0.5)
    fire_on_attack_hit(world, i, e, damage=100)

    fragile_list = [s for s in e.statuses if s.kind == StatusKind.FRAGILE and s.source_tag == _TALENT_FRAGILE_TAG]
    assert len(fragile_list) == 1, "FRAGILE must not stack — exactly one instance after refresh"


# ---------------------------------------------------------------------------
# Test 6: S2 regression (Swift Judgement unchanged)
# ---------------------------------------------------------------------------

def test_s2_regression():
    i = make_irene(slot="S2")
    sk = i.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Swift Judgement"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
