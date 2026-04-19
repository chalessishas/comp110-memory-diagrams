"""Angelina S3 All for One — team ATK+50% and ASPD+25 aura for 40s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.angelina import make_angelina
from data.characters.silverash import make_silverash
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _slug_far() -> object:
    """Slug that starts outside Angelina's range (lockout prevention for Angelina)."""
    slug = make_originium_slug(path=[(6 + i, 1) for i in range(2)])
    slug.deployed = True
    slug.max_hp = 99_999
    slug.hp = 99_999
    slug.move_speed = 0.0
    return slug


def test_s3_buffs_all_deployed_allies():
    """S3 activation applies ATK and ASPD buffs to every deployed ally."""
    w = _world()

    ang = make_angelina("S3")
    ang.deployed = True
    ang.position = (0.0, 1.0)
    ang.skill.sp = float(ang.skill.sp_cost)  # pre-charged
    w.add_unit(ang)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 1.0)
    w.add_unit(sa)

    # Slug in Angelina's DECEL_RANGE so lockout doesn't block her skill
    slug = _slug_far()
    slug.path = [(1 + i, 1) for i in range(5)]
    w.add_unit(slug)

    w.tick()  # S3 fires

    assert ang.skill.active_remaining > 0, "S3 must be active"

    for ally in [ang, sa]:
        atk_buffs = [b for b in ally.buffs if b.axis == BuffAxis.ATK]
        aspd_buffs = [b for b in ally.buffs if b.axis == BuffAxis.ASPD]
        assert atk_buffs, f"{ally.name} missing ATK buff"
        assert aspd_buffs, f"{ally.name} missing ASPD buff"
        assert any(abs(b.value - 0.50) < 1e-9 for b in atk_buffs), \
            f"{ally.name} ATK buff value wrong: {[b.value for b in atk_buffs]}"
        assert any(abs(b.value - 25.0) < 1e-9 for b in aspd_buffs), \
            f"{ally.name} ASPD buff value wrong: {[b.value for b in aspd_buffs]}"


def test_s3_buffs_removed_on_end():
    """All aura buffs are cleaned up when S3 expires."""
    w = _world()

    ang = make_angelina("S3")
    ang.deployed = True
    ang.position = (0.0, 1.0)
    ang.skill.sp = float(ang.skill.sp_cost)
    ang.skill.duration = 0.5  # short duration for fast test
    w.add_unit(ang)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 1.0)
    w.add_unit(sa)

    slug = _slug_far()
    slug.path = [(1 + i, 1) for i in range(5)]
    w.add_unit(slug)

    w.tick()  # S3 fires
    assert ang.skill.active_remaining > 0, "S3 must fire first"

    # Advance past duration
    for _ in range(TICK_RATE * 2):
        w.tick()

    assert ang.skill.active_remaining == 0.0, "Skill must have ended"
    for ally in [ang, sa]:
        aura_buffs = [b for b in ally.buffs if b.source_tag == "angelina_s3_aura"]
        assert not aura_buffs, f"{ally.name} still has aura buffs after S3 ends"


def test_s3_atk_buff_increases_effective_atk():
    """Angelina's ATK ratio buff raises effective_atk on teammates."""
    w = _world()

    ang = make_angelina("S3")
    ang.deployed = True
    ang.position = (0.0, 1.0)
    ang.skill.sp = float(ang.skill.sp_cost)
    w.add_unit(ang)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 1.0)
    base_atk = sa.effective_atk
    w.add_unit(sa)

    slug = _slug_far()
    slug.path = [(1 + i, 1) for i in range(5)]
    w.add_unit(slug)

    w.tick()  # S3 fires

    from math import floor
    expected = int(floor(base_atk * 1.50))
    assert sa.effective_atk == expected, \
        f"Expected buffed ATK={expected}, got {sa.effective_atk}"
