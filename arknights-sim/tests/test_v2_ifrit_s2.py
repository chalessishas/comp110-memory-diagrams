"""Ifrit S2 "Combustion" — instant AOE arts burst + initial_sp seeding."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, AttackType, Profession
from core.systems import register_default_systems
from data.characters.ifrit import make_ifrit


def _enemy(hp: int = 5000, res: float = 0.0, pos=(2.0, 0.0)) -> UnitState:
    e = UnitState(name="dummy_enemy", faction=Faction.ENEMY, max_hp=hp)
    e.res = res
    e.deployed = True
    e.position = pos
    return e


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            tile_type = TileType.ELEVATED if y == 1 else TileType.GROUND
            grid.set_tile(TileState(x=x, y=y, type=tile_type))
    w = World(tile_grid=grid)
    w.global_state.dp = 99
    register_default_systems(w)
    return w


def test_initial_sp_seeded_on_deploy():
    """initial_sp=10 is applied when ranged operator is deployed on ELEVATED tile."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)   # elevated tile — ranged operator allowed
    result = w.deploy(op)
    assert result is True, "deploy on elevated must succeed for ranged operator"
    assert op.skill.sp == 10.0, f"expected 10 initial SP, got {op.skill.sp}"


def test_s2_is_instant_no_active_remaining():
    """After S2 fires, active_remaining == 0 (instant skill, not sustained)."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    op.atk_cd = 999.0   # block regular attacks
    w.add_unit(op)

    enemy = _enemy()
    w.add_unit(enemy)
    op.__target__ = enemy

    op.skill.sp = op.skill.sp_cost  # force ready
    w.tick()

    assert op.skill.active_remaining == 0.0, "instant skill must not set active_remaining"
    assert op.skill.sp == 0.0, "SP must reset to 0 after instant fire"
    assert op.skill.fire_count == 1


def test_s2_deals_arts_damage_to_enemy_in_range():
    """S2 deals floor(ATK*2.60) arts damage (respecting RES) to target in range."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    op.atk_cd = 999.0   # block regular attacks so only S2 damage is counted
    w.add_unit(op)

    enemy = _enemy(hp=10000, res=0.0, pos=(2.0, 1.0))  # (2,0) relative → in range
    w.add_unit(enemy)
    op.__target__ = enemy

    burst_atk = int(math.floor(op.atk * 2.60))
    expected = max(1, int(burst_atk * 1.0))  # RES=0

    op.skill.sp = op.skill.sp_cost
    w.tick()

    assert enemy.hp == enemy.max_hp - expected, (
        f"expected {expected} dmg, got {enemy.max_hp - enemy.hp}"
    )


def test_s2_respects_res():
    """Arts damage is reduced by enemy RES (50% RES → 50% damage)."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = _enemy(hp=10000, res=50.0, pos=(2.0, 1.0))
    w.add_unit(enemy)
    op.__target__ = enemy

    burst_atk = int(math.floor(op.atk * 2.60))
    expected = max(1, int(burst_atk * 0.50))

    op.skill.sp = op.skill.sp_cost
    w.tick()

    assert enemy.hp == enemy.max_hp - expected, (
        f"expected {expected} dmg with 50% RES, got {enemy.max_hp - enemy.hp}"
    )


def test_s2_hits_all_enemies_in_range():
    """S2 AOE hits every enemy within range simultaneously."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    # Three enemies in range (tiles (1,0), (2,0), (3,0) relative to op at y=1 → abs (1,1),(2,1),(3,1))
    e1 = _enemy(hp=10000, pos=(1.0, 1.0))
    e2 = _enemy(hp=10000, pos=(2.0, 1.0))
    e3 = _enemy(hp=10000, pos=(3.0, 1.0))
    for e in (e1, e2, e3):
        w.add_unit(e)
    op.__target__ = e1

    op.skill.sp = op.skill.sp_cost
    w.tick()

    assert e1.hp < e1.max_hp, "e1 must be hit"
    assert e2.hp < e2.max_hp, "e2 must be hit"
    assert e3.hp < e3.max_hp, "e3 must be hit"
    assert e1.hp == e2.hp == e3.hp, "identical enemies in range get identical damage"


def test_s2_does_not_hit_enemy_outside_range():
    """Enemy outside Ifrit's range takes no damage from S2."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    w.add_unit(op)

    in_range = _enemy(hp=5000, pos=(2.0, 1.0))
    out_range = _enemy(hp=5000, pos=(5.0, 1.0))  # dx=5, beyond range (max dx=3)
    w.add_unit(in_range)
    w.add_unit(out_range)
    op.__target__ = in_range

    op.skill.sp = op.skill.sp_cost
    w.tick()

    assert in_range.hp < in_range.max_hp, "in-range enemy must be hit"
    assert out_range.hp == out_range.max_hp, "out-of-range enemy must be untouched"


def test_s2_sp_recharges_and_fires_again():
    """After first instant fire, Ifrit recharges and fires S2 a second time."""
    w = _world()
    op = make_ifrit()
    op.position = (0.0, 1.0)
    op.deployed = True
    w.add_unit(op)

    enemy = _enemy(hp=999999, res=0.0, pos=(2.0, 1.0))
    w.add_unit(enemy)
    op.__target__ = enemy

    # Force first fire
    op.skill.sp = op.skill.sp_cost
    w.tick()
    assert op.skill.fire_count == 1

    # Advance until SP refills (22s AUTO_TIME)
    for _ in range(int(22 / DT) + 5):
        w.tick()

    assert op.skill.fire_count == 2, "S2 should have fired a second time"
