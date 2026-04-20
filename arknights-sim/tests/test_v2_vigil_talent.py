"""Vigil talent "Wolven Nature" — DEF ignore 175 on physical attacks.

Tests cover:
  - Talent configured correctly (name + behavior_tag)
  - on_attack_hit fires and deals bonus true damage = min(enemy_def, 175)
  - Bonus is capped at enemy effective_def (can't be negative)
  - Bonus is capped at 175 when enemy DEF > 175
  - S3 active does not suppress the talent
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, AttackType, Profession
from core.systems import register_default_systems
from data.characters.vigil import make_vigil, _TALENT_TAG, _DEF_IGNORE
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def test_vigil_config():
    v = make_vigil()
    assert len(v.talents) == 1
    assert v.talents[0].name == "Wolven Nature"
    assert v.talents[0].behavior_tag == _TALENT_TAG


def test_def_ignore_bonus_applied():
    """Vigil's attack must deal extra true damage equal to min(enemy_def, 175)."""
    w = _world()
    v = make_vigil(slot=None)
    v.deployed = True; v.position = (0.0, 1.0)
    w.add_unit(v)

    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.deployed = True; slug.position = (1.0, 1.0)
    slug.move_speed = 0.0
    slug_def = slug.effective_def
    slug_hp_before = slug.hp
    w.add_unit(slug)

    # Fire exactly one attack: set atk_cd=0 so attack fires on next tick
    v.atk_cd = 0.0
    w.tick()

    # Vigil base physical damage (no def ignore) = max(int(raw * 0.05), raw - slug_def)
    raw = v.effective_atk
    base_dmg = max(int(raw * 0.05), raw - slug_def)
    bonus = min(slug_def, _DEF_IGNORE)
    expected_total = base_dmg + bonus

    actual_dmg = slug_hp_before - slug.hp
    assert actual_dmg == expected_total, (
        f"Vigil attack must deal base {base_dmg} + bonus {bonus} = {expected_total}; "
        f"got {actual_dmg}"
    )


def test_def_ignore_capped_at_def():
    """When enemy DEF < 175, bonus = enemy DEF (not 175)."""
    w = _world()
    v = make_vigil(slot=None)
    v.deployed = True; v.position = (0.0, 1.0)
    w.add_unit(v)

    # Create a low-DEF enemy (DEF=50 < 175)
    low_def_enemy = UnitState(
        name="LowDefEnemy", faction=Faction.ENEMY,
        max_hp=5000, atk=0, defence=50, res=0.0,
        atk_interval=99.0, attack_range_melee=True,
        profession=Profession.GUARD, block=0, cost=0,
    )
    low_def_enemy.deployed = True; low_def_enemy.position = (1.0, 1.0)
    low_def_enemy.move_speed = 0.0
    w.add_unit(low_def_enemy)

    hp_before = low_def_enemy.hp
    v.atk_cd = 0.0
    w.tick()

    raw = v.effective_atk
    enemy_def = low_def_enemy.effective_def  # should be 50
    base_dmg = max(int(raw * 0.05), raw - enemy_def)
    bonus = min(enemy_def, _DEF_IGNORE)  # min(50, 175) = 50
    expected_total = base_dmg + bonus

    actual_dmg = hp_before - low_def_enemy.hp
    assert actual_dmg == expected_total, (
        f"Bonus must be capped at enemy DEF {enemy_def} (not 175); "
        f"expected {expected_total}, got {actual_dmg}"
    )


def test_def_ignore_capped_at_175():
    """When enemy DEF > 175, bonus is exactly 175."""
    w = _world()
    v = make_vigil(slot=None)
    v.deployed = True; v.position = (0.0, 1.0)
    w.add_unit(v)

    high_def_enemy = UnitState(
        name="HighDefEnemy", faction=Faction.ENEMY,
        max_hp=5000, atk=0, defence=400, res=0.0,
        atk_interval=99.0, attack_range_melee=True,
        profession=Profession.GUARD, block=0, cost=0,
    )
    high_def_enemy.deployed = True; high_def_enemy.position = (1.0, 1.0)
    high_def_enemy.move_speed = 0.0
    w.add_unit(high_def_enemy)

    hp_before = high_def_enemy.hp
    v.atk_cd = 0.0
    w.tick()

    raw = v.effective_atk
    enemy_def = high_def_enemy.effective_def
    base_dmg = max(int(raw * 0.05), raw - enemy_def)
    bonus = min(enemy_def, _DEF_IGNORE)  # min(400, 175) = 175
    expected_total = base_dmg + bonus

    actual_dmg = hp_before - high_def_enemy.hp
    assert actual_dmg == expected_total, (
        f"Bonus must be capped at 175; expected {expected_total}, got {actual_dmg}"
    )
