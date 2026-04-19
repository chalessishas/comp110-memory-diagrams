"""Liskarm talent: Lightning Discharge — electric arc to attacker on being hit."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters import make_liskarm
from data.enemies import make_originium_slug


PATH = [(x, 0) for x in range(4)]


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_lightning_discharge_deals_damage_to_attacker():
    """When slug attacks Liskarm, Liskarm's arc fires back and deals Arts damage to slug."""
    w = _world()
    liskarm = make_liskarm()
    liskarm.deployed = True
    liskarm.position = (1.0, 0.0)
    w.add_unit(liskarm)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.blocked_by_unit_ids = [liskarm.unit_id]
    slug.atk_cd = 0.0
    w.add_unit(slug)

    slug_hp_before = slug.hp

    # Run until slug has attacked Liskarm at least once
    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.hp < slug_hp_before:
            break

    assert slug.hp < slug_hp_before, \
        f"Lightning Discharge must deal damage to attacker, slug HP unchanged: {slug.hp}"


def test_lightning_discharge_uses_liskarm_atk():
    """Arc damage is 120% of Liskarm's ATK (Arts, reduced by slug RES=0 → full)."""
    w = _world()
    liskarm = make_liskarm()
    liskarm.deployed = True
    liskarm.position = (1.0, 0.0)
    w.add_unit(liskarm)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.res = 0.0   # no resistance → full Arts damage
    slug.blocked_by_unit_ids = [liskarm.unit_id]
    slug.atk_cd = 0.0
    w.add_unit(slug)

    # Prevent Liskarm from attacking so only arc fires
    liskarm.atk_cd = 999.0

    slug_hp_before = slug.hp

    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.hp < slug_hp_before:
            break

    expected_arc = int(liskarm.effective_atk * 1.20)
    actual_dmg = slug_hp_before - slug.hp
    assert actual_dmg == expected_arc, \
        f"Arc damage should be {expected_arc} (120% ATK={liskarm.effective_atk}), got {actual_dmg}"
