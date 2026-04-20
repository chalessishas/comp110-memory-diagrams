"""Weedy — Free-Flowing DEF buff (not-blocking) + S3 AoE BIND mechanic."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, StatusKind
from core.systems import register_default_systems
from data.characters.weedy import (
    make_weedy, _TALENT_TAG, _TALENT_DEF_RATIO,
    _S3_ATK_RATIO, _S3_DURATION, _S3_BIND_DURATION,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=9999, atk=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = atk
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered correctly
# ---------------------------------------------------------------------------

def test_weedy_talent_registered():
    weedy = make_weedy()
    assert len(weedy.talents) == 1
    assert weedy.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Free-Flowing grants DEF buff when not blocking
# ---------------------------------------------------------------------------

def test_free_flowing_buff_when_not_blocking():
    """DEF buff activates when Weedy has no blocked enemies."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 999.0
    w.add_unit(weedy)

    def_base = weedy.effective_def
    w.tick()   # passive_talent_system fires on_tick

    assert weedy.effective_def > def_base, "DEF buff must apply when not blocking"
    expected = int(def_base * (1.0 + _TALENT_DEF_RATIO))
    assert weedy.effective_def == expected, (
        f"Expected DEF={expected}, got {weedy.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: Free-Flowing buff removed when blocking
# ---------------------------------------------------------------------------

def test_free_flowing_buff_removed_when_blocking():
    """DEF buff is cleared once Weedy begins blocking an enemy."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 999.0
    w.add_unit(weedy)

    # Tick to activate buff
    w.tick()
    assert weedy.effective_def > weedy.defence, "Buff should be active initially"

    # Place enemy on same tile — targeting system assigns Weedy as blocker
    slug = _slug(pos=(0, 1), hp=9999, atk=0)
    w.add_unit(slug)

    w.tick()  # targeting system assigns block, talent_on_tick removes buff

    # Verify blocking assignment happened
    is_blocking = any(weedy.unit_id in e.blocked_by_unit_ids for e in w.enemies())
    assert is_blocking, "Weedy must be assigned as blocker"
    assert weedy.effective_def == weedy.defence, "DEF buff must be removed when blocking"


# ---------------------------------------------------------------------------
# Test 4: S3 activates AoE ARTS attack + ATK buff
# ---------------------------------------------------------------------------

def test_weedy_s3_atk_buff_and_arts():
    """S3 fires: ATK increases +160% and attack_type switches to ARTS."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 999.0
    w.add_unit(weedy)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = weedy.effective_atk
    weedy.skill.sp = weedy.skill.sp_cost
    w.tick()  # S3 fires

    assert weedy.skill.active_remaining > 0.0, "S3 must be active"
    expected_atk = int(atk_base * (1.0 + _S3_ATK_RATIO))
    assert weedy.effective_atk == expected_atk, (
        f"S3 ATK should be {expected_atk}, got {weedy.effective_atk}"
    )
    assert weedy.attack_type == AttackType.ARTS, "S3 must switch to ARTS"


# ---------------------------------------------------------------------------
# Test 5: S3 applies BIND to enemy on hit
# ---------------------------------------------------------------------------

def test_weedy_s3_binds_enemy_on_hit():
    """After S3 activates and Weedy attacks, the target gets BIND status."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 0.0   # attacks as soon as possible
    w.add_unit(weedy)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    weedy.skill.sp = weedy.skill.sp_cost
    # S3 fires in SKILL phase of tick 1; first S3 attack lands around tick 13
    # (atk_interval=1.2s → 12 ticks between attacks)
    for _ in range(20):
        w.tick()

    assert slug.has_status(StatusKind.BIND), "Enemy must be BOUND after Weedy S3 hit"


# ---------------------------------------------------------------------------
# Test 6: BIND prevents enemy movement
# ---------------------------------------------------------------------------

def test_weedy_s3_bind_stops_movement():
    """A BOUND enemy cannot act (can_act() returns False)."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 0.0
    w.add_unit(weedy)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    weedy.skill.sp = weedy.skill.sp_cost
    # S3 fires tick 1; first S3 attack ~tick 13 — bind applied
    for _ in range(20):
        w.tick()

    assert slug.has_status(StatusKind.BIND), "Slug must be bound first"
    assert not slug.can_act(), "BOUND enemy must not be able to act"


# ---------------------------------------------------------------------------
# Test 7: BIND expires after 2 seconds
# ---------------------------------------------------------------------------

def test_weedy_s3_bind_expires():
    """BIND status is removed after _S3_BIND_DURATION seconds pass."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 0.0
    w.add_unit(weedy)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    weedy.skill.sp = weedy.skill.sp_cost
    # S3 fires tick 1; first S3 attack ~tick 13
    for _ in range(20):
        w.tick()

    assert slug.has_status(StatusKind.BIND), "Bind must be applied first"

    # Disable Weedy attacking further (prevent bind refresh)
    weedy.atk_cd = 999.0

    # Advance time past BIND expiry
    for _ in range(int(TICK_RATE * (_S3_BIND_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.BIND), "BIND must expire after 2s without refresh"


# ---------------------------------------------------------------------------
# Test 8: S3 AoE — both enemies in range get bound
# ---------------------------------------------------------------------------

def test_weedy_s3_binds_multiple_enemies():
    """AoE mode: all enemies in range are hit and bound."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 0.0
    w.add_unit(weedy)

    slug_a = _slug(pos=(1, 1), hp=99999, atk=0)
    slug_b = _slug(pos=(1, 1), hp=99999, atk=0)  # same tile
    w.add_unit(slug_a)
    w.add_unit(slug_b)

    weedy.skill.sp = weedy.skill.sp_cost
    for _ in range(20):
        w.tick()

    assert slug_a.has_status(StatusKind.BIND), "First enemy must be bound"
    assert slug_b.has_status(StatusKind.BIND), "Second enemy must also be bound"


# ---------------------------------------------------------------------------
# Test 9: S3 on_end reverts attack_type and clears AoE flag
# ---------------------------------------------------------------------------

def test_weedy_s3_reverts_on_end():
    """After S3 expires, attack_type reverts to PHYSICAL and AoE is cleared."""
    w = _world()
    weedy = make_weedy()
    weedy.deployed = True
    weedy.position = (0.0, 1.0)
    weedy.atk_cd = 999.0
    w.add_unit(weedy)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    weedy.skill.sp = weedy.skill.sp_cost
    w.tick()  # S3 fires

    # Run past full duration
    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert weedy.skill.active_remaining == 0.0, "S3 must have expired"
    assert weedy.attack_type == AttackType.PHYSICAL, "attack_type must revert to PHYSICAL"
    assert not getattr(weedy, "_attack_all_in_range", False), "AoE flag must be cleared"
    assert not getattr(weedy, "_weedy_bind_active", False), "Bind flag must be cleared"
