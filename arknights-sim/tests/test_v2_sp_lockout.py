"""SP lockout window — post-skill SP gain immunity.

After a skill's active duration ends, there is a brief lockout window
(SP_POST_SKILL_LOCKOUT = 0.5s) during which no SP can be gained from
any source: AUTO_TIME, AUTO_ATTACK, AUTO_DEFENSIVE, Ptilopsis aura,
or Sora bard aura.

Tests cover:
  - AUTO_TIME skill: SP stays 0 immediately after skill ends (within lockout)
  - AUTO_TIME skill: SP resumes accumulating after lockout expires
  - AUTO_ATTACK skill: no SP on attack during lockout window
  - AUTO_ATTACK skill: SP on attack resumes after lockout expires
  - AUTO_DEFENSIVE: no SP on being hit during lockout
  - Ptilopsis aura: does not grant SP to an ally in lockout
  - Ptilopsis aura: does grant SP to an ally after lockout expires
  - Sora bard aura: does not grant SP to an ally in lockout
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, Profession,
    RoleArchetype, SPGainMode, SkillTrigger, SP_POST_SKILL_LOCKOUT,
)
from core.systems import register_default_systems
from data.characters.ptilopsis import make_ptilopsis
from data.characters.sora import make_sora
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _auto_time_op(sp_cost: int = 10, duration: float = 2.0) -> UnitState:
    """Operator with AUTO_TIME skill, no behavior needed for this test."""
    from core.systems.skill_system import register_skill
    register_skill("_test_lockout_noop", on_start=None, on_tick=None, on_end=None)
    return UnitState(
        name="TestAutoTime",
        faction=Faction.ALLY,
        max_hp=2000, hp=2000, atk=100,
        defence=0, atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=((1, 0),)),
        deployed=True, position=(0.0, 1.0),
        skill=SkillComponent(
            name="Noop",
            slot="S1",
            sp_cost=sp_cost,
            initial_sp=0,
            duration=duration,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag="_test_lockout_noop",
        ),
    )


def _auto_attack_op(sp_cost: int = 5, duration: float = 0.0) -> UnitState:
    """Operator with AUTO_ATTACK skill (instant-fire, no duration)."""
    from core.systems.skill_system import register_skill
    register_skill("_test_lockout_aa", on_start=None, on_tick=None, on_end=None)
    return UnitState(
        name="TestAutoAttack",
        faction=Faction.ALLY,
        max_hp=2000, hp=2000, atk=100,
        defence=0, atk_interval=0.1, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=((1, 0),)),
        deployed=True, position=(0.0, 1.0),
        atk_cd=0.0,
        skill=SkillComponent(
            name="AA Noop",
            slot="S1",
            sp_cost=sp_cost,
            initial_sp=0,
            duration=duration,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag="_test_lockout_aa",
        ),
    )


def _slug(pos=(1, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: AUTO_TIME — no SP within lockout window after skill ends
# ---------------------------------------------------------------------------

def test_auto_time_no_sp_during_lockout():
    """Immediately after a skill ends, SP stays 0 during the lockout window."""
    w = _world()
    op = _auto_time_op(sp_cost=10, duration=0.2)  # very short skill
    op.skill.sp = op.skill.sp_cost  # full SP
    w.add_unit(op)

    # Manually fire the skill
    from core.systems.skill_system import manual_trigger
    op.skill.trigger = SkillTrigger.MANUAL
    # Force skill active by directly setting
    op.skill.active_remaining = op.skill.duration

    # Run until skill ends (0.2s = 2 ticks)
    for _ in range(3):
        w.tick()

    # Skill should be over; lockout should be active
    assert op.skill.active_remaining == 0.0, "Skill should have ended"
    assert op.skill.sp_lockout_until > w.global_state.elapsed, (
        f"Lockout should be active; lockout_until={op.skill.sp_lockout_until}, "
        f"now={w.global_state.elapsed}"
    )
    sp_at_lockout_start = op.skill.sp
    assert sp_at_lockout_start == 0.0, f"SP should be 0 right after skill ends; got {sp_at_lockout_start}"

    # Tick once more (still within lockout)
    w.tick()
    assert op.skill.sp == 0.0, (
        f"SP must not increase during lockout; got {op.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 2: AUTO_TIME — SP resumes after lockout expires
# ---------------------------------------------------------------------------

def test_auto_time_sp_resumes_after_lockout():
    """After SP_POST_SKILL_LOCKOUT seconds, AUTO_TIME SP gain resumes."""
    w = _world()
    op = _auto_time_op(sp_cost=10, duration=0.1)
    op.skill.active_remaining = op.skill.duration  # skill is active
    w.add_unit(op)

    # Advance until skill ends + past lockout
    lockout_ticks = int(SP_POST_SKILL_LOCKOUT * TICK_RATE) + 3
    for _ in range(2 + lockout_ticks):
        w.tick()

    # Now lockout should be over; SP should be accumulating
    assert w.global_state.elapsed > op.skill.sp_lockout_until, "Lockout should have expired"
    sp_before = op.skill.sp

    # One more tick to accumulate
    w.tick()
    assert op.skill.sp > sp_before or op.skill.sp > 0.0, (
        f"SP must accumulate after lockout; was {sp_before}, now {op.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 3: AUTO_ATTACK — no SP on attack during lockout
# ---------------------------------------------------------------------------

def test_auto_attack_no_sp_during_lockout():
    """No SP gained on attack during the post-skill lockout window."""
    w = _world()
    op = _auto_attack_op(sp_cost=5, duration=0.1)  # instant-ish skill
    op.skill.active_remaining = 0.2  # skill active
    op.atk_cd = 0.0
    w.add_unit(op)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Let skill end (0.2s = 2 ticks)
    for _ in range(3):
        w.tick()

    assert op.skill.active_remaining == 0.0, "Skill must have ended"
    assert w.global_state.elapsed <= op.skill.sp_lockout_until, "Must still be in lockout"

    sp_before = op.skill.sp  # should be 0
    op.atk_cd = 0.0          # force attack
    w.tick()

    # SP should NOT increase during lockout
    assert op.skill.sp == sp_before, (
        f"No SP gain on attack during lockout; expected {sp_before}, got {op.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 4: AUTO_ATTACK — SP on attack resumes after lockout expires
# ---------------------------------------------------------------------------

def test_auto_attack_sp_resumes_after_lockout():
    """AUTO_ATTACK SP gain resumes once the lockout window expires."""
    w = _world()
    op = _auto_attack_op(sp_cost=5, duration=0.1)
    op.skill.active_remaining = 0.1  # skill ends quickly
    op.atk_cd = 0.0
    w.add_unit(op)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Advance past lockout
    advance_ticks = int((0.1 + SP_POST_SKILL_LOCKOUT) * TICK_RATE) + 3
    for _ in range(advance_ticks):
        w.tick()

    assert w.global_state.elapsed > op.skill.sp_lockout_until, "Lockout must have expired"

    sp_before = op.skill.sp
    op.atk_cd = 0.0   # force attack now
    w.tick()

    assert op.skill.sp > sp_before, (
        f"SP must increase on attack after lockout; was {sp_before}, now {op.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 5: AUTO_DEFENSIVE — no SP on being hit during lockout
# ---------------------------------------------------------------------------

def test_auto_defensive_no_sp_during_lockout():
    """No SP gained from being hit during the post-skill lockout window."""
    from core.systems.skill_system import register_skill
    register_skill("_test_lockout_def", on_start=None, on_tick=None, on_end=None)
    w = _world()
    op = UnitState(
        name="DefOp",
        faction=Faction.ALLY,
        max_hp=9999, hp=9999, atk=0,
        defence=0, atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(0.0, 1.0),
        skill=SkillComponent(
            name="Def Noop",
            slot="S1",
            sp_cost=5,
            initial_sp=0,
            duration=0.1,
            sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag="_test_lockout_def",
        ),
    )
    op.skill.active_remaining = 0.2  # skill active
    w.add_unit(op)

    # A dummy enemy that attacks op
    attacker = UnitState(
        name="Attacker",
        faction=Faction.ENEMY,
        max_hp=9999, hp=9999, atk=10,
        defence=0, atk_interval=0.1, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=((0, 0),)),
        deployed=True, position=(0.0, 1.0),
        atk_cd=0.0,
    )
    attacker.blocked_by_unit_ids = [op.unit_id]
    w.add_unit(attacker)

    # Let skill end
    for _ in range(3):
        w.tick()

    assert op.skill.active_remaining == 0.0
    assert w.global_state.elapsed <= op.skill.sp_lockout_until, "Should be in lockout"

    sp_before = op.skill.sp
    # Force another attack against op
    attacker.atk_cd = 0.0
    w.tick()

    assert op.skill.sp == sp_before, (
        f"No SP from being hit during lockout; expected {sp_before}, got {op.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Ptilopsis aura does NOT grant SP during lockout
# ---------------------------------------------------------------------------

def test_ptilopsis_aura_blocked_during_lockout():
    """Ptilopsis Unisonant aura must not grant SP to an ally in lockout."""
    w = _world()

    ptilo = make_ptilopsis()
    ptilo.deployed = True
    ptilo.position = (1.0, 1.0)
    ptilo.atk_cd = 999.0   # don't heal
    w.add_unit(ptilo)

    # Target ally with a skill in post-skill lockout
    target = _auto_time_op(sp_cost=20, duration=0.1)
    target.position = (0.0, 1.0)
    target.skill.active_remaining = 0.1  # will end quickly
    w.add_unit(target)

    # Let skill end
    for _ in range(2):
        w.tick()

    # Set lockout manually to ensure we're testing what we think
    target.skill.sp_lockout_until = w.global_state.elapsed + 1.0  # 1s lockout
    sp_before = target.skill.sp

    # Run for 0.3s inside lockout
    for _ in range(3):
        w.tick()

    assert target.skill.sp == sp_before, (
        f"Ptilopsis must not grant SP during lockout; sp was {sp_before}, now {target.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 7: Ptilopsis aura DOES grant SP after lockout expires
# ---------------------------------------------------------------------------

def test_ptilopsis_aura_resumes_after_lockout():
    """After lockout expires, Ptilopsis aura grants SP normally."""
    w = _world()

    ptilo = make_ptilopsis()
    ptilo.deployed = True
    ptilo.position = (1.0, 1.0)
    ptilo.atk_cd = 999.0
    w.add_unit(ptilo)

    target = _auto_time_op(sp_cost=20, duration=0.1)
    target.position = (0.0, 1.0)
    # Set lockout to expire in 0.1s
    target.skill.sp_lockout_until = w.global_state.elapsed + 0.1
    w.add_unit(target)

    # Advance past lockout
    for _ in range(4):
        w.tick()

    assert w.global_state.elapsed > target.skill.sp_lockout_until, "Lockout must have expired"
    sp_before = target.skill.sp

    # Run a few more ticks — Ptilopsis should grant SP now
    for _ in range(5):
        w.tick()

    assert target.skill.sp > sp_before, (
        f"Ptilopsis must grant SP after lockout; sp was {sp_before}, now {target.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 8: Sora bard aura does NOT grant SP during lockout
# ---------------------------------------------------------------------------

def test_sora_aura_blocked_during_lockout():
    """Sora's bard SP aura must not grant SP to an ally in lockout."""
    w = _world()

    sora = make_sora(slot="S2", talent=False)
    sora.deployed = True
    sora.position = (1.0, 1.0)
    w.add_unit(sora)

    target = _auto_time_op(sp_cost=20, duration=0.1)
    target.position = (0.0, 1.0)
    # Force lockout: 2 seconds
    target.skill.sp_lockout_until = w.global_state.elapsed + 2.0
    sp_before = target.skill.sp
    w.add_unit(target)

    # Run 0.5s — Sora's aura fires but lockout blocks it
    for _ in range(5):
        w.tick()

    assert w.global_state.elapsed < target.skill.sp_lockout_until, "Still in lockout"
    assert target.skill.sp == sp_before, (
        f"Sora aura must not grant SP during lockout; sp was {sp_before}, now {target.skill.sp}"
    )
