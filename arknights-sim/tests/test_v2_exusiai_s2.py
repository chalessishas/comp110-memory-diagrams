"""Exusiai S2 Only Orange — +100 ASPD (halves attack interval) for 30s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.exusiai import make_exusiai
from data.enemies import make_originium_slug


EXU_POS = (0.0, 0.0)
SLUG_PATH = [(1 + i, 0) for i in range(8)]


def _world() -> World:
    grid = TileGrid(width=9, height=1)
    for i in range(9):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _make_slug() -> object:
    slug = make_originium_slug(path=SLUG_PATH)
    slug.deployed = True
    return slug


def test_s2_fires_and_aspd_buff_applied():
    """S2 activates when SP ready: ASPD buff is present on carrier."""
    w = _world()
    exa = make_exusiai()
    exa.deployed = True
    exa.position = EXU_POS
    # Pre-charge SP so skill fires on first auto-trigger window
    exa.skill.sp = float(exa.skill.sp_cost)
    w.add_unit(exa)

    slug = _make_slug()
    w.add_unit(slug)

    # Run until skill fires (active_remaining > 0)
    for _ in range(TICK_RATE * 2):
        w.tick()
        if exa.skill.active_remaining > 0:
            break

    assert exa.skill.active_remaining > 0, "S2 must have fired"
    aspd_buffs = [b for b in exa.buffs if b.axis == BuffAxis.ASPD]
    assert aspd_buffs, "ASPD buff must be present during S2"
    assert aspd_buffs[0].value == 100.0, f"Expected +100 ASPD, got {aspd_buffs[0].value}"


def test_s2_halves_attack_interval():
    """With +100 ASPD buff active, current_atk_interval == base / 2."""
    from core.state.unit_state import Buff
    from core.types import BuffStack

    exa = make_exusiai()
    base_interval = exa.atk_interval  # 1.0s

    exa.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=100.0, source_tag="test",
    ))
    # effective_aspd = 100 + 100 = 200  →  interval = 1.0 * 100/200 = 0.5
    assert abs(exa.current_atk_interval - base_interval / 2.0) < 1e-9, \
        f"Expected {base_interval/2.0}s interval, got {exa.current_atk_interval}"


def test_aspd_clamp_minimum():
    """ASPD below 20 is clamped to 20 — interval cannot exceed atk_interval * 5."""
    from core.state.unit_state import Buff
    from core.types import BuffStack

    exa = make_exusiai()
    base_interval = exa.atk_interval  # 1.0s

    # -500 ASPD → effective = 100 - 500 = -400, clamped to 20
    exa.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=-500.0, source_tag="test",
    ))
    expected = base_interval * 100.0 / 20.0  # = 5.0s
    assert abs(exa.current_atk_interval - expected) < 1e-9, \
        f"Expected {expected}s (clamp-min), got {exa.current_atk_interval}"


def test_aspd_clamp_maximum():
    """ASPD above 600 is clamped to 600 — interval cannot drop below atk_interval / 6."""
    from core.state.unit_state import Buff
    from core.types import BuffStack

    exa = make_exusiai()
    base_interval = exa.atk_interval  # 1.0s

    # +900 ASPD → effective = 100 + 900 = 1000, clamped to 600
    exa.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=900.0, source_tag="test",
    ))
    expected = base_interval * 100.0 / 600.0  # ≈ 0.1667s
    assert abs(exa.current_atk_interval - expected) < 1e-9, \
        f"Expected {expected:.4f}s (clamp-max), got {exa.current_atk_interval}"


def test_s2_buff_removed_on_end():
    """ASPD buff must be cleaned up when S2 expires."""
    w = _world()
    exa = make_exusiai()
    exa.deployed = True
    exa.position = EXU_POS
    exa.skill.sp = float(exa.skill.sp_cost)
    w.add_unit(exa)

    slug = _make_slug()
    w.add_unit(slug)

    # Fire skill
    for _ in range(TICK_RATE * 2):
        w.tick()
        if exa.skill.active_remaining > 0:
            break
    assert exa.skill.active_remaining > 0, "S2 must fire first"

    # Lock out further fires and run past duration (30s)
    exa.skill.sp = 0.0
    for _ in range(TICK_RATE * 32):  # 32s > 30s duration
        w.tick()

    assert exa.skill.active_remaining == 0.0, "Skill must have ended"
    aspd_buffs = [b for b in exa.buffs if b.axis == BuffAxis.ASPD]
    assert not aspd_buffs, "ASPD buff must be removed after S2 ends"
