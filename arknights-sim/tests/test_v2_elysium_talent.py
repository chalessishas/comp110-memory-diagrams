"""Elysium talent "Standard Instruction" — +0.3 SP/s to all deployed Vanguard operators.

Tests cover:
  - Talent configured correctly
  - Vanguard ally gains SP over time while Elysium is deployed
  - Non-Vanguard ally (Sniper) does NOT gain SP from talent
  - Elysium himself (also a Vanguard) gains SP from his own talent
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
from data.characters.elysium import (
    make_elysium, _TALENT_TAG, _TALENT_SP_RATE,
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
    """A Vanguard operator with a skill at 0 SP (ideal recipient for talent)."""
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
        sp_gain_mode=SPGainMode.AUTO_TIME,
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="__nonexistent__",
    )
    u.skill.sp = 0.0
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _sniper_stub(pos=(3, 1)) -> UnitState:
    """A Sniper operator — should NOT receive the talent SP bonus.
    Uses AUTO_ATTACK sp mode so it gains 0 base SP (no enemies to attack).
    """
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
        sp_gain_mode=SPGainMode.AUTO_ATTACK,   # no enemies → 0 base SP
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

def test_elysium_talent_configured():
    e = make_elysium(slot="S1")
    assert len(e.talents) == 1
    assert e.talents[0].name == "Standard Instruction"
    assert e.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Vanguard ally gains SP while Elysium is deployed
# ---------------------------------------------------------------------------

def test_elysium_talent_sp_to_vanguard():
    w = _world()
    e = make_elysium(slot=None)    # slot=None so skill won't fire
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    van = _vanguard_stub(pos=(2, 1))
    w.add_unit(van)

    sp_before = van.skill.sp
    _ticks(w, 5.0)

    expected_min = _TALENT_SP_RATE * 4.5   # generous lower bound
    assert van.skill.sp > sp_before + expected_min, (
        f"Vanguard SP must grow by at least {expected_min:.1f} in 5s; "
        f"got delta={van.skill.sp - sp_before:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 3: Non-Vanguard (Sniper) does NOT get SP from talent
# ---------------------------------------------------------------------------

def test_elysium_talent_no_sp_to_sniper():
    w = _world()
    e = make_elysium(slot=None)
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    sniper = _sniper_stub(pos=(3, 1))
    sp_before = sniper.skill.sp
    w.add_unit(sniper)

    _ticks(w, 5.0)

    assert sniper.skill.sp == sp_before, (
        "Non-Vanguard Sniper must not receive Elysium talent SP bonus"
    )


# ---------------------------------------------------------------------------
# Test 4: Elysium himself (Vanguard) gains SP from his own talent
# ---------------------------------------------------------------------------

def test_elysium_talent_buffs_self():
    w = _world()
    e = make_elysium(slot="S1")   # has skill at initial_sp=10
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    sp_before = e.skill.sp
    _ticks(w, 5.0)

    assert e.skill.sp > sp_before, (
        "Elysium himself (Vanguard) must gain SP from his own talent"
    )


# ---------------------------------------------------------------------------
# Test 5: SP does not exceed sp_cost cap
# ---------------------------------------------------------------------------

def test_elysium_talent_sp_capped_at_cost():
    w = _world()
    e = make_elysium(slot=None)
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    van = _vanguard_stub(pos=(2, 1))
    van.skill.sp = float(van.skill.sp_cost) - 0.1   # almost full
    w.add_unit(van)

    _ticks(w, 10.0)   # more than enough to fill

    assert van.skill.sp <= float(van.skill.sp_cost), (
        "SP must be capped at sp_cost; talent must not overflow"
    )
