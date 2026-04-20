"""Hellagur S3 'Iron Will' — ATK+250%, HP drain, post-skill DAMAGE_IMMUNE."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.hellagur import (
    make_hellagur,
    _S3_ATK_RATIO, _S3_DURATION, _S3_HP_DRAIN, _S3_IMMUNE_DURATION,
)
from data.enemies import make_originium_slug


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 1), hp=999999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.defence = defence
    e.atk = 0; e.move_speed = 0.0
    return e


def _fire_s3(world: World, h: UnitState) -> None:
    """Set SP to max and tick once to fire S3."""
    h.skill.sp = float(h.skill.sp_cost)
    world.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    h = make_hellagur("S3")
    sk = h.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 35
    assert sk.duration == 35.0
    assert sk.requires_target is True


# ---------------------------------------------------------------------------
# Test 2: S3 grants ATK+250% buff while active
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """Iron Will: ATK must be (base × 3.50) while skill is active."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    base_atk = h.effective_atk
    _fire_s3(w, h)

    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert h.effective_atk == expected, (
        f"S3 ATK must be {expected}; got {h.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: HP drains each tick during S3
# ---------------------------------------------------------------------------

def test_s3_drains_hp_per_tick():
    """HP must decrease by approximately _S3_HP_DRAIN/s every tick."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = h.max_hp   # start full
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    _fire_s3(w, h)   # skill fires, first on_tick also runs
    hp_after_fire = h.hp

    w.tick()  # one more tick of drain
    assert h.hp < hp_after_fire, (
        f"HP must drain during S3; was {hp_after_fire}, now {h.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: HP drain cannot drop HP below 1
# ---------------------------------------------------------------------------

def test_s3_hp_floor_at_one():
    """HP drain must never reduce Hellagur below 1 HP."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = 2   # near death — on_tick drain should floor at 1
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    _fire_s3(w, h)  # tick 1: skill fires (on_tick not yet called)
    w.tick()        # tick 2: on_tick drains → hp floored at 1

    assert h.hp >= 1, f"HP must never drop below 1 from drain; hp={h.hp}"
    assert h.alive, "Hellagur must still be alive after HP floor"


# ---------------------------------------------------------------------------
# Test 5: S3 terminates early when HP hits floor
# ---------------------------------------------------------------------------

def test_s3_early_terminate_on_hp_floor():
    """When HP reaches 1 mid-skill, active_remaining is forced to 0 and on_end fires."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = 2   # will hit floor on first on_tick drain
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    _fire_s3(w, h)  # tick 1: skill fires, active_remaining = 35.0
    w.tick()        # tick 2: on_tick drains → hp=1 → active_remaining forced to 0 → on_end fires

    assert h.skill.active_remaining == 0.0, (
        "Skill must end early when HP floor is hit"
    )
    # on_end grants DAMAGE_IMMUNE
    assert h.has_status(StatusKind.DAMAGE_IMMUNE), (
        "DAMAGE_IMMUNE must be granted when skill ends early via HP floor"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 grants DAMAGE_IMMUNE on natural end
# ---------------------------------------------------------------------------

def test_s3_immune_on_natural_end():
    """At natural skill expiry, Hellagur gains DAMAGE_IMMUNE for _S3_IMMUNE_DURATION."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = h.max_hp
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    _fire_s3(w, h)

    # Run through skill duration (drain won't kill because max_hp=4225, drain~55/s for 35s=1925 total)
    for _ in range(int(TICK_RATE * _S3_DURATION)):
        w.tick()

    assert h.skill.active_remaining == 0.0, "Skill must have expired"
    assert h.has_status(StatusKind.DAMAGE_IMMUNE), (
        "DAMAGE_IMMUNE must be granted after natural S3 expiry"
    )


# ---------------------------------------------------------------------------
# Test 7: ATK buff removed after S3 ends
# ---------------------------------------------------------------------------

def test_s3_atk_buff_removed_on_end():
    """After S3 expires, effective_atk returns to base."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = h.max_hp
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    base_atk = h.effective_atk
    _fire_s3(w, h)
    assert h.effective_atk > base_atk, "Buff must be active"

    for _ in range(int(TICK_RATE * _S3_DURATION)):
        w.tick()

    assert h.effective_atk == base_atk, (
        f"ATK must revert after S3; expected {base_atk}, got {h.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: DAMAGE_IMMUNE blocks incoming damage after S3 ends
# ---------------------------------------------------------------------------

def test_s3_immune_blocks_damage():
    """The post-skill DAMAGE_IMMUNE window must absorb all incoming damage."""
    w = _world()
    h = make_hellagur("S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.hp = 2   # triggers early end on second tick
    w.add_unit(h)
    enemy = _slug()
    w.add_unit(enemy)

    _fire_s3(w, h)  # tick 1: skill fires
    w.tick()        # tick 2: drain → hp=1 → early end → DAMAGE_IMMUNE applied

    hp_after_immune = h.hp
    absorbed = h.take_damage(9999)
    assert absorbed == 0, f"DAMAGE_IMMUNE must absorb all damage; absorbed={absorbed}"
    assert h.hp == hp_after_immune, "HP must not change during DAMAGE_IMMUNE"
