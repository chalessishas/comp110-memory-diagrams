"""Eyjafjalla S3 "Pyroclastic Eruption" — ATK+220%, AoE radius 2.0, TRUE damage, 50s.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, requires_target)
  - ATK +220% during S3
  - splash_radius set to 2.0 during S3
  - attack_type converts to TRUE during S3
  - Wide AoE hits enemies at r>1.3 (beyond S2 splash)
  - ATK buff + splash_radius + attack_type reverted on end
  - S2 regression (Volcanic Activity unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, AttackType, SkillTrigger
from core.systems import register_default_systems
from data.characters.eyjafjalla import (
    make_eyjafjalla,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_SPLASH_RADIUS,
    _S2_SPLASH_RADIUS,
)
from data.enemies import make_originium_slug


def _world(w: int = 8, h: int = 5) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _slug(pos, hp: int = 99999):
    path = [(int(pos[0]), int(pos[1]))] * 30
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.defence = 0; e.res = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    eyja = make_eyjafjalla(slot="S3")
    sk = eyja.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Pyroclastic Eruption"
    assert sk.sp_cost == 60
    assert sk.initial_sp == 15
    assert sk.duration == 50.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is True
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +220% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    base_atk = eyja.effective_atk
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    slug = _slug((2, 2))
    w.add_unit(slug)

    eyja.skill.sp = float(eyja.skill.sp_cost)
    w.tick()

    assert eyja.skill.active_remaining > 0.0, "S3 must be active after sp full + enemy present"
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(eyja.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {eyja.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: splash_radius set to 2.0 during S3
# ---------------------------------------------------------------------------

def test_s3_splash_radius():
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    assert eyja.splash_radius == 0.0, "Base splash radius must be 0"
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    slug = _slug((2, 2))
    w.add_unit(slug)

    eyja.skill.sp = float(eyja.skill.sp_cost)
    w.tick()

    assert eyja.splash_radius == _S3_SPLASH_RADIUS, (
        f"S3 splash_radius must be {_S3_SPLASH_RADIUS}; got {eyja.splash_radius}"
    )
    assert _S3_SPLASH_RADIUS > _S2_SPLASH_RADIUS, "S3 splash must exceed S2 splash"


# ---------------------------------------------------------------------------
# Test 4: attack_type converts to TRUE during S3
# ---------------------------------------------------------------------------

def test_s3_true_damage_type():
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    slug = _slug((2, 2))
    w.add_unit(slug)

    eyja.skill.sp = float(eyja.skill.sp_cost)
    w.tick()

    assert eyja.attack_type == AttackType.TRUE, "S3 must convert attack_type to TRUE"


# ---------------------------------------------------------------------------
# Test 5: Wide AoE hits enemy at r>1.3 (beyond S2 splash)
# ---------------------------------------------------------------------------

def test_s3_wide_aoe_hits_far_enemy():
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 0.0
    w.add_unit(eyja)

    primary = _slug((2, 2))
    # Distance from primary (2,2) to (3.7, 2) ≈ 1.7, within r=2.0 but beyond r=1.3
    far_enemy = _slug((3, 2))
    far_enemy.position = (3.7, 2.0)
    w.add_unit(primary)
    w.add_unit(far_enemy)

    hp_before = far_enemy.hp
    eyja.skill.sp = float(eyja.skill.sp_cost)
    _ticks(w, 3.0)

    assert far_enemy.hp < hp_before, (
        "S3 wide AoE (r=2.0) must damage enemy at distance >1.3 from primary"
    )


# ---------------------------------------------------------------------------
# Test 6: ATK buff, splash_radius, and attack_type reverted on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    eyja = make_eyjafjalla(slot="S3")
    base_atk = eyja.effective_atk
    eyja.deployed = True; eyja.position = (0.0, 2.0); eyja.atk_cd = 999.0
    w.add_unit(eyja)

    slug = _slug((2, 2))
    w.add_unit(slug)

    eyja.skill.sp = float(eyja.skill.sp_cost)
    _ticks(w, 52.0)  # 50s duration + buffer

    assert eyja.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in eyja.buffs), "S3 ATK buff must be cleared"
    assert eyja.splash_radius == 0.0, "splash_radius must revert to 0"
    assert eyja.attack_type == AttackType.ARTS, "attack_type must revert to ARTS"
    assert abs(eyja.effective_atk - base_atk) <= 2, "ATK must revert to base"


# ---------------------------------------------------------------------------
# Test 7: S2 regression (Volcanic Activity unchanged)
# ---------------------------------------------------------------------------

def test_s2_regression():
    eyja = make_eyjafjalla(slot="S2")
    sk = eyja.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Volcanic Activity"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
