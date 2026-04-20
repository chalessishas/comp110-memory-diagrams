"""Sora — SUP_BARD SP aura mechanic.

Tests cover:
  - Archetype and never-attacks rule
  - SP aura charges nearby ally's skill over time
  - SP aura rate: ~1 SP/s from trait alone, ~1.5 SP/s with Mellow Flow talent
  - Sora does NOT grant SP to herself or to allies with active skills
  - Sora does NOT attack enemies even when they are in range
  - S2 Encore doubles aura rate (×2) while active
  - Ally out of range receives no SP from Sora
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.sora import (
    make_sora, _TRAIT_SP_RATE, _TALENT_SP_BONUS, _S2_DURATION, _S2_SP_MULTIPLIER,
)
from data.characters import make_liskarm
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


def _ally_with_skill(pos=(1, 1), sp_cost: int = 20) -> UnitState:
    """A deployed ally with a skill at 0 SP."""
    op = make_liskarm()
    op.deployed = True
    op.position = (float(pos[0]), float(pos[1]))
    op.skill = SkillComponent(
        name="TestSkill",
        slot="S1",
        sp_cost=sp_cost,
        initial_sp=0,
        duration=10.0,
        sp_gain_mode=SPGainMode.AUTO_ATTACK,  # no natural SP gain; only Sora's aura
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="noop_skill",
    )
    op.skill.sp = 0.0
    return op


# ---------------------------------------------------------------------------
# Test 1: Archetype
# ---------------------------------------------------------------------------

def test_sora_archetype():
    s = make_sora()
    assert s.archetype == RoleArchetype.SUP_BARD


# ---------------------------------------------------------------------------
# Test 2: Sora never attacks enemies in range
# ---------------------------------------------------------------------------

def test_sora_never_attacks_enemies():
    """Sora must NOT damage enemies even when they are in her range."""
    w = _world()
    s = make_sora()
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 0.0
    w.add_unit(s)

    path = [(x, 1) for x in range(8)]
    slug = make_originium_slug(path=path)
    slug.deployed = True; slug.position = (2.0, 1.0)
    slug.max_hp = 9999; slug.hp = 9999
    slug.move_speed = 0.0
    w.add_unit(slug)

    hp_before = slug.hp
    for _ in range(TICK_RATE * 5):
        w.tick()

    assert slug.hp == hp_before, (
        f"Sora (SUP_BARD) must not deal damage; hp={slug.hp}/{hp_before}"
    )


# ---------------------------------------------------------------------------
# Test 3: SP aura charges nearby ally's skill (trait only)
# ---------------------------------------------------------------------------

def test_sp_aura_charges_ally_skill():
    """Sora (trait only) grants ~1 SP/s to a nearby ally's skill."""
    w = _world()
    s = make_sora(talent=False)  # trait only, no Mellow Flow
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _ally_with_skill(pos=(2, 1), sp_cost=100)
    w.add_unit(ally)

    sp_before = ally.skill.sp

    # Run 3 seconds
    ticks = TICK_RATE * 3
    for _ in range(ticks):
        w.tick()

    expected_min = _TRAIT_SP_RATE * 3.0 * 0.8  # 80% tolerance
    gained = ally.skill.sp - sp_before
    assert gained >= expected_min, (
        f"Expected ≥{expected_min:.1f} SP gained in 3s, got {gained:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 4: Mellow Flow talent adds extra SP/s
# ---------------------------------------------------------------------------

def test_mellow_flow_adds_bonus_sp():
    """With Mellow Flow talent, SP gain rate is higher than trait alone."""
    w_with = _world()
    s_with = make_sora(talent=True)
    s_with.deployed = True; s_with.position = (0.0, 1.0)
    w_with.add_unit(s_with)
    ally_with = _ally_with_skill(pos=(2, 1), sp_cost=100)
    w_with.add_unit(ally_with)

    w_without = _world()
    s_without = make_sora(talent=False)
    s_without.deployed = True; s_without.position = (0.0, 1.0)
    w_without.add_unit(s_without)
    ally_without = _ally_with_skill(pos=(2, 1), sp_cost=100)
    w_without.add_unit(ally_without)

    ticks = TICK_RATE * 5
    for _ in range(ticks):
        w_with.tick()
        w_without.tick()

    assert ally_with.skill.sp > ally_without.skill.sp, (
        f"Mellow Flow must increase SP gain: {ally_with.skill.sp:.2f} vs {ally_without.skill.sp:.2f}"
    )
    # Difference should be approximately _TALENT_SP_BONUS * 5s
    diff = ally_with.skill.sp - ally_without.skill.sp
    expected_bonus = _TALENT_SP_BONUS * 5.0 * 0.7
    assert diff >= expected_bonus, (
        f"Mellow Flow bonus too small: diff={diff:.2f}, expected ≥{expected_bonus:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 5: Sora does NOT grant SP to ally with active skill
# ---------------------------------------------------------------------------

def test_aura_skips_ally_with_active_skill():
    """Sora's aura must not add SP to an ally whose skill is currently active."""
    w = _world()
    s = make_sora(talent=True)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _ally_with_skill(pos=(2, 1), sp_cost=20)
    w.add_unit(ally)

    # Force skill active
    ally.skill.sp = float(ally.skill.sp_cost)
    ally.skill.active_remaining = 10.0  # skill is running

    sp_before = ally.skill.sp
    for _ in range(TICK_RATE * 2):
        w.tick()

    assert ally.skill.sp <= sp_before + 0.01, (
        f"Aura must not charge SP during active skill; sp={ally.skill.sp:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 6: Ally out of range receives no SP
# ---------------------------------------------------------------------------

def test_aura_does_not_reach_out_of_range_ally():
    """An ally deployed beyond Sora's range_shape does not gain SP."""
    w = _world()
    s = make_sora(talent=True)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    # Sora's range: dx 0-3. Ally at dx=5 is out of range.
    far_ally = _ally_with_skill(pos=(5, 1), sp_cost=100)
    w.add_unit(far_ally)

    sp_before = far_ally.skill.sp
    for _ in range(TICK_RATE * 3):
        w.tick()

    assert far_ally.skill.sp == sp_before, (
        f"Out-of-range ally must not gain SP; gained {far_ally.skill.sp - sp_before:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 Encore doubles aura rate
# ---------------------------------------------------------------------------

def test_s2_doubles_sp_aura():
    """During S2, SP gain rate doubles compared to normal."""
    w_s2 = _world()
    s_s2 = make_sora(slot="S2", talent=False)
    s_s2.deployed = True; s_s2.position = (0.0, 1.0)
    s_s2.atk_cd = 999.0
    w_s2.add_unit(s_s2)
    ally_s2 = _ally_with_skill(pos=(2, 1), sp_cost=200)
    w_s2.add_unit(ally_s2)

    w_base = _world()
    s_base = make_sora(slot=None, talent=False)
    s_base.deployed = True; s_base.position = (0.0, 1.0)
    w_base.add_unit(s_base)
    ally_base = _ally_with_skill(pos=(2, 1), sp_cost=200)
    w_base.add_unit(ally_base)

    # Activate S2 immediately
    s_s2.skill.sp = s_s2.skill.sp_cost
    ticks = TICK_RATE * 5

    for _ in range(ticks):
        w_s2.tick()
        w_base.tick()

    s2_gain = ally_s2.skill.sp
    base_gain = ally_base.skill.sp

    assert s2_gain > base_gain * 1.5, (
        f"S2 must roughly double SP gain: s2={s2_gain:.2f}, base={base_gain:.2f}"
    )
