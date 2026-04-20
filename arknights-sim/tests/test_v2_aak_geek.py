"""Aak — SPEC_GEEK: ARTS attacks + friendly-fire syringe talent.

SPEC_GEEK trait:
  - attack_type = ARTS (unusual for a Specialist)
  - archetype = SPEC_GEEK

Talent "Emergency Protocol":
  - After each attack against an enemy, inject the nearest in-range ally
  - Injection deals _SYRINGE_TRUE_DMG True damage to the ally
  - Ally receives +_SYRINGE_ATK_RATIO% ATK buff for _SYRINGE_DURATION seconds

S2 "Medical Protocol": 15s duration
  - Aak gains +_S2_SELF_ATK_RATIO% ATK
  - Enhanced syringe: _S2_SYRINGE_DMG true damage + stronger +_S2_ATK_RATIO% ATK buff
  - Both revert on skill end

Tests cover:
  - Archetype is SPEC_GEEK, attack_type=ARTS, block=1
  - ARTS damage to enemies (not physical)
  - Talent injects nearest in-range ally with true damage on attack
  - Injected ally receives ATK buff
  - Out-of-range ally is NOT injected
  - S2 applies self-ATK buff to Aak
  - S2 syringe damage is reduced (_S2_SYRINGE_DMG < _SYRINGE_TRUE_DMG)
  - S2 self-ATK buff removed after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype
from core.systems import register_default_systems
from data.characters.aak import (
    make_aak,
    _SYRINGE_TRUE_DMG, _SYRINGE_ATK_RATIO, _SYRINGE_DURATION,
    _S2_SELF_ATK_RATIO, _S2_SYRINGE_DMG, _S2_ATK_RATIO, _S2_DURATION,
    _SYRINGE_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(3, 2)) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = 99999; e.hp = 99999; e.atk = 0
    e.defence = 0; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(2, 2), max_hp=5000) -> UnitState:
    return UnitState(
        name="Ally",
        faction=Faction.ALLY,
        max_hp=max_hp, hp=max_hp, atk=500,
        defence=0, res=0.0,
        atk_interval=999.0, block=1,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype and base stats
# ---------------------------------------------------------------------------

def test_aak_archetype():
    a = make_aak()
    assert a.archetype == RoleArchetype.SPEC_GEEK
    assert a.attack_type == AttackType.ARTS
    assert a.block == 1


# ---------------------------------------------------------------------------
# Test 2: ARTS damage to enemies
# ---------------------------------------------------------------------------

def test_arts_damage_to_enemies():
    """Aak's attacks deal ARTS damage (reduced by RES, not DEF)."""
    w1 = _world()
    a1 = make_aak()
    a1.deployed = True; a1.position = (0.0, 2.0); a1.atk_cd = 0.0
    w1.add_unit(a1)
    e_no_res = _slug(pos=(2, 2))
    e_no_res.res = 0.0; e_no_res.defence = 0
    w1.add_unit(e_no_res)
    w1.tick()
    dmg_no_res = 99999 - e_no_res.hp

    w2 = _world()
    a2 = make_aak()
    a2.deployed = True; a2.position = (0.0, 2.0); a2.atk_cd = 0.0
    w2.add_unit(a2)
    e_hi_res = _slug(pos=(2, 2))
    e_hi_res.res = 60.0; e_hi_res.defence = 0
    w2.add_unit(e_hi_res)
    w2.tick()
    dmg_hi_res = 99999 - e_hi_res.hp

    assert dmg_no_res > 0, "Must deal damage"
    assert dmg_no_res > dmg_hi_res, (
        f"ARTS damage must be reduced by RES; RES=0:{dmg_no_res}, RES=60:{dmg_hi_res}"
    )


# ---------------------------------------------------------------------------
# Test 3: Talent injects nearest in-range ally with true damage
# ---------------------------------------------------------------------------

