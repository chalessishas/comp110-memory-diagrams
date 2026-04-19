"""P8: enemy visibility — is_invisible + has_true_sight + ranged targeting gate."""
from __future__ import annotations
import pytest
from core.battle import Battle, DT
from core.operator import Operator
from core.enemy import Enemy
from data.operators import make_exusiai


PATH = [(x, 2) for x in range(8)]


def _enemy(name: str = "E", hp: int = 5000, progress: float = 0.0,
           invisible: bool = False) -> Enemy:
    e = Enemy(
        name=name, max_hp=hp, atk=0, defence=0, res=0,
        atk_interval=99.0, attack_type="physical",
        path=PATH, speed=0.0,
        is_invisible=invisible,
    )
    e._path_progress = progress
    return e


# ── Ranged cannot target invisible ─────────────────────────────────────────────

def test_ranged_cannot_target_invisible():
    """Ranged op without true sight must NOT attack an invisible enemy."""
    op = make_exusiai()   # has_true_sight=False by default
    ghost = _enemy("Ghost", invisible=True)

    battle = Battle(operators=[op], enemies=[ghost], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert ghost.hp == ghost.max_hp, "Ranged op should not be able to target invisible enemy"


def test_ranged_with_true_sight_targets_invisible():
    """Ranged op with has_true_sight=True MUST be able to attack invisible enemy."""
    op = make_exusiai()
    op.has_true_sight = True
    ghost = _enemy("Ghost", invisible=True)

    battle = Battle(operators=[op], enemies=[ghost], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert ghost.hp < ghost.max_hp, "True-sight operator must be able to hit invisible enemy"


# ── Melee is unaffected by visibility ──────────────────────────────────────────

def test_melee_blocks_invisible():
    """Melee blocking is physical — visibility flag must NOT prevent melee attacks."""
    op = Operator(
        name="Melee", max_hp=3000, atk=500, defence=300, res=0,
        atk_interval=1.0, block=1, attack_type="physical",
    )
    ghost = _enemy("Ghost", hp=1000, invisible=True)

    battle = Battle(operators=[op], enemies=[ghost], max_lives=3)
    battle._tick()  # one full tick assigns block and fires attack

    assert ghost.hp < ghost.max_hp, "Melee operator must still hit a blocked invisible enemy"


# ── Mixed visibility: visible always preferred when invisible not targetable ────

def test_ranged_skips_invisible_targets_visible():
    """When both visible and invisible enemies exist, ranged targets the visible one
    even when the invisible enemy has higher path_progress."""
    op = make_exusiai()   # no true_sight
    ghost = _enemy("Ghost", hp=9999, progress=6.0, invisible=True)   # closer to goal
    visible = _enemy("Visible", hp=9999, progress=1.0, invisible=False)

    battle = Battle(operators=[op], enemies=[ghost, visible], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert visible.hp < visible.max_hp, "Ranged must target visible enemy"
    assert ghost.hp == ghost.max_hp, "Invisible enemy must not be targeted without true sight"


# ── Invisible enemy reaches goal if never targeted ────────────────────────────

def test_invisible_enemy_reaches_goal_unchecked():
    """Invisible enemy, with no true-sight operator present, slips through and
    decrements lives."""
    op = make_exusiai()   # no true_sight
    ghost = Enemy(
        name="Ghost", max_hp=500, atk=0, defence=0, res=0,
        atk_interval=99.0, attack_type="physical",
        path=PATH, speed=2.0,    # fast enough to reach goal within test window
        is_invisible=True,
    )

    battle = Battle(operators=[op], enemies=[ghost], max_lives=3)
    result = battle.run(max_seconds=10.0)

    assert battle.lives < battle.max_lives, "Invisible enemy must reach goal and cost a life"
