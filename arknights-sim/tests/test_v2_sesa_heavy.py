"""Sesa — SNIPER_HEAVY: SLOW trait + Percussion Resonance every-7-hits Arts + S2 ATK buff.

SNIPER_HEAVY trait: Attacks slow enemy movement by 30% for 0.5s.

Talent "Percussion Resonance": Every 7 attacks, deal 150% ATK Arts damage to enemies
  within 1.2 tiles of the primary target.

S2 "Drumroll": ATK +80% for 20s.

Tests cover:
  - Archetype is SNIPER_HEAVY
  - Trait applies SLOW status on attack hit
  - Talent does NOT fire on hits 1-6
  - Talent fires Arts explosion on 7th hit
  - Talent fires again on 14th hit (every-7 cycle)
  - Talent Arts explosion hits adjacent enemy within radius
  - S2 increases ATK by 80%
  - S2 ATK buff removed after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.sesa import (
    make_sesa,
    _TRAIT_TAG, _TRAIT_SLOW_AMOUNT, _TRAIT_SLOW_DURATION,
    _TALENT_TAG, _TALENT_HIT_COUNT, _TALENT_BONUS_ATK_RATIO, _TALENT_RADIUS,
    _S2_ATK_RATIO, _S2_DURATION,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(3, 1), hp=99999, defence=0, res=0.0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = res
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _deploy_sesa(w: World) -> UnitState:
    op = make_sesa()
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 0.0
    w.add_unit(op)
    return op


# ---------------------------------------------------------------------------
# Test 1: Archetype SNIPER_HEAVY
# ---------------------------------------------------------------------------

def test_sesa_archetype():
    s = make_sesa()
    assert s.archetype == RoleArchetype.SNIPER_HEAVY
    assert s.block == 1


# ---------------------------------------------------------------------------
# Test 2: Trait applies SLOW on attack hit
# ---------------------------------------------------------------------------

def test_trait_applies_slow_on_hit():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1))
    w.add_unit(enemy)

    w.tick()   # Sesa attacks with atk_cd=0

    assert enemy.has_status(StatusKind.SLOW), (
        "SNIPER_HEAVY trait must apply SLOW to hit enemy"
    )
    slow = next(st for st in enemy.statuses if st.kind == StatusKind.SLOW)
    assert slow.params["amount"] == _TRAIT_SLOW_AMOUNT


# ---------------------------------------------------------------------------
# Test 3: Talent does NOT fire on hits 1-6
# ---------------------------------------------------------------------------

def test_talent_does_not_fire_before_7th_hit():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1), hp=99999, res=0.0)
    w.add_unit(enemy)

    initial_hp = enemy.hp
    # Fire 6 hits via the talent registry directly (pure arts only, no physical)
    for _ in range(_TALENT_HIT_COUNT - 1):
        fire_on_attack_hit(w, s, enemy, 0)
    hit_hp = enemy.hp

    assert hit_hp == initial_hp, (
        f"Percussion Resonance must not fire before {_TALENT_HIT_COUNT} hits"
    )


# ---------------------------------------------------------------------------
# Test 4: Talent fires Arts explosion on 7th hit
# ---------------------------------------------------------------------------

def test_talent_fires_on_7th_hit():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1), hp=99999, res=0.0)
    w.add_unit(enemy)

    initial_hp = enemy.hp
    for _ in range(_TALENT_HIT_COUNT):
        fire_on_attack_hit(w, s, enemy, 0)

    assert enemy.hp < initial_hp, (
        f"Percussion Resonance must deal Arts damage on hit #{_TALENT_HIT_COUNT}"
    )
    expected_min_dmg = int(s.effective_atk * _TALENT_BONUS_ATK_RATIO)
    damage_dealt = initial_hp - enemy.hp
    assert damage_dealt >= expected_min_dmg - 5, (
        f"Arts damage should be ~{expected_min_dmg}; got {damage_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent fires again on 14th hit
# ---------------------------------------------------------------------------

def test_talent_fires_again_on_14th_hit():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1), hp=99999, res=0.0)
    w.add_unit(enemy)

    # 7th hit fires first explosion
    for _ in range(_TALENT_HIT_COUNT):
        fire_on_attack_hit(w, s, enemy, 0)
    hp_after_7 = enemy.hp

    # hits 8-13: no explosion
    for _ in range(_TALENT_HIT_COUNT - 1):
        fire_on_attack_hit(w, s, enemy, 0)
    hp_before_14 = enemy.hp

    # 14th hit: second explosion
    fire_on_attack_hit(w, s, enemy, 0)
    hp_after_14 = enemy.hp

    assert hp_after_14 < hp_before_14, (
        f"Percussion Resonance must fire again on hit #{_TALENT_HIT_COUNT * 2}"
    )


# ---------------------------------------------------------------------------
# Test 6: Talent Arts explosion hits adjacent enemy within radius
# ---------------------------------------------------------------------------

def test_talent_arts_hits_adjacent_enemy():
    w = _world()
    s = _deploy_sesa(w)
    primary = _slug(pos=(2, 1), hp=99999, res=0.0)
    adjacent = _slug(pos=(2, 2), hp=99999, res=0.0)  # 1 tile from primary — within 1.2 radius
    w.add_unit(primary)
    w.add_unit(adjacent)

    primary_initial_hp = primary.hp
    adjacent_initial_hp = adjacent.hp

    for _ in range(_TALENT_HIT_COUNT):
        fire_on_attack_hit(w, s, primary, 0)

    assert primary.hp < primary_initial_hp, "Primary must take Arts damage"
    assert adjacent.hp < adjacent_initial_hp, (
        f"Adjacent enemy within {_TALENT_RADIUS} tiles must also take Arts damage"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 increases ATK by 80%
# ---------------------------------------------------------------------------

def test_s2_increases_atk():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1))
    w.add_unit(enemy)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert s.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(s.effective_atk - expected_atk) <= 2, (
        f"S2 must give ATK ×{1 + _S2_ATK_RATIO}; expected={expected_atk}, got={s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed after skill ends
# ---------------------------------------------------------------------------

def test_s2_atk_buff_removed_on_end():
    w = _world()
    s = _deploy_sesa(w)
    enemy = _slug(pos=(2, 1))
    w.add_unit(enemy)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert s.skill.active_remaining == 0.0, "S2 must have ended"
    assert abs(s.effective_atk - base_atk) <= 2, (
        f"ATK must return to base after S2; expected={base_atk}, got={s.effective_atk}"
    )
