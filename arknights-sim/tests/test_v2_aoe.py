"""v2 AOE (splash_radius) integration tests — arts caster hits nearby enemies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Faction, Profession, TileType, TICK_RATE
from core.systems import register_default_systems
from data.enemies import make_originium_slug


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    register_default_systems(world)
    return world


def _make_aoe_caster(pos: tuple, splash: float = 1.0) -> UnitState:
    ox, oy = int(pos[0]), int(pos[1])
    # 3×3 range covering tiles (-2..1, -1..1) relative to caster
    range_tiles = tuple(
        (dx, dy) for dx in range(-2, 2) for dy in range(-1, 2)
    )
    return UnitState(
        name="AOE Caster",
        faction=Faction.ALLY,
        max_hp=1500,
        atk=500,
        defence=80,
        res=20.0,
        atk_interval=2.0,
        attack_type=AttackType.ARTS,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=range_tiles),
        splash_radius=splash,
        block=0,
        deployed=True,
        position=pos,
    )


def _make_slug_at(x: int, y: int) -> UnitState:
    # Long path starting at (x, y) going right — enemy won't reach goal in 5 ticks
    path = [(x + i, y) for i in range(5)]
    slug = make_originium_slug(path=path)
    slug.position = (float(x), float(y))
    slug.deployed = True
    return slug


def test_aoe_hits_primary_and_adjacent():
    """Caster attacks primary target; nearby enemy within splash_radius also takes damage."""
    w = _world()
    caster = _make_aoe_caster(pos=(3.0, 1.0), splash=1.0)
    w.add_unit(caster)

    slug_primary = _make_slug_at(2, 1)    # directly in front — will be targeted
    slug_splash = _make_slug_at(2, 2)     # 1 tile away — within splash radius
    slug_far = _make_slug_at(0, 0)        # far away — outside splash radius
    w.add_unit(slug_primary)
    w.add_unit(slug_splash)
    w.add_unit(slug_far)

    hp_before_far = slug_far.hp
    hp_before_splash = slug_splash.hp
    hp_before_primary = slug_primary.hp

    # Force target to primary slug (bypass targeting system for test clarity)
    caster.__target__ = slug_primary    # type: ignore[attr-defined]
    caster.atk_cd = 0.0

    for _ in range(5):
        w.tick()
        if slug_primary.hp < hp_before_primary:
            break

    assert slug_primary.hp < hp_before_primary, "Primary target must take damage"
    assert slug_splash.hp < hp_before_splash, "Splash target must take damage from AOE"
    assert slug_far.hp == hp_before_far, "Distant enemy outside splash must not take damage"


def test_aoe_arts_damage_uses_res():
    """AOE arts damage is reduced by target's magic resistance."""
    w = _world()
    caster = _make_aoe_caster(pos=(3.0, 1.0), splash=2.0)
    w.add_unit(caster)

    # Enemy with 50% RES — takes half arts damage
    slug_resistant = _make_slug_at(2, 1)
    slug_resistant.res = 50.0
    # Normal enemy with 0% RES
    slug_normal = _make_slug_at(2, 2)
    slug_normal.res = 0.0

    for e in [slug_resistant, slug_normal]:
        w.add_unit(e)

    hp_before_resistant = slug_resistant.hp
    hp_before_normal = slug_normal.hp

    caster.__target__ = slug_resistant   # type: ignore[attr-defined]
    caster.atk_cd = 0.0

    for _ in range(5):
        w.tick()
        if slug_resistant.hp < hp_before_resistant:
            break

    dmg_resistant = hp_before_resistant - slug_resistant.hp
    dmg_normal = hp_before_normal - slug_normal.hp

    assert dmg_normal > 0, "Normal enemy must take splash damage"
    assert dmg_resistant > 0, "Resistant enemy must take some damage"
    # RES 50%: resistant takes ~half — allow some rounding
    assert dmg_resistant < dmg_normal, "50% RES enemy should take less arts damage"


def test_aoe_zero_splash_radius_no_splash():
    """Operator with splash_radius=0 must not hit adjacent enemies."""
    w = _world()
    caster = _make_aoe_caster(pos=(3.0, 1.0), splash=0.0)
    w.add_unit(caster)

    slug_primary = _make_slug_at(2, 1)
    slug_adjacent = _make_slug_at(2, 2)
    w.add_unit(slug_primary)
    w.add_unit(slug_adjacent)

    hp_before = slug_adjacent.hp
    caster.__target__ = slug_primary   # type: ignore[attr-defined]
    caster.atk_cd = 0.0

    for _ in range(5):
        w.tick()
        if slug_primary.hp < 1300:
            break

    assert slug_adjacent.hp == hp_before, "Non-AOE caster must not splash adjacent enemies"
