"""P2 acceptance test: main_0-1 clears with 2 operators, 3 lives remaining."""
import os
import pytest
from core.operator import Operator
from stages.loader import load_stage, stage_to_battle

STAGE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "stages", "main_0-1.yaml"
)


def make_liskarm() -> Operator:
    return Operator(
        name="Liskarm",
        max_hp=2000, atk=480, defence=500, res=0,
        atk_interval=1.05, block=1, attack_type="physical",
    )


def make_hoshiguma() -> Operator:
    return Operator(
        name="Hoshiguma",
        max_hp=3200, atk=436, defence=800, res=0,
        atk_interval=1.15, block=3, attack_type="physical",
    )


def test_main_0_1_clears():
    stage = load_stage(STAGE_PATH)
    battle = stage_to_battle(stage, operators=[make_liskarm(), make_hoshiguma()])
    result = battle.run()

    assert result == "win", (
        f"Expected win, got {result}\n{battle.log.dump()}"
    )
    assert battle.lives == 3, (
        f"Expected 3 lives, got {battle.lives}\n{battle.log.dump()}"
    )


def test_stage_loads_correctly():
    stage = load_stage(STAGE_PATH)
    assert stage.id == "main_0-1"
    assert stage.max_lives == 3
    assert len(stage.enemy_specs) == 1
    spec = stage.enemy_specs[0]
    assert spec.enemy_id == "originium_slug"
    assert spec.count == 5
    assert spec.interval == 4.0
    assert len(spec.path) == 8


def test_wave_spawning_order():
    """Enemies must spawn at correct intervals, not all at once."""
    stage = load_stage(STAGE_PATH)
    battle = stage_to_battle(stage, operators=[make_liskarm(), make_hoshiguma()])

    # Initially no active enemies — all in spawn queue
    assert len(battle.enemies) == 0
    assert len(battle.spawn_queue) == 5

    # First enemy spawns at t=0 (first tick at t=DT)
    assert battle.spawn_queue[0].time == 0.0
    assert battle.spawn_queue[1].time == 4.0
    assert battle.spawn_queue[4].time == 16.0


def test_enemy_path_advancement():
    """Enemy without a blocker should advance along path and reach goal."""
    from core.enemy import Enemy
    from core.battle import Battle, SpawnEvent

    slug = Enemy(
        name="Slug",
        max_hp=1300, atk=280, defence=0, res=0,
        atk_interval=1.5, attack_type="physical",
        path=[(0, 0), (1, 0), (2, 0)],  # 2 tiles to traverse
        speed=1.0,
    )
    # No operators, max_lives=1 → losing 1 life = game over
    battle = Battle(operators=[], enemies=[], max_lives=1,
                    spawn_queue=[SpawnEvent(time=0.0, enemy=slug)])
    result = battle.run(max_seconds=10.0)

    assert result == "loss", f"Expected loss (slug reaches goal), got {result}"
    assert battle.lives == 0, f"Expected 0 lives, got {battle.lives}"
