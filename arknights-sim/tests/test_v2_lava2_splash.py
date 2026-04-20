"""Lava the Purgatory — CASTER_SPLASH: AoE damage radius around primary target.

CASTER_SPLASH trait:
  - splash_radius = 0.8 tiles (always active, even without skill)
  - All enemies within 0.8 tiles of primary target take full Arts damage
  - S2 "Scorched Earth": radius expands to 1.5 tiles + ATK+30% for 25s

Tests cover:
  - Archetype is CASTER_SPLASH and splash_radius > 0 on deploy
  - Attack damages primary target
  - Secondary enemy within splash radius is hit
  - Enemy outside splash radius is NOT hit
  - Talent "Thermal Conduction": ATK buff when 2+ enemies in range
  - Talent buff removed when enemies drop below threshold
  - S2 increases splash_radius from 0.8 to 1.5
  - S2 ATK buff active during skill; reverts after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, RoleArchetype
from core.systems import register_default_systems
from data.characters.lava2 import (
    make_lava2,
    _TRAIT_SPLASH_RADIUS, _S2_SPLASH_RADIUS,
    _TALENT_BUFF_TAG, _TALENT_ATK_RATIO,
    _S2_ATK_RATIO, _S2_ATK_BUFF_TAG, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and splash_radius on deploy
# ---------------------------------------------------------------------------

def test_lava2_archetype_and_splash():
    lava = make_lava2()
    assert lava.archetype == RoleArchetype.CASTER_SPLASH
    assert lava.splash_radius == _TRAIT_SPLASH_RADIUS, (
        f"splash_radius must be {_TRAIT_SPLASH_RADIUS} on deploy; got {lava.splash_radius}"
    )
    assert lava.splash_radius > 0.0, "Splash radius must be positive (trait is always on)"


# ---------------------------------------------------------------------------
# Test 2: Attack damages the primary target
# ---------------------------------------------------------------------------

def test_attack_damages_primary_target():
    """Lava deals Arts damage to the primary target."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    lava.atk_cd = 0.0
    w.add_unit(lava)

    enemy = _slug(pos=(2, 2), hp=9999, res=0)
    initial_hp = enemy.hp
    w.add_unit(enemy)

    for _ in range(3):
        w.tick()

    assert enemy.hp < initial_hp, (
        f"Primary target must take Arts damage; was {initial_hp}, now {enemy.hp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Secondary enemy within splash radius is hit
# ---------------------------------------------------------------------------

def test_splash_hits_nearby_enemy():
    """An enemy within splash_radius tiles of the primary target also takes damage."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    lava.atk_cd = 0.0
    w.add_unit(lava)

    primary = _slug(pos=(2, 2), hp=9999, res=0)
    # Secondary enemy at same tile (distance=0 < 0.8 radius) — path consistent
    secondary = _slug(pos=(2, 2), hp=9999, res=0)
    initial_primary = primary.hp
    initial_secondary = secondary.hp
    w.add_unit(primary); w.add_unit(secondary)

    for _ in range(3):
        w.tick()

    assert primary.hp < initial_primary, "Primary must take damage"
    assert secondary.hp < initial_secondary, (
        f"Secondary enemy within {_TRAIT_SPLASH_RADIUS} tiles must also take splash damage; "
        f"was {initial_secondary}, now {secondary.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: Enemy outside splash radius is NOT hit
# ---------------------------------------------------------------------------

def test_splash_does_not_hit_far_enemy():
    """Enemies more than splash_radius tiles from the target are unaffected."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    lava.atk_cd = 0.0
    w.add_unit(lava)

    primary = _slug(pos=(2, 2), hp=9999, res=0)
    # Far enemy 2 tiles away (outside 0.8 radius)
    far = _slug(hp=9999, res=0)
    far.position = (4.0, 2.0)  # 2.0 tiles from primary — outside splash
    far.deployed = True
    initial_far = far.hp
    w.add_unit(primary); w.add_unit(far)

    for _ in range(3):
        w.tick()

    assert far.hp == initial_far, (
        f"Enemy 2 tiles away must NOT take splash damage; was {initial_far}, now {far.hp}"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent ATK buff activates when 2+ enemies in range
# ---------------------------------------------------------------------------

def test_talent_atk_buff_with_two_enemies():
    """Thermal Conduction: ATK+20% when 2+ enemies are within attack range."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    base_atk = lava.effective_atk
    w.add_unit(lava)

    # Two enemies in Lava's attack range
    e1 = _slug(pos=(2, 2))
    e2 = _slug(pos=(3, 2))
    w.add_unit(e1); w.add_unit(e2)

    for _ in range(3):
        w.tick()

    talent_buffs = [b for b in lava.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(talent_buffs) == 1, f"Thermal Conduction buff must be active; buffs={[b.source_tag for b in lava.buffs]}"
    expected_atk = int(base_atk * (1 + _TALENT_ATK_RATIO))
    assert abs(lava.effective_atk - expected_atk) <= 2, (
        f"ATK must be base×{1+_TALENT_ATK_RATIO}; base={base_atk}, expected={expected_atk}, got={lava.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: Talent buff removed when enemies drop below threshold
# ---------------------------------------------------------------------------

def test_talent_buff_removed_below_threshold():
    """Thermal Conduction buff is removed when fewer than 2 enemies are in range."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    w.add_unit(lava)

    e1 = _slug(pos=(2, 2))
    e2 = _slug(pos=(3, 2))
    w.add_unit(e1); w.add_unit(e2)

    # Let talent activate
    for _ in range(3):
        w.tick()
    assert any(b.source_tag == _TALENT_BUFF_TAG for b in lava.buffs), "Buff must be active"

    # Kill both enemies — world.enemies() will no longer return them
    e1.alive = False
    e2.alive = False

    for _ in range(3):
        w.tick()

    assert not any(b.source_tag == _TALENT_BUFF_TAG for b in lava.buffs), (
        "Thermal Conduction buff must be removed when enemies leave range"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 increases splash_radius to 1.5 tiles
# ---------------------------------------------------------------------------

def test_s2_increases_splash_radius():
    """After S2 activates, splash_radius must expand to _S2_SPLASH_RADIUS."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    w.add_unit(lava)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    assert lava.splash_radius == _TRAIT_SPLASH_RADIUS, "Must start at base radius"

    # Activate S2
    lava.skill.sp = float(lava.skill.sp_cost)
    w.tick()

    assert lava.skill.active_remaining > 0.0, "S2 must be active"
    assert lava.splash_radius == _S2_SPLASH_RADIUS, (
        f"splash_radius must expand to {_S2_SPLASH_RADIUS} during S2; got {lava.splash_radius}"
    )

    # After S2 ends, radius returns
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert lava.splash_radius == _TRAIT_SPLASH_RADIUS, (
        f"splash_radius must return to {_TRAIT_SPLASH_RADIUS} after S2; got {lava.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK+30% buff active during skill, removed after
# ---------------------------------------------------------------------------

def test_s2_atk_buff_active_and_reverts():
    """S2 applies ATK+30% that reverts when skill ends."""
    w = _world()
    lava = make_lava2()
    lava.deployed = True; lava.position = (0.0, 2.0)
    w.add_unit(lava)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    base_atk = lava.effective_atk

    lava.skill.sp = float(lava.skill.sp_cost)
    w.tick()
    assert lava.skill.active_remaining > 0.0, "S2 must be active"

    expected_s2_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(lava.effective_atk - expected_s2_atk) <= 2, (
        f"ATK during S2 must be base×{1+_S2_ATK_RATIO}; base={base_atk}, "
        f"expected={expected_s2_atk}, got={lava.effective_atk}"
    )

    # Wait for S2 to end
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert lava.skill.active_remaining == 0.0, "S2 must have ended"
    s2_buffs = [b for b in lava.buffs if b.source_tag == _S2_ATK_BUFF_TAG]
    assert len(s2_buffs) == 0, f"S2 ATK buff must be removed after skill ends"
    # ATK returns to base (or thermal buff if enemies still in range)
    assert lava.effective_atk <= int(base_atk * 1.22), (
        f"ATK must revert close to base after S2; base={base_atk}, got={lava.effective_atk}"
    )
