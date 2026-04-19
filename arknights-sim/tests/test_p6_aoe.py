"""P6 acceptance: AOE splash damage (Euclidean radius, magic & physical)."""
from __future__ import annotations
from core.battle import Battle, DT
from core.operator import Operator
from core.enemy import Enemy
from data.operators import make_angelina


PATH = [(x, 2) for x in range(8)]  # horizontal 8-tile path


def _slug(hp: int = 2000, progress: float = 0.0) -> Enemy:
    e = Enemy(
        name="Slug", max_hp=hp, atk=0, defence=0, res=0,
        atk_interval=99.0, attack_type="physical",
        path=PATH, speed=0.0,  # speed=0 → never advances on its own
    )
    e._path_progress = progress
    return e


def test_tile_pos_snaps_to_path_index():
    e = _slug(progress=1.7)
    assert e.tile_pos == (1, 2), "tile_pos should floor to nearest integer index"


def test_splash_hits_adjacent_enemy():
    """AOE op at radius=1.5 attacks slug at tile 0; slug at tile 1 (dist=1.0) also hit."""
    op = make_angelina()   # splash_radius=1.2, magic, ranged
    primary = _slug(hp=5000, progress=0.0)    # tile (0,2)
    nearby = _slug(hp=5000, progress=1.0)     # tile (1,2), dist=1.0 ≤ 1.2
    primary_hp_before = primary.hp
    nearby_hp_before = nearby.hp

    battle = Battle(operators=[op], enemies=[primary, nearby], max_lives=3)
    battle._tick()   # one tick — op fires if atk_cd <= 0 initially

    # Force op to fire by advancing cd past threshold
    op._atk_cd = -99.0   # guarantee attack fires on next tick
    battle._resolve_operators()

    assert primary.hp < primary_hp_before, "Primary target must take damage"
    assert nearby.hp < nearby_hp_before, "Nearby enemy within radius must take splash damage"


def test_splash_misses_distant_enemy():
    """Enemy at tile 3 (dist=3.0 > 1.2) should NOT take splash damage."""
    op = make_angelina()
    primary = _slug(hp=5000, progress=0.0)    # tile (0,2)
    far = _slug(hp=5000, progress=3.0)        # tile (3,2), dist=3.0 > 1.2
    far_hp_before = far.hp

    battle = Battle(operators=[op], enemies=[primary, far], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert far.hp == far_hp_before, "Distant enemy must not take splash damage"


def test_no_splash_when_radius_zero():
    """Physical melee op with splash_radius=0 must not splash."""
    op = Operator(
        name="Melee", max_hp=2000, atk=500, defence=200, res=0,
        atk_interval=1.0, block=2, attack_type="physical",
        splash_radius=0.0,
    )
    primary = _slug(hp=5000, progress=0.0)
    nearby = _slug(hp=5000, progress=1.0)
    nearby_hp_before = nearby.hp

    battle = Battle(operators=[op], enemies=[primary, nearby], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    assert nearby.hp == nearby_hp_before, "No splash when radius=0"


def test_splash_damage_uses_magic_formula():
    """Angelina's magic splash respects RES: target with RES=50 takes ~50% damage."""
    op = make_angelina()  # atk=580, magic
    primary = _slug(hp=9999, progress=0.0)
    resistant = Enemy(
        name="Resistant", max_hp=9999, atk=0, defence=0, res=50,
        atk_interval=99.0, attack_type="physical",
        path=PATH, speed=0.0,
    )
    resistant._path_progress = 0.8   # tile (0,2) same as primary, dist=0.0 ≤ 1.2

    resistant_hp_before = resistant.hp
    battle = Battle(operators=[op], enemies=[primary, resistant], max_lives=3)
    op._atk_cd = -99.0
    battle._resolve_operators()

    expected_dmg = max(1, int(op.atk * (1 - 50 / 100)))  # 290
    actual_dmg = resistant_hp_before - resistant.hp
    assert actual_dmg == expected_dmg, (
        f"Magic formula: expected {expected_dmg} splash dmg, got {actual_dmg}"
    )


def test_aoe_caster_clears_clustered_wave():
    """Angelina should clear a cluster of low-HP enemies faster than single-target."""
    import copy
    op_aoe = make_angelina()
    op_single = make_angelina()
    op_single.splash_radius = 0.0   # strip AOE

    slugs_aoe = [_slug(hp=300, progress=float(i % 2)) for i in range(4)]
    slugs_single = [_slug(hp=300, progress=float(i % 2)) for i in range(4)]

    battle_aoe = Battle(operators=[op_aoe], enemies=slugs_aoe, max_lives=10)
    battle_single = Battle(operators=[op_single], enemies=slugs_single, max_lives=10)

    result_aoe = battle_aoe.run(max_seconds=30.0)
    result_single = battle_single.run(max_seconds=30.0)

    assert result_aoe == "win"
    assert battle_aoe.elapsed < battle_single.elapsed or result_single != "win", (
        "AOE operator should clear clustered enemies at least as fast as single-target"
    )
