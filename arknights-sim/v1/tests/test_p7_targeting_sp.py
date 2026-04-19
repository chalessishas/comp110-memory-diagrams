"""P7: targeting priority (highest path_progress) + SP lockout (orange meter)."""
from __future__ import annotations
import pytest
from core.battle import Battle, DT
from core.operator import Operator
from core.enemy import Enemy
from core.skill import Skill
from data.operators import make_exusiai, make_silverash


PATH = [(x, 2) for x in range(8)]


def _enemy(name: str = "E", hp: int = 5000, progress: float = 0.0) -> Enemy:
    e = Enemy(
        name=name, max_hp=hp, atk=0, defence=0, res=0,
        atk_interval=99.0, attack_type="physical",
        path=PATH, speed=0.0,
    )
    e._path_progress = progress
    return e


# ---- Targeting priority -------------------------------------------------------


def test_ranged_targets_highest_path_progress():
    """Ranged op must attack the enemy closest to the goal, not the first in list."""
    op = make_exusiai()  # ranged
    near = _enemy("Near", hp=9999, progress=1.0)   # tile (1,2)
    far = _enemy("Far", hp=9999, progress=5.0)     # tile (5,2) — closest to goal

    battle = Battle(operators=[op], enemies=[near, far], max_lives=3)
    op._atk_cd = -99.0   # guarantee attack fires
    battle._resolve_operators()

    # far (progress=5.0) should be the target
    assert far.hp < far.max_hp, "Enemy closest to goal must be targeted"
    assert near.hp == near.max_hp, "Enemy with lower progress should not be attacked"


def test_ranged_targeting_skips_dead_enemies():
    """Ranged targeting must ignore dead enemies even if they have highest progress."""
    op = make_exusiai()
    dead_high = _enemy("Dead", hp=1, progress=7.0)
    live_low = _enemy("Live", hp=9999, progress=1.0)

    dead_high.alive = False   # pre-kill highest-progress enemy

    battle = Battle(operators=[op], enemies=[dead_high, live_low], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert live_low.hp < live_low.max_hp, "Live enemy should be targeted, not dead one"


def test_melee_targeting_unchanged_by_priority():
    """Melee targeting still uses block assignments, not path_progress sort."""
    from core.operator import Operator as Op
    op = Op(
        name="Melee", max_hp=3000, atk=500, defence=300, res=0,
        atk_interval=1.0, block=1, attack_type="physical",
    )
    enemy_low = _enemy("Low", hp=500, progress=0.5)
    enemy_high = _enemy("High", hp=500, progress=3.0)

    battle = Battle(operators=[op], enemies=[enemy_low, enemy_high], max_lives=3)
    # Let battle engine assign blocks normally (both enemies → only 1 slot)
    battle._tick()  # one full tick: assigns block, attacks

    # Melee only attacks the one it's blocking (first assigned to its 1 block slot)
    # Exactly 1 enemy should have taken damage
    damaged = sum(1 for e in [enemy_low, enemy_high] if e.hp < e.max_hp)
    assert damaged == 1, "Melee operator with block=1 should only damage one enemy"


# ---- SP Lockout ----------------------------------------------------------------


def test_sp_does_not_fire_without_target():
    """When SP is full but has_target=False, skill must not fire."""
    op = make_silverash()
    # Accumulate to full SP (200 ticks) without a target
    for _ in range(200):
        op.update_skill(DT, has_target=False)
    assert op.sp >= op.skill.sp_cost, "SP should reach cost"
    assert not op.skill_active, "Skill must NOT fire without a target"
    assert op._sp_locked, "Operator must enter SP lockout state"


def test_sp_fires_immediately_when_target_appears():
    """After lockout, skill fires on the very first tick where has_target=True."""
    op = make_silverash()
    for _ in range(200):
        op.update_skill(DT, has_target=False)
    assert op._sp_locked

    op.update_skill(DT, has_target=True)
    assert op.skill_active, "Skill should fire immediately when target appears"
    assert not op._sp_locked, "Lockout cleared when skill fires"


def test_sp_accumulates_normally_with_target():
    """Normal case: has_target=True throughout → skill fires as before."""
    op = make_silverash()
    for _ in range(199):
        op.update_skill(DT, has_target=True)
    assert not op.skill_active
    op.update_skill(DT, has_target=True)
    assert op.skill_active
    assert not op._sp_locked


def test_sp_lockout_in_full_battle():
    """SilverAsh skill should only fire once enemies are present (after wave spawns)."""
    from core.battle import SpawnEvent
    from data.enemies import make_arts_master

    sa = make_silverash()
    # Enemy spawns at t=25s (after SilverAsh would hit full SP at t=20s)
    arts = make_arts_master(path=PATH)
    battle = Battle(
        operators=[sa],
        enemies=[],
        max_lives=3,
        spawn_queue=[SpawnEvent(time=25.0, enemy=arts)],
    )
    result = battle.run(max_seconds=90.0)

    assert result == "win"
    assert any("activates Truesilver Slash" in e for e in battle.log.entries), (
        "Skill must fire after enemies appear, not before"
    )
    # Skill should not have fired at t=20s (no enemy); first fire must be ≥ t=25s
    first_activation = next(
        e for e in battle.log.entries if "activates Truesilver Slash" in e
    )
    activation_time = float(first_activation.split("t=")[1].split()[0])
    assert activation_time >= 25.0, (
        f"Skill fired at {activation_time}s but enemy only spawned at 25s"
    )
