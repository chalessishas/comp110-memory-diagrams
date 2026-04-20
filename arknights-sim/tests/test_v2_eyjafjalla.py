"""Eyjafjalla — Pyrobreath faction ATK aura + S2 AoE ARTS splash + S3 AoE TRUE damage."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, AttackType, Faction, Profession
from core.systems import register_default_systems
from data.characters.eyjafjalla import (
    make_eyjafjalla, _S2_SPLASH_RADIUS, _S2_ATK_RATIO,
    _PYROBREATH_BUFF_TAG, _PYROBREATH_ATK_RATIO,
)
from data.enemies import make_originium_slug


def _bare_caster(pos=(3.0, 2.0)) -> UnitState:
    """Plain Caster ally with no talents — used to test Pyrobreath aura."""
    u = UnitState(
        name="BareTestCaster",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=400, defence=0, res=0.0,
        atk_interval=2.0,
        profession=Profession.CASTER,
        block=1, cost=10,
        deployed=True,
        position=pos,
    )
    return u


def _bare_guard(pos=(3.0, 2.0)) -> UnitState:
    """Plain non-Caster ally — must NOT receive Pyrobreath buff."""
    u = UnitState(
        name="BareTestGuard",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=400, defence=0, res=0.0,
        atk_interval=2.0,
        profession=Profession.GUARD,
        block=2, cost=10,
        deployed=True,
        position=pos,
    )
    return u


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos, hp=99999, atk=0) -> 'UnitState':
    from core.state.unit_state import UnitState
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: S2 fires and activates ATK buff
# ---------------------------------------------------------------------------

def test_eyjafjalla_s2_atk_buff():
    """S2 applies +160% ATK ratio buff."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)
    slug = _slug((2, 2), hp=99999)
    w.add_unit(slug)

    atk_base = eyja.effective_atk
    eyja.skill.sp = eyja.skill.sp_cost
    w.tick()

    assert eyja.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert eyja.effective_atk == expected, (
        f"S2 ATK must be {expected}; got {eyja.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 2: S2 activates splash radius
# ---------------------------------------------------------------------------

def test_eyjafjalla_s2_splash_radius():
    """During S2, Eyjafjalla's splash_radius increases to 1.3."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)
    slug = _slug((2, 2), hp=99999)
    w.add_unit(slug)

    assert eyja.splash_radius == 0.0, "Base splash radius must be 0"
    eyja.skill.sp = eyja.skill.sp_cost
    w.tick()

    assert eyja.splash_radius == _S2_SPLASH_RADIUS, (
        f"S2 splash_radius must be {_S2_SPLASH_RADIUS}; got {eyja.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 3: S2 splash hits adjacent enemy
# ---------------------------------------------------------------------------

def test_eyjafjalla_s2_splash_hits_adjacent():
    """S2 AoE: an enemy next to the primary target takes splash damage."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 0.0
    w.add_unit(eyja)

    primary = _slug((2, 2), hp=99999)
    adjacent = _slug((3, 2), hp=99999)   # 1 tile away from primary → within r=1.3
    w.add_unit(primary)
    w.add_unit(adjacent)

    eyja.skill.sp = eyja.skill.sp_cost

    hp_primary_before = primary.hp
    hp_adjacent_before = adjacent.hp

    for _ in range(20):
        w.tick()

    assert primary.hp < hp_primary_before, "Primary target must take damage"
    assert adjacent.hp < hp_adjacent_before, (
        "Adjacent enemy within S2 splash radius must also take damage"
    )


# ---------------------------------------------------------------------------
# Test 4: S2 reverts on end
# ---------------------------------------------------------------------------

def test_eyjafjalla_s2_reverts_on_end():
    """After S2 expires, splash_radius returns to 0 and ATK returns to base."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)
    slug = _slug((2, 2), hp=99999)
    w.add_unit(slug)

    atk_base = eyja.effective_atk
    eyja.skill.sp = eyja.skill.sp_cost
    w.tick()  # S2 fires

    for _ in range(TICK_RATE * 41):
        w.tick()

    assert eyja.skill.active_remaining == 0.0, "S2 must have expired"
    assert eyja.splash_radius == 0.0, "splash_radius must revert to 0 after S2"
    assert eyja.effective_atk == atk_base, "ATK must revert to base after S2"


# ---------------------------------------------------------------------------
# Test 5: S3 converts to TRUE damage
# ---------------------------------------------------------------------------

def test_eyjafjalla_s3_true_damage():
    """S3 converts Eyjafjalla's attacks to TRUE damage type."""
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)
    slug = _slug((2, 2), hp=99999)
    w.add_unit(slug)

    eyja.skill.sp = eyja.skill.sp_cost
    w.tick()

    assert eyja.skill.active_remaining > 0.0, "S3 must be active"
    assert eyja.attack_type == AttackType.TRUE, "S3 must convert to TRUE damage"

