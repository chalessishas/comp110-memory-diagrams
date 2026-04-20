"""Pinecone — SNIPER_ARTILLERY: physical primary + Arts AoE splash per hit.

SNIPER_ARTILLERY trait:
  - Physical damage to primary target (reduced by DEF, not RES)
  - After each hit, Arts AoE splash to nearby enemies within _SPLASH_RADIUS tiles
  - Splash is reduced by RES, not DEF

Talent "Blast Shell":
  - Triggers via on_attack_hit
  - Arts splash = 80% of ATK to enemies within 0.9 tiles of target
  - S2 active: radius expands from 0.9 to 1.5 tiles

S2 "Heavy Barrage": 20s duration
  - ATK+30%
  - Splash radius expands to 1.5 tiles (detected by is_s2 flag in talent)

Tests cover:
  - Archetype is SNIPER_ARTILLERY, attack_type=PHYSICAL, block=1
  - Primary attack deals physical damage (reduced by DEF)
  - Primary damage is NOT reduced by RES
  - Splash hits nearby enemy with Arts damage
  - Splash IS reduced by RES
  - Splash does NOT hit enemy beyond base radius (0.9 tiles)
  - S2 ATK+30% applied during skill
  - S2 expands splash radius so enemy at 1.2 tiles is now hit
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, RoleArchetype, AttackType
from core.systems import register_default_systems
from data.characters.pinecone import (
    make_pinecone,
    _ARTS_SPLASH_RATIO, _SPLASH_RADIUS, _S2_SPLASH_RADIUS,
    _S2_ATK_BUFF_TAG, _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(2, 2), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = int(defence); e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and base stats
# ---------------------------------------------------------------------------

def test_pinecone_archetype():
    p = make_pinecone()
    assert p.archetype == RoleArchetype.SNIPER_ARTILLERY
    assert p.attack_type == AttackType.PHYSICAL
    assert p.block == 1


# ---------------------------------------------------------------------------
# Test 2: Primary attack damages enemy (physical, reduced by DEF)
# ---------------------------------------------------------------------------

def test_primary_physical_damage():
    """Primary attack is physical — higher DEF means less damage."""
    w1 = _world()
    p1 = make_pinecone()
    p1.deployed = True; p1.position = (0.0, 2.0)
    p1.atk_cd = 0.0
    w1.add_unit(p1)
    e_lo = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    w1.add_unit(e_lo)
    for _ in range(3):
        w1.tick()
    dmg_no_def = 99999 - e_lo.hp

    w2 = _world()
    p2 = make_pinecone()
    p2.deployed = True; p2.position = (0.0, 2.0)
    p2.atk_cd = 0.0
    w2.add_unit(p2)
    e_hi = _slug(pos=(2, 2), hp=99999, defence=400, res=0)
    w2.add_unit(e_hi)
    for _ in range(3):
        w2.tick()
    dmg_hi_def = 99999 - e_hi.hp

    assert dmg_no_def > 0, "Must deal damage"
    assert dmg_no_def > dmg_hi_def, (
        f"Physical damage must be reduced by DEF; DEF=0:{dmg_no_def}, DEF=400:{dmg_hi_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: Primary damage is NOT reduced by RES
# ---------------------------------------------------------------------------

def test_primary_not_reduced_by_res():
    """Physical primary hit ignores enemy RES."""
    w1 = _world()
    p1 = make_pinecone()
    p1.deployed = True; p1.position = (0.0, 2.0)
    p1.atk_cd = 0.0
    w1.add_unit(p1)
    e_no_res = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    w1.add_unit(e_no_res)
    for _ in range(3):
        w1.tick()
    dmg_no_res = 99999 - e_no_res.hp

    w2 = _world()
    p2 = make_pinecone()
    p2.deployed = True; p2.position = (0.0, 2.0)
    p2.atk_cd = 0.0
    w2.add_unit(p2)
    e_hi_res = _slug(pos=(2, 2), hp=99999, defence=0, res=60)
    w2.add_unit(e_hi_res)
    for _ in range(3):
        w2.tick()
    dmg_hi_res = 99999 - e_hi_res.hp

    assert dmg_no_res > 0
    assert dmg_no_res == dmg_hi_res, (
        f"RES must NOT reduce physical primary; RES=0:{dmg_no_res}, RES=60:{dmg_hi_res}"
    )


# ---------------------------------------------------------------------------
# Test 4: Splash hits nearby enemy with Arts damage
# ---------------------------------------------------------------------------

def test_splash_hits_nearby_with_arts():
    """Secondary enemy within _SPLASH_RADIUS takes Arts damage from Blast Shell."""
    w = _world()
    p = make_pinecone()
    p.deployed = True; p.position = (0.0, 2.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    primary = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    # Nearby secondary (distance=0 tiles — same position) within 0.9 radius
    secondary = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    w.add_unit(primary); w.add_unit(secondary)

    for _ in range(3):
        w.tick()

    assert secondary.hp < 99999, (
        f"Nearby enemy must take Arts splash damage; hp={secondary.hp}"
    )


# ---------------------------------------------------------------------------
# Test 5: Splash IS reduced by enemy RES
# ---------------------------------------------------------------------------

def test_splash_reduced_by_res():
    """Arts splash damage is mitigated by enemy RES."""
    w1 = _world()
    p1 = make_pinecone()
    p1.deployed = True; p1.position = (0.0, 2.0)
    p1.atk_cd = 0.0
    w1.add_unit(p1)
    primary1 = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    splash1 = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    w1.add_unit(primary1); w1.add_unit(splash1)
    w1.tick()
    splash_dmg_no_res = 99999 - splash1.hp

    w2 = _world()
    p2 = make_pinecone()
    p2.deployed = True; p2.position = (0.0, 2.0)
    p2.atk_cd = 0.0
    w2.add_unit(p2)
    primary2 = _slug(pos=(2, 2), hp=99999, defence=0, res=0)
    splash2 = _slug(pos=(2, 2), hp=99999, defence=0, res=50)
    w2.add_unit(primary2); w2.add_unit(splash2)
    w2.tick()
    splash_dmg_hi_res = 99999 - splash2.hp

    assert splash_dmg_no_res > 0, "Must have splash damage"
    assert splash_dmg_no_res > splash_dmg_hi_res, (
        f"Arts splash must be reduced by RES; RES=0:{splash_dmg_no_res}, RES=50:{splash_dmg_hi_res}"
    )


# ---------------------------------------------------------------------------
# Test 6: Enemy beyond base radius is NOT hit by splash
# ---------------------------------------------------------------------------

def test_splash_does_not_hit_beyond_base_radius():
    """Enemy at 2.0 tiles from primary must not take splash damage (outside 0.9 radius)."""
    w = _world()
    p = make_pinecone()
    p.deployed = True; p.position = (0.0, 2.0)
    p.atk_cd = 0.0
    w.add_unit(p)

    primary = _slug(pos=(2, 2), hp=99999)
    far_enemy = _slug(pos=(4, 2), hp=99999)  # 2.0 tiles from primary — outside 0.9
    w.add_unit(primary); w.add_unit(far_enemy)

    for _ in range(3):
        w.tick()

    assert far_enemy.hp == 99999, (
        f"Enemy 2.0 tiles from primary must NOT be splashed; hp={far_enemy.hp}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 applies ATK+30%
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """During S2, effective_atk must be base × 1.3."""
    w = _world()
    p = make_pinecone()
    p.deployed = True; p.position = (0.0, 2.0)
    w.add_unit(p)
    e = _slug(pos=(2, 2))
    w.add_unit(e)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(p.effective_atk - expected) <= 2, (
        f"ATK must be base×{1+_S2_ATK_RATIO}; base={base_atk}, expected={expected}, got={p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 expands splash radius — enemy at 1.2 tiles is now hit
# ---------------------------------------------------------------------------

def test_s2_expands_splash_radius():
    """During S2, enemy at 1.2 tiles (outside base 0.9, inside S2 1.5) must be splashed."""
    w = _world()
    p = make_pinecone()
    p.deployed = True; p.position = (0.0, 2.0)
    w.add_unit(p)

    primary = _slug(pos=(2, 2), hp=99999)
    # Place secondary at x=3.2, y=2.0 → distance from primary (2,2) = sqrt((3.2-2)^2) = 1.2
    # But since we can only use integer-path slugs, use the approach:
    # primary at (2,2), secondary at (3,2) — distance exactly 1.0 tile
    # 1.0 > 0.9 (base radius) so not hit normally, but 1.0 < 1.5 (S2 radius) so hit during S2
    secondary = _slug(pos=(3, 2), hp=99999)
    w.add_unit(primary); w.add_unit(secondary)

    # Verify secondary NOT hit with base radius (before S2)
    p.atk_cd = 0.0
    initial_hp = secondary.hp
    w.tick()
    assert secondary.hp == initial_hp, (
        f"Secondary at 1.0 tile must NOT be hit with base {_SPLASH_RADIUS} radius; hp={secondary.hp}"
    )

    # Activate S2 — radius expands to 1.5
    secondary.hp = 99999
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()  # S2 activates
    assert p.skill.active_remaining > 0.0

    p.atk_cd = 0.0
    secondary.hp = 99999
    w.tick()  # attack with S2 active

    assert secondary.hp < 99999, (
        f"During S2, enemy at 1.0 tile (< {_S2_SPLASH_RADIUS} radius) must be splashed; hp={secondary.hp}"
    )
