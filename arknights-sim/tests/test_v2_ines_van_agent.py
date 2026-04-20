"""Ines — VAN_AGENT: CAMOUFLAGE on deploy + talent SILENCE + S3 AoE physical + re-CAMO.

VAN_AGENT trait: On deployment, Ines gains CAMOUFLAGE so enemies cannot target her.

Talent "Quiet Visitor": On deployment, all enemies within 4 Manhattan tiles are
  silenced for 6 seconds.

S3 "Obedient Strings": MANUAL, instant.
  Deals 200% ATK physical damage to all in-range enemies.
  Silences each hit enemy for 8s, then Ines regains CAMOUFLAGE for 20s.

Tests cover:
  - Archetype is VAN_AGENT
  - On deploy, Ines gains CAMOUFLAGE status
  - During CAMOUFLAGE, enemies do NOT target Ines
  - CAMOUFLAGE expires after duration
  - Talent silences nearby enemies on deploy
  - Talent does NOT silence out-of-range enemies
  - S3 deals physical damage to in-range enemies
  - S3 silences all in-range enemies
  - S3 grants Ines CAMOUFLAGE after activation
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype, Faction, AttackType
from core.systems import register_default_systems
from data.characters.ines import (
    make_ines,
    _TALENT_TAG, _TALENT_SILENCE_DURATION, _TALENT_SILENCE_TAG, _TALENT_RANGE,
    _CAMO_DURATION, _CAMO_TAG,
    _S3_SILENCE_DURATION, _S3_SILENCE_TAG, _S3_CAMO_DURATION, _S3_ATK_RATIO,
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


def _slug(pos=(1, 1), hp=99999, defence=0, atk=100) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk
    e.defence = defence; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype is VAN_AGENT
# ---------------------------------------------------------------------------

def test_ines_archetype():
    i = make_ines()
    assert i.archetype == RoleArchetype.VAN_AGENT
    assert len(i.talents) == 1
    assert i.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: On deploy, Ines gains CAMOUFLAGE
# ---------------------------------------------------------------------------

def test_deploy_grants_camouflage():
    """When Ines is added to the world, she must immediately have CAMOUFLAGE."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    assert i.has_status(StatusKind.CAMOUFLAGE), "Ines must have CAMOUFLAGE after deployment"
    camo = next(s for s in i.statuses if s.kind == StatusKind.CAMOUFLAGE)
    assert camo.source_tag == _CAMO_TAG


# ---------------------------------------------------------------------------
# Test 3: During CAMOUFLAGE, enemies do NOT target Ines
# ---------------------------------------------------------------------------

def test_camouflage_prevents_targeting():
    """While Ines has CAMOUFLAGE, enemies with ATK must NOT attack her."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    # Enemy that would normally attack operators in range
    attacker = _slug(pos=(1, 1), hp=99999, atk=500)
    w.add_unit(attacker)

    initial_hp = i.hp
    for _ in range(TICK_RATE * 3):
        w.tick()

    assert i.has_status(StatusKind.CAMOUFLAGE), "CAMOUFLAGE must still be active"
    assert i.hp == initial_hp, (
        f"Enemy must not attack camo-Ines; hp changed from {initial_hp} to {i.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: CAMOUFLAGE expires after duration
# ---------------------------------------------------------------------------

def test_camouflage_expires():
    """CAMOUFLAGE must expire after _CAMO_DURATION seconds."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    assert i.has_status(StatusKind.CAMOUFLAGE), "CAMOUFLAGE must be present initially"

    for _ in range(int(TICK_RATE * (_CAMO_DURATION + 1))):
        w.tick()

    assert not i.has_status(StatusKind.CAMOUFLAGE), (
        f"CAMOUFLAGE must expire after {_CAMO_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent silences nearby enemies on deploy
# ---------------------------------------------------------------------------

def test_talent_silences_nearby_on_deploy():
    """Quiet Visitor must apply SILENCE to enemies within range on deployment."""
    w = _world()
    # Add enemy before Ines — on_battle_start fires when Ines is added
    enemy = _slug(pos=(2, 1), hp=99999)
    w.add_unit(enemy)

    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    assert enemy.has_status(StatusKind.SILENCE), "Nearby enemy must be silenced on Ines deploy"
    silence = next(s for s in enemy.statuses if s.kind == StatusKind.SILENCE)
    assert silence.source_tag == _TALENT_SILENCE_TAG


# ---------------------------------------------------------------------------
# Test 6: Talent does NOT silence out-of-range enemies
# ---------------------------------------------------------------------------

def test_talent_no_silence_out_of_range():
    """Enemies beyond _TALENT_RANGE Manhattan tiles must not be silenced."""
    w = _world()
    far_enemy = _slug(pos=(7, 1), hp=99999)  # 7 Manhattan tiles away
    w.add_unit(far_enemy)

    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    assert not far_enemy.has_status(StatusKind.SILENCE), (
        "Out-of-range enemy must NOT be silenced by Quiet Visitor"
    )


# ---------------------------------------------------------------------------
# Test 7: S3 deals physical damage to in-range enemies
# ---------------------------------------------------------------------------

def test_s3_physical_damage_in_range():
    """S3 Obedient Strings must deal 200% ATK physical damage to in-range enemies."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    enemy = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(enemy)

    pre_hp = enemy.hp
    i.skill.sp = float(i.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, i)

    assert enemy.hp < pre_hp, "S3 must deal physical damage to in-range enemy"
    # Verify damage is approximately 200% ATK (defence=0)
    damage = pre_hp - enemy.hp
    expected = int(i.effective_atk * _S3_ATK_RATIO)
    assert abs(damage - expected) <= 2, (
        f"S3 damage must be ~{expected} (200% ATK); got {damage}"
    )


# ---------------------------------------------------------------------------
# Test 8: S3 silences in-range enemies
# ---------------------------------------------------------------------------

def test_s3_silences_in_range():
    """S3 must apply SILENCE to all hit enemies."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    i.skill.sp = float(i.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, i)

    assert enemy.has_status(StatusKind.SILENCE), "S3 must silence in-range enemy"
    silence = next(s for s in enemy.statuses if s.kind == StatusKind.SILENCE)
    assert silence.source_tag == _S3_SILENCE_TAG


# ---------------------------------------------------------------------------
# Test 9: S3 grants Ines CAMOUFLAGE after activation
# ---------------------------------------------------------------------------

def test_s3_regrants_camouflage():
    """After S3 fires, Ines must have CAMOUFLAGE again."""
    w = _world()
    i = make_ines()
    i.deployed = True; i.position = (0.0, 1.0)
    w.add_unit(i)

    # Let deploy CAMOUFLAGE expire first so we know the S3 granted a fresh one
    for _ in range(int(TICK_RATE * (_CAMO_DURATION + 1))):
        w.tick()
    assert not i.has_status(StatusKind.CAMOUFLAGE), "Deploy CAMOUFLAGE must have expired"

    i.skill.sp = float(i.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, i)

    assert i.has_status(StatusKind.CAMOUFLAGE), "S3 must grant Ines CAMOUFLAGE after activation"
    camo = next(s for s in i.statuses if s.kind == StatusKind.CAMOUFLAGE)
    expected_expiry = w.global_state.elapsed + _S3_CAMO_DURATION
    assert abs(camo.expires_at - expected_expiry) < 1.0, (
        f"S3 CAMOUFLAGE duration must be ~{_S3_CAMO_DURATION}s"
    )
