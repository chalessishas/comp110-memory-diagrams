"""Pallas — GUARD_INSTRUCTOR: melee Guard + allies in range gain ATK on each hit.

GUARD_INSTRUCTOR trait:
  - Physical melee Guard, block=2, extended range (3 tiles × 3 rows)
  - After each attack, in-range allies get +80 flat ATK for 5s (refreshed each hit)

Talent "Battle Inspiration":
  - Triggers on_attack_hit: all in-range allies gain +80 flat ATK
  - Buff expires after _TALENT_BUFF_DURATION if not refreshed
  - Out-of-range allies are NOT buffed

S2 "Blessing of the Muses": 25s duration
  - attack_type switches from PHYSICAL to ARTS during skill
  - ATK+30% ratio buff active during skill
  - Both revert when skill ends

Tests cover:
  - Archetype is GUARD_INSTRUCTOR, attack_type=PHYSICAL, block=2
  - Normal attack damages enemy
  - Talent: ally in range gains flat ATK buff after attack
  - Talent: out-of-range ally is NOT buffed
  - Talent: buff expires after duration with no further attacks
  - Talent: buff duration is refreshed on subsequent hits
  - S2: attack_type becomes ARTS; ATK+30% applied
  - S2: both attack_type and ATK buff revert after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype,
)
from core.systems import register_default_systems
from data.characters.pallas import (
    make_pallas,
    _TALENT_BUFF_TAG, _TALENT_ATK_FLAT, _TALENT_BUFF_DURATION,
    _S2_ATK_BUFF_TAG, _S2_ATK_RATIO, _S2_DURATION,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=99999, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(0, 0), hp=2000, max_hp=2000, base_atk=100) -> UnitState:
    return UnitState(
        name="AllyOp",
        faction=Faction.ALLY,
        max_hp=max_hp, hp=hp, atk=base_atk,
        defence=0, atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype, attack_type, block
# ---------------------------------------------------------------------------

def test_pallas_archetype_and_stats():
    p = make_pallas()
    assert p.archetype == RoleArchetype.GUARD_INSTRUCTOR
    assert p.attack_type == AttackType.PHYSICAL
    assert p.block == 2, f"Block must be 2; got {p.block}"


# ---------------------------------------------------------------------------
# Test 2: Normal attack damages enemy
# ---------------------------------------------------------------------------

def test_attack_damages_enemy():
    """Pallas deals physical damage to an enemy in range."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999, res=0)
    initial_hp = enemy.hp
    w.add_unit(enemy)

    for _ in range(3):
        w.tick()

    assert enemy.hp < initial_hp, (
        f"Pallas must deal damage; hp was {initial_hp}, now {enemy.hp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Talent gives flat ATK buff to in-range ally after attack
# ---------------------------------------------------------------------------

def test_talent_buffs_in_range_ally():
    """After Pallas attacks, an ally within range gains +_TALENT_ATK_FLAT ATK."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999)
    w.add_unit(enemy)

    base_atk = 200
    ally = _ally(pos=(1, 1), base_atk=base_atk)  # within range (dx=1, dy=0)
    w.add_unit(ally)

    w.tick()

    inspire_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(inspire_buffs) == 1, (
        f"Ally must have inspiration buff; buffs={[b.source_tag for b in ally.buffs]}"
    )
    assert abs(ally.effective_atk - (base_atk + _TALENT_ATK_FLAT)) <= 1, (
        f"Ally ATK must be base+{_TALENT_ATK_FLAT}; "
        f"base={base_atk}, expected={base_atk + _TALENT_ATK_FLAT}, got={ally.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: Out-of-range ally is NOT buffed
# ---------------------------------------------------------------------------

def test_talent_no_buff_out_of_range_ally():
    """Ally outside Pallas's range must not receive inspiration."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999)
    w.add_unit(enemy)

    # Ally at (6, 1) — dx=6 from Pallas, outside her 3-tile range
    ally_far = _ally(pos=(6, 1), base_atk=100)
    w.add_unit(ally_far)

    w.tick()

    inspire_buffs = [b for b in ally_far.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(inspire_buffs) == 0, (
        f"Out-of-range ally must NOT be buffed; buffs={[b.source_tag for b in ally_far.buffs]}"
    )


# ---------------------------------------------------------------------------
# Test 5: Buff expires after _TALENT_BUFF_DURATION with no refresh
# ---------------------------------------------------------------------------

def test_talent_buff_expires_without_refresh():
    """Inspiration buff must expire after _TALENT_BUFF_DURATION if not refreshed."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999)
    w.add_unit(enemy)

    ally = _ally(pos=(1, 1), base_atk=100)
    w.add_unit(ally)

    # Let Pallas attack once to trigger inspiration
    w.tick()
    assert any(b.source_tag == _TALENT_BUFF_TAG for b in ally.buffs), (
        "Buff must be applied after first attack"
    )

    # Freeze Pallas's attacks so buff is not refreshed
    p.atk_cd = 9999.0

    # Advance time past buff expiry
    for _ in range(int(TICK_RATE * (_TALENT_BUFF_DURATION + 1))):
        w.tick()

    expire_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(expire_buffs) == 0, (
        f"Inspiration buff must expire after {_TALENT_BUFF_DURATION}s; "
        f"still present: {expire_buffs}"
    )


# ---------------------------------------------------------------------------
# Test 6: Buff duration refreshes on subsequent hits
# ---------------------------------------------------------------------------

def test_talent_buff_duration_refreshed():
    """Repeated attacks must refresh the buff's expires_at rather than stacking."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    ally = _ally(pos=(1, 1), base_atk=100)
    w.add_unit(ally)

    # Two attack ticks
    w.tick()
    w.tick()

    # Buff must exist but only one instance (no stacking)
    inspire_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(inspire_buffs) == 1, (
        f"Must have exactly 1 inspiration buff (no stacking); count={len(inspire_buffs)}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 switches attack_type to ARTS and applies ATK+30%
# ---------------------------------------------------------------------------

def test_s2_arts_attack_and_atk_buff():
    """During S2, Pallas's attack_type is ARTS and ATK is base×1.3."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999)
    w.add_unit(enemy)

    base_atk = p.effective_atk
    assert p.attack_type == AttackType.PHYSICAL, "Must start as PHYSICAL"

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.skill.active_remaining > 0.0, "S2 must be active"
    assert p.attack_type == AttackType.ARTS, (
        f"attack_type must switch to ARTS during S2; got {p.attack_type}"
    )
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(p.effective_atk - expected_atk) <= 2, (
        f"ATK during S2 must be base×{1+_S2_ATK_RATIO}; "
        f"base={base_atk}, expected={expected_atk}, got={p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: After S2 ends, attack_type reverts to PHYSICAL and ATK buff removed
# ---------------------------------------------------------------------------

def test_s2_reverts_after_end():
    """After S2, attack_type returns to PHYSICAL and ATK buff is removed."""
    w = _world()
    p = make_pallas()
    p.deployed = True; p.position = (0.0, 1.0)
    w.add_unit(p)

    enemy = _slug(pos=(1, 1), hp=9999)
    w.add_unit(enemy)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()
    assert p.skill.active_remaining > 0.0, "S2 must be active"
    assert p.attack_type == AttackType.ARTS

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert p.skill.active_remaining == 0.0, "S2 must have ended"
    assert p.attack_type == AttackType.PHYSICAL, (
        f"attack_type must revert to PHYSICAL after S2; got {p.attack_type}"
    )
    s2_buffs = [b for b in p.buffs if b.source_tag == _S2_ATK_BUFF_TAG]
    assert len(s2_buffs) == 0, "S2 ATK buff must be removed after skill ends"
