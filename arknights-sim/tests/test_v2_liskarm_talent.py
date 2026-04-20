"""Liskarm talent: Lightning Discharge — arc damage + SP battery (self + 1 nearby ally)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import TileType, TICK_RATE, Faction, AttackType, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import register_skill
from data.characters import make_liskarm
from data.enemies import make_originium_slug

register_skill("_test_noop_liskarm")


PATH = [(x, 0) for x in range(4)]


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_lightning_discharge_deals_damage_to_attacker():
    """When slug attacks Liskarm, Liskarm's arc fires back and deals Arts damage to slug."""
    w = _world()
    liskarm = make_liskarm()
    liskarm.deployed = True
    liskarm.position = (1.0, 0.0)
    w.add_unit(liskarm)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.blocked_by_unit_ids = [liskarm.unit_id]
    slug.atk_cd = 0.0
    w.add_unit(slug)

    slug_hp_before = slug.hp

    # Run until slug has attacked Liskarm at least once
    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.hp < slug_hp_before:
            break

    assert slug.hp < slug_hp_before, \
        f"Lightning Discharge must deal damage to attacker, slug HP unchanged: {slug.hp}"


def test_lightning_discharge_uses_liskarm_atk():
    """Arc damage is 120% of Liskarm's ATK (Arts, reduced by slug RES=0 → full)."""
    w = _world()
    liskarm = make_liskarm()
    liskarm.deployed = True
    liskarm.position = (1.0, 0.0)
    w.add_unit(liskarm)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.res = 0.0   # no resistance → full Arts damage
    slug.blocked_by_unit_ids = [liskarm.unit_id]
    slug.atk_cd = 0.0
    w.add_unit(slug)

    # Prevent Liskarm from attacking so only arc fires
    liskarm.atk_cd = 999.0

    slug_hp_before = slug.hp

    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.hp < slug_hp_before:
            break

    expected_arc = int(liskarm.effective_atk * 1.20)
    actual_dmg = slug_hp_before - slug.hp
    assert actual_dmg == expected_arc, \
        f"Arc damage should be {expected_arc} (120% ATK={liskarm.effective_atk}), got {actual_dmg}"


# ---------------------------------------------------------------------------
# Helpers for SP battery tests
# ---------------------------------------------------------------------------

def _world_2x2() -> World:
    grid = TileGrid(width=4, height=2)
    for x in range(4):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally_with_skill(position, sp_cost=20):
    """Simple ally unit with a skill that can accumulate SP."""
    u = UnitState(
        name="TestAlly",
        faction=Faction.ALLY,
        max_hp=5000, hp=5000,
        atk=100, defence=0, res=0.0,
        atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=RangeShape(tiles=((0, 0),)),
        deployed=True,
        position=(float(position[0]), float(position[1])),
    )
    u.skill = SkillComponent(
        name="TestSkill", slot="S1",
        sp_cost=sp_cost, duration=5.0,
        sp_gain_mode=SPGainMode.AUTO_TIME,
        behavior_tag="_test_noop_liskarm",
    )
    u.skill.sp = 0.0
    return u


# ---------------------------------------------------------------------------
# Test: Liskarm gains SP on being hit
# ---------------------------------------------------------------------------

def test_liskarm_gains_sp_when_hit():
    """When slug attacks Liskarm, she gains +1 SP (SP battery: self)."""
    w = _world_2x2()
    lisk = make_liskarm()
    lisk.deployed = True
    lisk.position = (1.0, 0.0)
    lisk.skill = SkillComponent(
        name="S2", slot="S2",
        sp_cost=30, duration=10.0,
        sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
        behavior_tag="_test_noop_liskarm",
    )
    lisk.skill.sp = 0.0
    w.add_unit(lisk)

    slug = make_originium_slug(path=[(1, 0)] * 5)
    slug.deployed = True; slug.position = (1.0, 0.0)
    slug.blocked_by_unit_ids = [lisk.unit_id]
    slug.move_speed = 0.0; slug.atk_cd = 0.0; slug.atk = 100
    w.add_unit(slug)

    lisk.atk_cd = 999.0   # don't let Liskarm attack — only arc/SP matters
    sp_before = lisk.skill.sp

    for _ in range(TICK_RATE * 3):
        w.tick()
        if lisk.skill.sp > sp_before:
            break

    assert lisk.skill.sp > sp_before, (
        f"Liskarm must gain SP when hit; sp stayed at {lisk.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test: Nearby ally gains SP when Liskarm is hit
# ---------------------------------------------------------------------------

def test_sp_battery_grants_sp_to_nearby_ally():
    """When Liskarm is hit, a nearby allied operator with skill room gains +1 SP."""
    w = _world_2x2()
    lisk = make_liskarm()
    lisk.deployed = True; lisk.position = (1.0, 0.0); lisk.atk_cd = 999.0
    w.add_unit(lisk)

    ally = _ally_with_skill(position=(1, 1), sp_cost=30)  # adjacent (distance=1.0)
    w.add_unit(ally)

    slug = make_originium_slug(path=[(1, 0)] * 5)
    slug.deployed = True; slug.position = (1.0, 0.0)
    slug.blocked_by_unit_ids = [lisk.unit_id]
    slug.move_speed = 0.0; slug.atk_cd = 0.0; slug.atk = 100
    w.add_unit(slug)

    ally_sp_before = ally.skill.sp

    for _ in range(TICK_RATE * 3):
        w.tick()
        if ally.skill.sp > ally_sp_before:
            break

    assert ally.skill.sp > ally_sp_before, (
        f"Nearby ally must receive SP from Liskarm SP battery; sp={ally.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test: Out-of-range ally does NOT gain SP
# ---------------------------------------------------------------------------

def test_sp_battery_does_not_reach_far_ally():
    """An ally outside _SP_RADIUS (>1.5 tiles) must NOT gain SP from Liskarm's battery."""
    w = _world_2x2()
    grid = w.tile_grid
    # Extend grid to give room
    from core.state.tile_state import TileGrid, TileState
    grid2 = TileGrid(width=8, height=2)
    for x in range(8):
        for y in range(2):
            grid2.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w2 = World(tile_grid=grid2)
    w2.global_state.dp_gain_rate = 0.0
    register_default_systems(w2)

    lisk = make_liskarm()
    lisk.deployed = True; lisk.position = (1.0, 0.0); lisk.atk_cd = 999.0
    w2.add_unit(lisk)

    far_ally = _ally_with_skill(position=(5, 0), sp_cost=30)  # 4 tiles away
    far_ally.skill.sp_gain_mode = SPGainMode.AUTO_DEFENSIVE  # won't auto-tick SP
    w2.add_unit(far_ally)

    slug = make_originium_slug(path=[(1, 0)] * 5)
    slug.deployed = True; slug.position = (1.0, 0.0)
    slug.blocked_by_unit_ids = [lisk.unit_id]
    slug.move_speed = 0.0; slug.atk_cd = 0.0; slug.atk = 100
    w2.add_unit(slug)

    far_sp_before = far_ally.skill.sp

    for _ in range(TICK_RATE * 5):
        w2.tick()

    assert far_ally.skill.sp == far_sp_before, (
        f"Out-of-range ally must NOT receive SP; sp changed from {far_sp_before} to {far_ally.skill.sp}"
    )
