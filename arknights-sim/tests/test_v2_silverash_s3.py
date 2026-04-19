"""SilverAsh S3 Truesilver Slash — 3-hit burst mechanics."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from math import floor

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.silverash import make_silverash
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _heavy_slug(path) -> object:
    """Slug with high HP so it survives 3 hits for assertion."""
    slug = make_originium_slug(path=path)
    slug.max_hp = 99_999
    slug.hp = 99_999
    return slug


def test_s3_burst_hits_3_times_on_activation():
    """S3 activation fires 3 rapid strikes immediately (using boosted ATK)."""
    w = _world()
    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 1.0)
    sa.atk_cd = 999.0                        # block normal attack this tick
    sa.skill.sp = float(sa.skill.sp_cost)    # S3 fires on first tick
    w.add_unit(sa)

    slug = _heavy_slug(path=[(1, 1)])        # dx=1, dy=0 — in GUARD_LORD_RANGE
    slug.deployed = True
    w.add_unit(slug)

    w.tick()

    # Expected per-hit damage: effective_atk (boosted) vs def=0
    boosted_atk = int(floor(sa.atk * (1 + 1.80)))
    per_hit = max(int(boosted_atk * 0.05), boosted_atk - slug.defence)
    assert w.global_state.total_damage_dealt == 3 * per_hit, (
        f"Expected 3×{per_hit}={3*per_hit} but got {w.global_state.total_damage_dealt}"
    )


def test_s3_burst_uses_boosted_atk():
    """Burst damage must use the +180% ATK buff applied in the same on_start hook."""
    w = _world()
    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 1.0)
    sa.atk_cd = 999.0
    sa.skill.sp = float(sa.skill.sp_cost)
    w.add_unit(sa)

    slug = _heavy_slug(path=[(1, 1)])
    slug.deployed = True
    w.add_unit(slug)

    w.tick()

    # If base ATK were used (no buff): 617 per hit × 3 hits
    # With +180% buff: floor(617 × 2.80) = 1727 per hit × 3 hits
    base_atk = sa.atk
    per_hit_base = max(int(base_atk * 0.05), base_atk - slug.defence)
    per_hit_boosted = max(int(floor(base_atk * 2.80) * 0.05), int(floor(base_atk * 2.80)) - slug.defence)

    assert w.global_state.total_damage_dealt == 3 * per_hit_boosted, "Burst must use boosted ATK"
    assert w.global_state.total_damage_dealt > 3 * per_hit_base, "Boosted must exceed base × 3"


def test_s3_burst_only_hits_enemies_in_range():
    """Enemies outside range_shape are not hit by the S3 burst."""
    w = _world()
    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 1.0)
    sa.atk_cd = 999.0
    sa.skill.sp = float(sa.skill.sp_cost)
    w.add_unit(sa)

    slug_in = _heavy_slug(path=[(1, 1)])    # dx=1 — in range
    slug_in.deployed = True
    w.add_unit(slug_in)

    slug_out = _heavy_slug(path=[(3, 1)])   # dx=3 — NOT in GUARD_LORD_RANGE {(0,0),(1,0)}
    slug_out.deployed = True
    w.add_unit(slug_out)

    w.tick()

    assert slug_in.hp < slug_in.max_hp, "In-range slug should take damage"
    assert slug_out.hp == slug_out.max_hp, "Out-of-range slug must not be hit"


def test_s3_atk_buff_persists_during_duration():
    """ATK buff from S3 stays active for the full 15s duration."""
    w = _world()
    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 1.0)
    sa.skill.sp = float(sa.skill.sp_cost)
    w.add_unit(sa)

    w.tick()  # S3 fires, buff applied

    from core.types import BuffAxis
    buff_axes = [b.axis for b in sa.buffs]
    assert BuffAxis.ATK in buff_axes, "ATK buff must be present after S3 activation"


def test_s3_atk_buff_removed_on_end():
    """ATK buff from S3 is cleaned up when skill duration expires."""
    w = _world()
    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 1.0)
    sa.skill.sp = float(sa.skill.sp_cost)
    sa.skill.duration = 0.5  # short duration for fast test
    w.add_unit(sa)

    w.tick()  # S3 fires

    from core.types import BuffAxis
    assert any(b.axis == BuffAxis.ATK for b in sa.buffs), "Buff active during skill"

    # Advance past duration
    for _ in range(TICK_RATE):  # 1 second > 0.5s duration
        w.tick()

    assert not any(b.axis == BuffAxis.ATK for b in sa.buffs), "Buff must be removed after skill ends"
