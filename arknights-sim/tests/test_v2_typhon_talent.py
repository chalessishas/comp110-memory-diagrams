"""Typhon — King's Sight talent: +40% ATK True damage bonus to blocked enemies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, RoleArchetype
from core.systems import register_default_systems
from data.characters.typhon import (
    make_typhon,
    _TALENT_TAG, _TALENT_BONUS_RATIO,
)
from data.characters.mountain import make_mountain
from data.enemies import make_originium_slug


def _world(w=8, h=3) -> World:
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


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_typhon_config():
    t = make_typhon()
    assert t.archetype == RoleArchetype.SNIPER_SIEGE
    assert t.block == 1
    assert len(t.talents) == 1
    assert t.talents[0].name == "King's Sight"
    assert t.talents[0].behavior_tag == _TALENT_TAG
    sk = t.skill
    assert sk is not None and sk.slot == "S3"


# ---------------------------------------------------------------------------
# Test 2: No bonus when enemy is NOT blocked
# ---------------------------------------------------------------------------

def test_no_bonus_when_unblocked():
    """King's Sight must NOT fire when the enemy has no blocker."""
    w = _world()
    typhon = make_typhon()
    typhon.deployed = True; typhon.position = (0.0, 1.0); typhon.atk_cd = 0.0
    typhon.skill = None  # remove S3 to isolate talent
    w.add_unit(typhon)

    slug = _slug(pos=(1, 1), hp=999999, defence=0)
    w.add_unit(slug)

    hp_before = slug.hp
    w.tick()  # Typhon attacks; slug has no blocker

    # Only normal physical damage (no True bonus)
    expected_dmg = typhon.effective_atk  # 1 attack
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_dmg, (
        f"No King's Sight bonus when unblocked; expected {expected_dmg}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 3: Bonus True damage applied when enemy IS blocked
# ---------------------------------------------------------------------------

def test_bonus_when_blocked():
    """King's Sight fires when enemy is blocked — extra True damage is dealt."""
    w = _world()

    # Mountain at (1, 1) blocks the slug
    mountain = make_mountain()
    mountain.deployed = True; mountain.position = (1.0, 1.0); mountain.atk_cd = 999.0
    w.add_unit(mountain)

    typhon = make_typhon()
    typhon.deployed = True; typhon.position = (0.0, 1.0); typhon.atk_cd = 999.0
    typhon.skill = None
    w.add_unit(typhon)

    slug = _slug(pos=(1, 1), hp=999999, defence=0)
    w.add_unit(slug)

    w.tick()  # Mountain blocks slug; Typhon attacks but has high atk_cd
    assert len(slug.blocked_by_unit_ids) > 0, "Slug must be blocked by Mountain"

    typhon.atk_cd = 0.0
    hp_before = slug.hp
    w.tick()  # Typhon attacks blocked slug → talent fires

    # Besieger trait multiplies normal physical damage by 1.5× against blocked enemies
    besieger_dmg = int(typhon.effective_atk * 1.5)
    bonus_dmg = int(typhon.effective_atk * _TALENT_BONUS_RATIO)
    expected_total = besieger_dmg + bonus_dmg
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_total, (
        f"King's Sight bonus: expected {expected_total} total dmg; got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 4: Bonus is True damage — bypasses DEF
# ---------------------------------------------------------------------------

def test_bonus_true_damage_ignores_def():
    """King's Sight bonus must bypass enemy DEF entirely."""
    w = _world()

    mountain = make_mountain()
    mountain.deployed = True; mountain.position = (1.0, 1.0); mountain.atk_cd = 999.0
    w.add_unit(mountain)

    typhon = make_typhon()
    typhon.deployed = True; typhon.position = (0.0, 1.0); typhon.atk_cd = 999.0
    typhon.skill = None
    w.add_unit(typhon)

    slug_armored = _slug(pos=(1, 1), hp=999999, defence=999999)
    w.add_unit(slug_armored)

    w.tick()  # Mountain blocks armored slug
    assert len(slug_armored.blocked_by_unit_ids) > 0

    typhon.atk_cd = 0.0
    hp_before = slug_armored.hp
    w.tick()  # Typhon attacks

    actual_dmg = hp_before - slug_armored.hp
    bonus_dmg = int(typhon.effective_atk * _TALENT_BONUS_RATIO)
    # Physical attack is capped at 1 (DEF >> ATK). True bonus is not.
    assert actual_dmg >= bonus_dmg, (
        f"True damage bonus must bypass DEF; expected at least {bonus_dmg}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 5: Bonus amount equals int(effective_atk × TALENT_BONUS_RATIO)
# ---------------------------------------------------------------------------

def test_bonus_amount():
    """Bonus True damage equals exactly int(effective_atk × _TALENT_BONUS_RATIO)."""
    w = _world()

    mountain = make_mountain()
    mountain.deployed = True; mountain.position = (1.0, 1.0); mountain.atk_cd = 999.0
    w.add_unit(mountain)

    typhon = make_typhon()
    typhon.deployed = True; typhon.position = (0.0, 1.0); typhon.atk_cd = 999.0
    typhon.skill = None
    w.add_unit(typhon)

    slug = _slug(pos=(1, 1), hp=999999, defence=0)
    w.add_unit(slug)

    w.tick()
    assert len(slug.blocked_by_unit_ids) > 0

    typhon.atk_cd = 0.0
    hp_before = slug.hp
    w.tick()

    total_dmg = hp_before - slug.hp
    besieger_dmg = int(typhon.effective_atk * 1.5)  # Besieger 1.5× vs blocked
    actual_bonus = total_dmg - besieger_dmg
    expected_bonus = int(typhon.effective_atk * _TALENT_BONUS_RATIO)
    assert actual_bonus == expected_bonus, (
        f"King's Sight bonus must be {expected_bonus}; got {actual_bonus}"
    )