# ---------------------------------------------------------------------------
# Test 6: Pyrobreath applies ATK buff to co-deployed Caster
# ---------------------------------------------------------------------------

def test_pyrobreath_buffs_caster_ally():
    """Pyrobreath must apply +14% ATK to a co-deployed Caster ally."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    caster = _bare_caster(pos=(3.0, 2.0))
    w.add_unit(caster)

    atk_base = caster.effective_atk
    w.tick()  # Pyrobreath on_tick fires

    expected_atk = int(atk_base * (1.0 + _PYROBREATH_ATK_RATIO))
    assert caster.effective_atk == expected_atk, (
        f"Pyrobreath must give Caster +{_PYROBREATH_ATK_RATIO*100:.0f}% ATK; "
        f"expected {expected_atk}, got {caster.effective_atk}"
    )
    assert any(b.source_tag == _PYROBREATH_BUFF_TAG for b in caster.buffs), (
        "Caster must have Pyrobreath buff in buff list"
    )


# ---------------------------------------------------------------------------
# Test 7: Pyrobreath does NOT buff non-Caster allies
# ---------------------------------------------------------------------------

def test_pyrobreath_ignores_non_caster():
    """Pyrobreath must NOT apply ATK buff to non-Caster allies."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    guard = _bare_guard(pos=(3.0, 2.0))
    w.add_unit(guard)

    atk_base = guard.effective_atk
    w.tick()

    assert guard.effective_atk == atk_base, "Pyrobreath must NOT buff non-Caster allies"
    assert not any(b.source_tag == _PYROBREATH_BUFF_TAG for b in guard.buffs)


# ---------------------------------------------------------------------------
# Test 8: Pyrobreath does NOT buff Eyjafjalla herself
# ---------------------------------------------------------------------------

def test_pyrobreath_does_not_self_buff():
    """Pyrobreath must NOT apply the buff to Eyjafjalla herself."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    atk_base = eyja.effective_atk
    w.tick()

    assert not any(b.source_tag == _PYROBREATH_BUFF_TAG for b in eyja.buffs), (
        "Eyjafjalla must not have Pyrobreath buff on herself"
    )


# ---------------------------------------------------------------------------
# Test 9: Pyrobreath applies to Caster deployed after Eyjafjalla
# ---------------------------------------------------------------------------

def test_pyrobreath_applies_to_late_deployed_caster():
    """Caster deployed after Eyjafjalla must receive Pyrobreath buff on next tick."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    w.tick()  # Eyjafjalla's aura fires with no other Casters present

    # Now deploy a Caster after Eyjafjalla
    caster = _bare_caster(pos=(3.0, 2.0))
    w.add_unit(caster)
    atk_base = caster.effective_atk

    w.tick()  # Pyrobreath on_tick picks up the new Caster

    expected_atk = int(atk_base * (1.0 + _PYROBREATH_ATK_RATIO))
    assert caster.effective_atk == expected_atk, (
        "Late-deployed Caster must receive Pyrobreath buff on next tick"
    )


# ---------------------------------------------------------------------------
# Test 10: Pyrobreath buff removed when Eyjafjalla retreats
# ---------------------------------------------------------------------------

def test_pyrobreath_removed_on_retreat():
    """When Eyjafjalla retreats, Pyrobreath buff must be removed from all Casters."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    caster = _bare_caster(pos=(3.0, 2.0))
    w.add_unit(caster)

    w.tick()  # Buff applied
    assert any(b.source_tag == _PYROBREATH_BUFF_TAG for b in caster.buffs), (
        "Caster must have buff before Eyjafjalla retreats"
    )

    atk_base = caster.atk  # base ATK without buff

    w.retreat(eyja)  # fires on_retreat → _pyrobreath_cleanup

    assert not any(b.source_tag == _PYROBREATH_BUFF_TAG for b in caster.buffs), (
        "Pyrobreath buff must be removed after Eyjafjalla retreats"
    )
    assert caster.effective_atk == atk_base, "Caster ATK must return to base after retreat"


# ---------------------------------------------------------------------------
# Test 11: Pyrobreath buff removed when Eyjafjalla dies
# ---------------------------------------------------------------------------

def test_pyrobreath_removed_on_death():
    """When Eyjafjalla dies, Pyrobreath buff must be removed from all Casters."""
    w = _world()
    eyja = make_eyjafjalla(slot="S2")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    caster = _bare_caster(pos=(3.0, 2.0))
    w.add_unit(caster)

    w.tick()  # Buff applied
    assert any(b.source_tag == _PYROBREATH_BUFF_TAG for b in caster.buffs)

    # Kill Eyjafjalla
    eyja.hp = 0; eyja.alive = False; eyja._just_died = True
    w.tick()  # cleanup fires on_death → _pyrobreath_cleanup

    assert not any(b.source_tag == _PYROBREATH_BUFF_TAG for b in caster.buffs), (
        "Pyrobreath buff must be removed after Eyjafjalla dies"
    )
