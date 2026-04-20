"""Zima — Lead Whistle STUN-on-deploy talent + S2 ATK burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind
from core.systems import register_default_systems
from data.characters.zima import (
    make_zima, _TALENT_TAG, _STUN_DURATION, _STUN_RANGE,
    _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_zima_talent_registered():
    z = make_zima()
    assert len(z.talents) == 1
    assert z.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Deploy stuns enemy in range
# ---------------------------------------------------------------------------

def test_lead_whistle_stuns_enemy_in_range():
    """When Zima is added (deployed), nearby enemy is instantly STUNNED."""
    w = _world()
    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    z.skill = None
    w.add_unit(z)  # on_battle_start fires here

    assert slug.has_status(StatusKind.STUN), (
        "Enemy within deploy range must be STUNNED on Zima's deploy"
    )


# ---------------------------------------------------------------------------
# Test 3: STUN blocks movement AND attack
# ---------------------------------------------------------------------------

def test_stun_blocks_movement_and_attack():
    """STUN: can_act() = False (blocks both movement and attack)."""
    w = _world()
    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    z.skill = None
    w.add_unit(z)

    assert slug.has_status(StatusKind.STUN), "STUN must be applied"
    assert not slug.can_act(), "STUNNED enemy must not be able to act"
    assert not slug.can_use_skill(), "STUNNED enemy must not use skills"


# ---------------------------------------------------------------------------
# Test 4: STUN expires after _STUN_DURATION
# ---------------------------------------------------------------------------

def test_stun_expires():
    """STUN clears after _STUN_DURATION seconds."""
    w = _world()
    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    z.skill = None
    w.add_unit(z)

    assert slug.has_status(StatusKind.STUN), "STUN must be applied on deploy"

    for _ in range(int(TICK_RATE * (_STUN_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.STUN), "STUN must expire after 3s"
    assert slug.can_act(), "Enemy can act again after STUN expires"


# ---------------------------------------------------------------------------
# Test 5: Enemy beyond range NOT stunned
# ---------------------------------------------------------------------------

def test_lead_whistle_does_not_stun_out_of_range():
    """Enemy more than _STUN_RANGE tiles away is NOT stunned on deploy."""
    w = _world()
    # Place enemy far away (Manhattan distance > 3 from Zima at (0,1))
    slug_far = _slug(pos=(7, 1))   # distance = 7 > 3
    w.add_unit(slug_far)

    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    z.skill = None
    w.add_unit(z)

    assert not slug_far.has_status(StatusKind.STUN), (
        "Enemy 7 tiles away must NOT be stunned (range = 3)"
    )


# ---------------------------------------------------------------------------
# Test 6: Near enemy stunned, far enemy not — both in same world
# ---------------------------------------------------------------------------

def test_lead_whistle_range_boundary():
    """Near enemy (dist ≤ 3) stunned; far enemy (dist > 3) not stunned."""
    w = _world()
    slug_near = _slug(pos=(2, 1))   # distance = 2, in range
    slug_far = _slug(pos=(6, 1))    # distance = 6, out of range
    w.add_unit(slug_near)
    w.add_unit(slug_far)

    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    z.skill = None
    w.add_unit(z)

    assert slug_near.has_status(StatusKind.STUN), "Near enemy must be STUNNED"
    assert not slug_far.has_status(StatusKind.STUN), "Far enemy must NOT be stunned"


# ---------------------------------------------------------------------------
# Test 7: S2 activates ATK buff
# ---------------------------------------------------------------------------

def test_zima_s2_atk_buff():
    """S2 fires: ATK increases by +80%."""
    w = _world()
    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    w.add_unit(z)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = z.effective_atk
    z.skill.sp = z.skill.sp_cost
    w.tick()

    assert z.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert z.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {z.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_zima_s2_buff_removed_on_end():
    """ATK reverts to base after S2 expires."""
    w = _world()
    z = make_zima()
    z.deployed = True
    z.position = (0.0, 1.0)
    z.atk_cd = 999.0
    w.add_unit(z)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = z.effective_atk
    z.skill.sp = z.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert z.skill.active_remaining == 0.0, "S2 must have expired"
    assert z.effective_atk == atk_base, "ATK must revert to base after S2"
