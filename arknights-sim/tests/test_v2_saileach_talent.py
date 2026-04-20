"""Saileach talent "Vanguard's Ruse" — all deployed Vanguards gain +2 SP at battle start.

Tests cover:
  - Talent configured correctly
  - Saileach herself (Vanguard) gains +2 SP
  - A second deployed Vanguard ally also gains +2 SP
  - A non-Vanguard ally (Sniper) does NOT gain SP from this talent
  - SP does not exceed sp_cost cap
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype, TileType,
    TICK_RATE, SPGainMode, SkillTrigger,
)
from core.systems import register_default_systems
from data.characters.saileach import (
    make_saileach, _VANGUARDS_RUSE_TAG, _SP_GRANT,
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


def _vanguard_stub(pos=(2, 1)) -> UnitState:
    u = UnitState(
        name="VanguardStub",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=100, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        block=1,
    )
    u.range_shape = RangeShape(tiles=((0, 0), (1, 0)))
    u.skill = SkillComponent(
        name="Stub Skill",
        slot="S1",
        sp_cost=20,
        initial_sp=0,
        duration=5.0,
        sp_gain_mode=SPGainMode.AUTO_ATTACK,
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="__nonexistent__",
    )
    u.skill.sp = 0.0
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _sniper_stub(pos=(3, 1)) -> UnitState:
    u = UnitState(
        name="SniperStub",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=100, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        block=1,
    )
    u.range_shape = RangeShape(tiles=((1, 0), (2, 0)))
    u.skill = SkillComponent(
        name="Stub Skill",
        slot="S1",
        sp_cost=20,
        initial_sp=0,
        duration=5.0,
        sp_gain_mode=SPGainMode.AUTO_ATTACK,
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="__nonexistent__",
    )
    u.skill.sp = 0.0
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: Talent is configured correctly
# ---------------------------------------------------------------------------

def test_saileach_talent_configured():
    s = make_saileach(slot="S2")
    assert len(s.talents) == 1
    assert s.talents[0].name == "Vanguard's Ruse"
    assert s.talents[0].behavior_tag == _VANGUARDS_RUSE_TAG


# ---------------------------------------------------------------------------
# Test 2: Saileach herself gains +2 SP at battle start
# ---------------------------------------------------------------------------

def test_vanguards_ruse_buffs_saileach_self():
    w = _world()
    s = make_saileach(slot="S1")   # S1: initial_sp=11
    s.deployed = True; s.position = (0.0, 1.0)
    sp_before = s.skill.sp   # should equal initial_sp=11 before add_unit fires battle_start
    w.add_unit(s)

    _ticks(w, 0.1)

    assert s.skill.sp >= sp_before + _SP_GRANT - 0.5, (
        f"Saileach must gain +{_SP_GRANT} SP from her own talent; "
        f"before={sp_before:.1f}, after={s.skill.sp:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 3: Deployed Vanguard ally also gains +2 SP
# ---------------------------------------------------------------------------

def test_vanguards_ruse_buffs_vanguard_ally():
    w = _world()
    # van must be on field before Saileach is added (talent fires on Saileach's add_unit)
    van = _vanguard_stub(pos=(2, 1))
    van.skill.sp = 0.0
    w.add_unit(van)

    s = make_saileach(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)   # talent fires here — van is already deployed

    _ticks(w, 0.1)

    assert van.skill.sp >= _SP_GRANT - 0.1, (
        f"Vanguard ally must gain +{_SP_GRANT} SP from Saileach talent; got {van.skill.sp:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 4: Non-Vanguard (Sniper) does NOT gain SP
# ---------------------------------------------------------------------------

def test_vanguards_ruse_skips_non_vanguard():
    w = _world()
    sniper = _sniper_stub(pos=(3, 1))
    sniper.skill.sp = 0.0
    w.add_unit(sniper)

    s = make_saileach(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    _ticks(w, 0.1)

    assert sniper.skill.sp == 0.0, (
        f"Sniper must not receive Vanguard's Ruse SP; got {sniper.skill.sp:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 5: SP does not exceed sp_cost cap
# ---------------------------------------------------------------------------

def test_vanguards_ruse_sp_capped():
    w = _world()
    van = _vanguard_stub(pos=(2, 1))
    van.skill.sp_cost = 5
    van.skill.sp = 4.0   # only 1 below cap, talent grants +2
    w.add_unit(van)

    s = make_saileach(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    _ticks(w, 0.1)

    assert van.skill.sp <= float(van.skill.sp_cost), (
        f"SP must be capped at sp_cost={van.skill.sp_cost}; got {van.skill.sp:.2f}"
    )
