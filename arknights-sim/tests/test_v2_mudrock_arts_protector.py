"""Mudrock — DEF_ARTS_PROTECTOR: conditional DEF talent + S3 EventQueue multi-hit.

DEF_ARTS_PROTECTOR trait:
  - archetype = DEF_ARTS_PROTECTOR
  - block = 3, high DEF

Talent "Rocksteady":
  - While HP > 50% max HP, Mudrock gains +_TALENT_DEF_BONUS flat DEF
  - Buff removed when HP drops to/below threshold

S3 "Surge of Rocks": 15s duration
  - On activation: +_S3_ATK_RATIO ATK buff + schedule 5 rock strikes via EventQueue
  - Each strike: physical AoE to all enemies in radius, generates +_STRIKE_DP_PER_HIT DP
  - Strikes fire at _STRIKE_INTERVAL intervals (EventQueue deferred dispatch)
  - ATK buff removed on S3 end; remaining queued strikes still fire if any

Tests cover:
  - Archetype + block
  - Physical attacks damage enemies
  - Talent DEF buff active when HP > 50%
  - Talent DEF buff absent when HP ≤ 50%
  - S3 schedules 5 events in EventQueue on activation
  - S3 strikes deal damage via EventQueue dispatch (deferred)
  - S3 strikes generate DP
  - S3 AoE hits multiple enemies simultaneously
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
from data.characters.mudrock import (
    make_mudrock,
    _TALENT_DEF_BONUS, _TALENT_DEF_BUFF_TAG, _HP_THRESHOLD,
    _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DURATION,
    _STRIKE_COUNT, _STRIKE_INTERVAL, _STRIKE_AOE_RADIUS, _STRIKE_DP_PER_HIT,
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


def _slug(pos=(2, 2), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and block
# ---------------------------------------------------------------------------

def test_mudrock_archetype():
    m = make_mudrock()
    assert m.archetype == RoleArchetype.DEF_ARTS_PROTECTOR
    assert m.block == 3
    assert m.attack_type == AttackType.PHYSICAL


# ---------------------------------------------------------------------------
# Test 2: Normal physical attacks damage enemies
# ---------------------------------------------------------------------------

def test_mudrock_physical_attacks():
    """Mudrock's base attacks deal physical damage (reduced by DEF, not RES)."""
    w = _world()
    m = make_mudrock()
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 0.0
    w.add_unit(m)

    e = _slug(pos=(1, 2))
    w.add_unit(e)

    w.tick()
    assert e.hp < 99999, f"Mudrock must deal damage; hp={e.hp}"


# ---------------------------------------------------------------------------
# Test 3: Talent DEF buff active when HP > 50%
# ---------------------------------------------------------------------------

def test_talent_def_buff_active_above_threshold():
    """When HP > 50%, Rocksteady applies +_TALENT_DEF_BONUS DEF."""
    w = _world()
    m = make_mudrock()
    m.deployed = True; m.position = (0.0, 2.0)
    m.hp = m.max_hp  # full HP — well above 50%
    w.add_unit(m)

    e = _slug(pos=(3, 2))
    w.add_unit(e)

    base_def = m.defence
    w.tick()  # passive_talent_system fires on_tick

    assert any(b.source_tag == _TALENT_DEF_BUFF_TAG for b in m.buffs), \
        "Rocksteady DEF buff must be present when HP > 50%"
    from core.state.unit_state import BuffAxis
    active_def_bonus = sum(
        b.value for b in m.buffs
        if b.source_tag == _TALENT_DEF_BUFF_TAG and b.axis == BuffAxis.DEF
    )
    assert abs(active_def_bonus - _TALENT_DEF_BONUS) <= 1, (
        f"DEF bonus must be {_TALENT_DEF_BONUS}; got {active_def_bonus}"
    )


# ---------------------------------------------------------------------------
# Test 4: Talent DEF buff absent when HP ≤ 50%
# ---------------------------------------------------------------------------

