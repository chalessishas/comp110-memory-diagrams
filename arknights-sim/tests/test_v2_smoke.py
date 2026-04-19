"""v2 architecture smoke test — prove the new World + Systems + State pipeline
actually simulates a combat end-to-end."""
from __future__ import annotations
from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.global_state import GlobalState
from core.systems import register_default_systems
from core.types import TileType, BuffAxis, BuffStack
from core.state.unit_state import Buff
from data.characters import make_silverash, make_liskarm
from data.enemies import make_originium_slug


def _make_grid() -> TileGrid:
    """Straight-path 8×3 grid: y=1 is walkable, y=0 is elevated, y=2 is elevated."""
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        grid.set_tile(TileState(x=x, y=1, type=TileType.GROUND))
        grid.set_tile(TileState(x=x, y=0, type=TileType.ELEVATED))
        grid.set_tile(TileState(x=x, y=2, type=TileType.ELEVATED))
    # goal at end of path
    goal = grid.get(7, 1)
    goal.type = TileType.GOAL
    return grid


PATH = [(x, 1) for x in range(8)]


def _fresh_world() -> World:
    w = World(tile_grid=_make_grid(), global_state=GlobalState(max_lives=3, lives=3))
    register_default_systems(w)
    return w


def test_world_imports_and_constructs():
    w = _fresh_world()
    assert w.global_state.lives == 3
    assert w.tile_grid.width == 8
    assert len(list(w.tile_grid.iter_tiles())) == 24


def test_buff_pipeline_two_stage():
    """Terra Wiki pipeline: FLOOR(atk*(1+Σratio)) * Π mult."""
    op = make_silverash()  # base atk 763 (akgd E2 trust-100)
    op.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO, value=1.80, source_tag="s3"))
    # +180% ratio → 763 * 2.80 = 2136.4 → floor 2136
    assert op.effective_atk == 2136

    op.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.MULTIPLIER, value=1.20, source_tag="teamA"))
    # 2136 * 1.20 = 2563.2 → floor 2563
    assert op.effective_atk == 2563


def test_silverash_skill_fires_and_applies_buff():
    """SilverAsh S3 needs 20 SP at 1 SP/s; should fire at t≈20s."""
    w = _fresh_world()
    op = make_silverash()
    op.deployed = True
    op.position = (3.0, 1.0)
    w.add_unit(op)
    # run 25 seconds
    for _ in range(250):
        w.tick()
        if op.skill.fire_count > 0:
            break
    assert op.skill.fire_count == 1, f"skill should fire once, got {op.skill.fire_count}"
    # While active, buff should be present
    assert any(b.source_tag == "silverash_s3_atk_buff" for b in op.buffs)


def test_silverash_beats_lone_slug():
    """End-to-end: SilverAsh on (2,1) blocks + kills 1 Originium Slug walking the path."""
    w = _fresh_world()
    op = make_silverash()
    op.deployed = True
    op.position = (2.0, 1.0)
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    result = w.run(max_seconds=60.0)
    assert result == "win", f"expected win, got {result}  lives={w.global_state.lives}"
    assert not slug.alive
    assert op.alive


def test_liskarm_survives_slug():
    """Regression: Liskarm 3240 HP (akgd E2 trust-100) tanks slug's attacks."""
    w = _fresh_world()
    op = make_liskarm()
    op.deployed = True
    op.position = (2.0, 1.0)
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    result = w.run(max_seconds=60.0)
    assert result == "win"
    assert op.hp > 0
