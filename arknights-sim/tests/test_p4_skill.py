"""P4 acceptance: skill system alters combat outcome verifiably.

Covers SP accumulation, skill activation, ATK buff window, restoration on end,
and the SilverAsh-vs-Arts-Master burst demo.
"""
from __future__ import annotations
import pytest
from core.battle import Battle, DT
from core.operator import Operator
from core.skill import Skill
from core.enemy import Enemy
from data.operators import make_silverash
from data.enemies import make_arts_master


# ---- Unit tests: skill lifecycle --------------------------------------------


def test_sp_accumulates_auto_time():
    """auto_time mode ticks SP up at sp_gain_rate per second."""
    op = make_silverash()
    # 10 ticks at DT=0.1 with sp_gain_rate=1.0 ⇒ 1 SP
    for _ in range(10):
        op.update_skill(DT)
    assert op.sp == pytest.approx(1.0), f"Expected 1.0 SP, got {op.sp}"


def test_skill_fires_on_full_sp():
    op = make_silverash()  # sp_cost=20
    # 200 ticks ⇒ 20 SP ⇒ fires this tick
    for _ in range(199):
        op.update_skill(DT)
    assert not op.skill_active, "Skill should not have fired yet"
    op.update_skill(DT)
    assert op.skill_active, "Skill should fire when SP reaches cost"
    assert op._skill_just_fired
    assert op.sp == 0.0, "SP resets on activation"
    assert op._atk_bonus > 0, "ATK bonus applied via on_start"


def test_atk_buff_applied_and_removed():
    op = make_silverash()
    base_atk = op.atk
    # fire skill
    for _ in range(200):
        op.update_skill(DT)
    assert op.effective_atk() == base_atk + int(base_atk * 1.80)

    # run duration (15s = 150 ticks)
    for _ in range(150):
        op.update_skill(DT)
    assert not op.skill_active, "Skill should have ended"
    assert op._atk_bonus == 0, "on_end should clear the bonus"
    assert op.effective_atk() == base_atk


def test_skill_does_not_gain_sp_while_active():
    """During the active window, SP should not accumulate further."""
    op = make_silverash()
    for _ in range(200):
        op.update_skill(DT)
    # Now active — 50 more ticks (5s), SP must stay 0
    for _ in range(50):
        op.update_skill(DT)
    assert op.sp == 0.0


def test_auto_attack_sp_gain_mode():
    """auto_attack mode accrues SP per hit landed, not per second."""
    target = Enemy(
        name="Dummy", max_hp=5000, atk=0, defence=0, res=0,
        atk_interval=99.0, attack_type="physical",
    )

    def noop(_op: Operator) -> None:
        pass

    op = Operator(
        name="Melee", max_hp=1000, atk=400, defence=0, res=0,
        atk_interval=1.0, block=1, attack_type="physical",
        sp_gain_per_attack=1.0,
    )
    op.skill = Skill(
        name="Noop Burst", sp_cost=3.0, duration=5.0,
        sp_gain_mode="auto_attack", on_start=noop, on_end=noop,
    )

    # 3 attacks ⇒ 3 SP (at cost)
    for _ in range(3):
        op.attack(target)
    assert op.sp == 3.0
    # Next update should activate
    op.update_skill(DT)
    assert op.skill_active


# ---- Integration: SilverAsh burst demo --------------------------------------


def test_silverash_beats_arts_master():
    silverash = make_silverash()
    arts_master = make_arts_master()
    battle = Battle(operators=[silverash], enemies=[arts_master], max_lives=3)
    result = battle.run(max_seconds=60.0)

    assert result == "win", (
        f"Expected win, got {result}\n{battle.log.dump()}"
    )
    assert silverash.alive, "SilverAsh should outlive Arts Master"
    assert not arts_master.alive
    # Confirm skill actually fired — log must record activation
    assert any("activates Truesilver Slash" in e for e in battle.log.entries), (
        "Skill activation not logged — did update_skill wire in?"
    )


def test_without_skill_silverash_loses_or_stalls():
    """Sanity check: remove the skill and SilverAsh should NOT be able
    to win inside the 60s window. If this test ever passes the win-case,
    the skill isn't actually load-bearing in the burst demo."""
    silverash = make_silverash()
    silverash.skill = None  # strip the burst
    arts_master = make_arts_master()
    battle = Battle(operators=[silverash], enemies=[arts_master], max_lives=3)
    result = battle.run(max_seconds=60.0)

    assert result != "win", (
        f"SilverAsh shouldn't win without skill — demo is not load-bearing.\n"
        f"{battle.log.dump()}"
    )