def test_talent_injects_ally_with_true_damage():
    """When Aak attacks an enemy, the nearest in-range ally takes true damage."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0); a.atk_cd = 0.0
    w.add_unit(a)

    ally = _ally(pos=(2, 2), max_hp=5000)
    w.add_unit(ally)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    hp_before = ally.hp
    w.tick()
    hp_after = ally.hp

    assert hp_after < hp_before, (
        f"Talent must deal true damage to ally; hp_before={hp_before}, after={hp_after}"
    )
    dmg = hp_before - hp_after
    assert abs(dmg - _SYRINGE_TRUE_DMG) <= 2, (
        f"True damage must equal _SYRINGE_TRUE_DMG={_SYRINGE_TRUE_DMG}; got {dmg}"
    )


# ---------------------------------------------------------------------------
# Test 4: Injected ally receives ATK buff
# ---------------------------------------------------------------------------

def test_talent_ally_receives_atk_buff():
    """After injection, the ally has an ATK+_SYRINGE_ATK_RATIO buff."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0); a.atk_cd = 0.0
    w.add_unit(a)

    ally = _ally(pos=(2, 2), max_hp=5000)
    base_atk = ally.effective_atk
    w.add_unit(ally)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    w.tick()

    syringe_buffs = [b for b in ally.buffs if b.source_tag == _SYRINGE_BUFF_TAG]
    assert len(syringe_buffs) == 1, (
        f"Must have 1 syringe buff; got {syringe_buffs}"
    )
    assert abs(syringe_buffs[0].value - _SYRINGE_ATK_RATIO) < 0.01, (
        f"Syringe buff must be +{_SYRINGE_ATK_RATIO}; got {syringe_buffs[0].value}"
    )
    expected_atk = int(base_atk * (1 + _SYRINGE_ATK_RATIO))
    assert abs(ally.effective_atk - expected_atk) <= 2


# ---------------------------------------------------------------------------
# Test 5: Out-of-range ally is NOT injected
# ---------------------------------------------------------------------------

def test_talent_no_injection_out_of_range():
    """Ally beyond Aak's range must not receive syringe injection."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0); a.atk_cd = 0.0
    w.add_unit(a)

    far_ally = _ally(pos=(7, 2), max_hp=5000)  # 7 tiles away — outside range
    w.add_unit(far_ally)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    hp_before = far_ally.hp
    w.tick()

    assert far_ally.hp == hp_before, (
        f"Out-of-range ally must NOT be injected; hp changed: {hp_before} → {far_ally.hp}"
    )
    syringe_buffs = [b for b in far_ally.buffs if b.source_tag == _SYRINGE_BUFF_TAG]
    assert len(syringe_buffs) == 0, "Out-of-range ally must not have syringe buff"


# ---------------------------------------------------------------------------
# Test 6: S2 applies self-ATK buff
# ---------------------------------------------------------------------------

def test_s2_self_atk_buff():
    """During S2, Aak's own effective_atk increases by _S2_SELF_ATK_RATIO."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0)
    w.add_unit(a)

    e = _slug(pos=(2, 2))
    w.add_unit(e)

    base_atk = a.effective_atk
    a.skill.sp = float(a.skill.sp_cost)
    w.tick()

    assert a.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(base_atk * (1 + _S2_SELF_ATK_RATIO))
    assert abs(a.effective_atk - expected) <= 2, (
        f"S2 self-ATK must be base×{1 + _S2_SELF_ATK_RATIO}; "
        f"base={base_atk}, expected={expected}, got={a.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 syringe damage is less than base talent damage
# ---------------------------------------------------------------------------

def test_s2_syringe_reduced_damage():
    """During S2, the syringe deals _S2_SYRINGE_DMG (less than _SYRINGE_TRUE_DMG)."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0); a.atk_cd = 0.0
    w.add_unit(a)

    ally = _ally(pos=(2, 2), max_hp=5000)
    w.add_unit(ally)

    e = _slug(pos=(2, 2))
    w.add_unit(e)

    a.skill.sp = float(a.skill.sp_cost)
    w.tick()  # S2 activates + Aak attacks

    assert a.skill.active_remaining > 0.0
    assert a._aak_s2_active is True

    # Now test injection damage in S2 context
    ally.hp = ally.max_hp  # reset
    a.atk_cd = 0.0
    w.tick()

    dmg_s2 = ally.max_hp - ally.hp
    assert dmg_s2 == _S2_SYRINGE_DMG, (
        f"S2 syringe must deal {_S2_SYRINGE_DMG} true dmg; got {dmg_s2}"
    )
    assert _S2_SYRINGE_DMG < _SYRINGE_TRUE_DMG, "S2 syringe damage must be less than base"


# ---------------------------------------------------------------------------
# Test 8: S2 self-ATK buff removed after skill ends
# ---------------------------------------------------------------------------

def test_s2_buff_removed_after_end():
    """After S2 ends, Aak's self-ATK buff is removed."""
    w = _world()
    a = make_aak()
    a.deployed = True; a.position = (0.0, 2.0)
    w.add_unit(a)

    e = _slug(pos=(2, 2))
    w.add_unit(e)

    base_atk = a.effective_atk
    a.skill.sp = float(a.skill.sp_cost)
    w.tick()
    assert a.skill.active_remaining > 0.0

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert a.skill.active_remaining == 0.0, "S2 must have ended"
    assert abs(a.effective_atk - base_atk) <= 2, (
        f"Self-ATK buff must be removed after S2; base={base_atk}, now={a.effective_atk}"
    )