def test_talent_def_buff_absent_below_threshold():
    """When HP ≤ 50%, Rocksteady buff must NOT be applied."""
    w = _world()
    m = make_mudrock()
    m.deployed = True; m.position = (0.0, 2.0)
    m.hp = int(m.max_hp * 0.50)  # exactly at threshold — must NOT apply
    w.add_unit(m)

    e = _slug(pos=(3, 2))
    w.add_unit(e)

    w.tick()
    assert not any(b.source_tag == _TALENT_DEF_BUFF_TAG for b in m.buffs), \
        "Rocksteady DEF buff must be absent when HP ≤ 50%"


# ---------------------------------------------------------------------------
# Test 5: S3 schedules exactly 5 events in EventQueue on activation
# ---------------------------------------------------------------------------

def test_s3_schedules_5_events():
    """S3 activation must schedule exactly _STRIKE_COUNT events in the EventQueue."""
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    e = _slug(pos=(1, 2))
    w.add_unit(e)

    events_before = len(w.event_queue)
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # S3 activates

    assert m.skill.active_remaining > 0.0, "S3 must be active"
    # EventQueue should have _STRIKE_COUNT more events than before
    events_added = len(w.event_queue) - events_before
    assert events_added == _STRIKE_COUNT, (
        f"S3 must schedule {_STRIKE_COUNT} rock strike events; "
        f"got {events_added}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 strikes deal deferred damage via EventQueue
# ---------------------------------------------------------------------------

def test_s3_strikes_deal_damage():
    """Rock strikes fire via EventQueue and deal physical damage to enemies in range."""
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    e = _slug(pos=(1, 2), hp=99999)
    w.add_unit(e)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # S3 activates

    hp_before = e.hp
    # Run long enough for all 5 strikes to fire
    for _ in range(int(TICK_RATE * (_STRIKE_COUNT * _STRIKE_INTERVAL + 0.5))):
        w.tick()

    assert e.hp < hp_before, (
        f"S3 rock strikes must deal damage; hp_before={hp_before}, now={e.hp}"
    )


# ---------------------------------------------------------------------------
# Test 7: S3 strikes generate DP
# ---------------------------------------------------------------------------

def test_s3_strikes_generate_dp():
    """Each rock strike hitting an enemy generates _STRIKE_DP_PER_HIT DP."""
    w = _world()
    w.global_state.dp = 0  # start with 0
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    e = _slug(pos=(1, 2), hp=99999)
    w.add_unit(e)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # S3 activates

    dp_before = w.global_state.dp
    # Run until all 5 strikes complete
    for _ in range(int(TICK_RATE * (_STRIKE_COUNT * _STRIKE_INTERVAL + 0.5))):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    expected_dp = _STRIKE_COUNT * _STRIKE_DP_PER_HIT
    assert dp_gained >= expected_dp, (
        f"S3 must generate ≥{expected_dp} DP ({_STRIKE_COUNT} hits × {_STRIKE_DP_PER_HIT}); "
        f"gained={dp_gained}"
    )


# ---------------------------------------------------------------------------
# Test 8: S3 strikes hit multiple enemies simultaneously (AoE)
# ---------------------------------------------------------------------------

def test_s3_strikes_hit_multiple_enemies():
    """Rock strikes are AoE — multiple enemies within radius all take damage."""
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (1.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    # Two enemies both within _STRIKE_AOE_RADIUS of Mudrock
    e1 = _slug(pos=(1, 2), hp=99999)  # same tile — dist=0
    e2 = _slug(pos=(1, 3), hp=99999)  # 1 tile away — within radius
    w.add_unit(e1)
    w.add_unit(e2)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # S3 activates

    hp1_before = e1.hp
    hp2_before = e2.hp

    for _ in range(int(TICK_RATE * (_STRIKE_INTERVAL + 0.2))):
        w.tick()

    assert e1.hp < hp1_before, "First rock strike must hit enemy 1"
    assert e2.hp < hp2_before, "First rock strike must also hit nearby enemy 2 (AoE)"
