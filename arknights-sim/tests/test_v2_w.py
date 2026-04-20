"""W — Last Will LEVITATE-on-hit talent + S2 ATK burst + S3 delayed bomb (EventQueue)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind
from core.systems import register_default_systems
from data.characters.w import (
    make_w, _TALENT_TAG, _LEVITATE_DURATION, _S2_ATK_RATIO, _S2_DURATION,
    _S3_TAG, _BOMB_DELAY, _BOMB_ATK_RATIO, _BOMB_RADIUS,
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


def _slug(pos=(1, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.defence = defence
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_w_talent_registered():
    w = make_w()
    assert len(w.talents) == 1
    assert w.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit applies LEVITATE
# ---------------------------------------------------------------------------

def test_last_will_applies_levitate():
    """After W hits an enemy, that enemy has LEVITATE status."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 0.0
    w.skill = None
    world.add_unit(w)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    world.tick()

    assert slug.has_status(StatusKind.LEVITATE), "Enemy must have LEVITATE after hit"


# ---------------------------------------------------------------------------
# Test 3: LEVITATE blocks action (can_act = False)
# ---------------------------------------------------------------------------

def test_levitate_blocks_action():
    """LEVITATE: can_act() = False (blocks movement and attack)."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 0.0
    w.skill = None
    world.add_unit(w)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    world.tick()

    assert slug.has_status(StatusKind.LEVITATE), "LEVITATE must be applied"
    assert not slug.can_act(), "LEVITATED enemy must not be able to act"


# ---------------------------------------------------------------------------
# Test 4: LEVITATE still allows damage to be taken
# ---------------------------------------------------------------------------

def test_levitate_does_not_prevent_damage():
    """LEVITATE blocks action but a levitated enemy still takes damage."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 0.0
    w.skill = None
    world.add_unit(w)

    slug = _slug(pos=(1, 1), hp=99999, defence=0)
    world.add_unit(slug)

    world.tick()

    assert slug.has_status(StatusKind.LEVITATE)
    assert slug.hp < slug.max_hp, "Levitated enemy must still take damage"


# ---------------------------------------------------------------------------
# Test 5: LEVITATE expires naturally
# ---------------------------------------------------------------------------

def test_levitate_expires():
    """LEVITATE clears after _LEVITATE_DURATION seconds without refresh."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 0.0
    w.skill = None
    world.add_unit(w)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    world.tick()
    assert slug.has_status(StatusKind.LEVITATE), "LEVITATE must be present"

    w.atk_cd = 999.0  # prevent refresh
    for _ in range(int(TICK_RATE * (_LEVITATE_DURATION + 1))):
        world.tick()

    assert not slug.has_status(StatusKind.LEVITATE), "LEVITATE must expire"
    assert slug.can_act(), "Enemy must be able to act after LEVITATE expires"


# ---------------------------------------------------------------------------
# Test 6: LEVITATE refreshes on re-hit (exactly 1 status)
# ---------------------------------------------------------------------------

def test_levitate_refreshes_on_rehit():
    """A second hit re-applies LEVITATE; exactly one LEVITATE status remains."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 0.0
    w.skill = None
    world.add_unit(w)

    slug = _slug(pos=(1, 1), hp=99999)
    world.add_unit(slug)

    for _ in range(int(w.atk_interval * TICK_RATE) + 1):
        world.tick()

    lev_count = sum(1 for s in slug.statuses if s.kind == StatusKind.LEVITATE)
    assert lev_count == 1, f"Must have exactly 1 LEVITATE, got {lev_count}"


# ---------------------------------------------------------------------------
# Test 7: S2 activates ATK buff
# ---------------------------------------------------------------------------

def test_w_s2_atk_buff():
    """S2 fires: ATK increases by +60%."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 999.0
    world.add_unit(w)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    atk_base = w.effective_atk
    w.skill.sp = w.skill.sp_cost
    world.tick()

    assert w.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert w.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {w.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_w_s2_buff_removed_on_end():
    """ATK reverts to base after S2 expires."""
    world = _world()
    w = make_w()
    w.deployed = True
    w.position = (0.0, 1.0)
    w.atk_cd = 999.0
    world.add_unit(w)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    atk_base = w.effective_atk
    w.skill.sp = w.skill.sp_cost
    world.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        world.tick()

    assert w.skill.active_remaining == 0.0, "S2 must have expired"
    assert w.effective_atk == atk_base, "ATK must revert to base after S2"


# ---------------------------------------------------------------------------
# Tests 9–11: S3 "Chaos Edict" — delayed bomb via EventQueue
# ---------------------------------------------------------------------------

def test_w_s3_schedules_bomb_event():
    """S3 activation must schedule exactly 1 bomb event in the EventQueue."""
    world = _world()
    w = make_w(slot="S3")
    w.deployed = True; w.position = (0.0, 1.0); w.atk_cd = 999.0
    world.add_unit(w)

    slug = _slug(pos=(2, 1), hp=99999)
    world.add_unit(slug)

    events_before = len(world.event_queue)
    w.skill.sp = float(w.skill.sp_cost)
    world.tick()  # S3 activates (instant duration=0)

    events_added = len(world.event_queue) - events_before
    assert events_added == 1, (
        f"S3 must schedule exactly 1 bomb event; scheduled {events_added}"
    )


def test_w_s3_bomb_detonates_after_delay():
    """Bomb must NOT deal damage immediately; must deal damage after _BOMB_DELAY seconds."""
    world = _world()
    w = make_w(slot="S3")
    w.deployed = True; w.position = (0.0, 1.0); w.atk_cd = 999.0
    world.add_unit(w)

    slug = _slug(pos=(1, 1), hp=99999)
    world.add_unit(slug)

    w.skill.sp = float(w.skill.sp_cost)
    world.tick()  # S3 activates — bomb placed
    hp_at_throw = slug.hp

    # Just before detonation: no damage yet
    for _ in range(int(TICK_RATE * (_BOMB_DELAY * 0.5))):
        world.tick()
    hp_mid = slug.hp
    assert hp_mid == hp_at_throw, (
        f"Bomb must not detonate early; hp at throw={hp_at_throw}, mid={hp_mid}"
    )

    # After detonation: damage must have been dealt
    for _ in range(int(TICK_RATE * _BOMB_DELAY)):
        world.tick()
    hp_after = slug.hp
    assert hp_after < hp_at_throw, (
        f"Bomb must deal damage after delay; hp at throw={hp_at_throw}, after={hp_after}"
    )


def test_w_s3_bomb_hits_multiple_enemies():
    """Bomb detonation is AoE — all enemies within radius take damage."""
    world = _world()
    w = make_w(slot="S3")
    w.deployed = True; w.position = (0.0, 1.0); w.atk_cd = 999.0
    world.add_unit(w)

    # Two enemies both within _BOMB_RADIUS
    e1 = _slug(pos=(2, 1), hp=99999)
    e2 = _slug(pos=(2, 2), hp=99999)  # 1 tile away from e1 — both within radius
    world.add_unit(e1)
    world.add_unit(e2)

    w.skill.sp = float(w.skill.sp_cost)
    world.tick()  # S3 fires — target is e1

    hp1_at_throw = e1.hp
    hp2_at_throw = e2.hp

    # Wait for detonation
    for _ in range(int(TICK_RATE * (_BOMB_DELAY + 0.5))):
        world.tick()

    assert e1.hp < hp1_at_throw, "Bomb AoE must hit primary target"
    assert e2.hp < hp2_at_throw, "Bomb AoE must hit nearby enemy within radius"
