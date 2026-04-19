"""Ch'en S2 "Sheathed Strike" — MANUAL trigger + AUTO_ATTACK SP gain."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, DT, Faction, AttackType
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.chen import make_chen


def _enemy(hp: int = 5000, res: float = 0.0, pos=(1.0, 0.0)) -> UnitState:
    e = UnitState(name="dummy", faction=Faction.ENEMY, max_hp=hp)
    e.res = res
    e.deployed = True
    e.position = pos
    return e


def _world() -> World:
    grid = TileGrid(width=5, height=2)
    for x in range(5):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = 99
    register_default_systems(w)
    return w


def test_manual_skill_does_not_auto_fire():
    """MANUAL skill must not fire even when SP is full — requires explicit trigger."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = _enemy()
    w.add_unit(enemy)
    op.__target__ = enemy

    op.skill.sp = op.skill.sp_cost  # SP is ready
    for _ in range(10):
        w.tick()

    assert op.skill.fire_count == 0, "MANUAL skill must not auto-fire when SP full"
    assert enemy.hp == enemy.max_hp, "no damage before manual trigger"


def test_manual_trigger_fires_skill():
    """manual_trigger() fires the skill when SP >= sp_cost."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = _enemy(hp=10000)
    w.add_unit(enemy)
    op.__target__ = enemy

    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)

    assert op.skill.fire_count == 1
    assert enemy.hp < enemy.max_hp, "enemy must take damage after manual trigger"


def test_manual_trigger_blocked_when_sp_insufficient():
    """manual_trigger() does nothing if SP < sp_cost."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = _enemy(hp=10000)
    w.add_unit(enemy)

    op.skill.sp = op.skill.sp_cost - 1   # one short
    manual_trigger(w, op)

    assert op.skill.fire_count == 0, "must not fire without enough SP"
    assert enemy.hp == enemy.max_hp


def test_s2_damage_formula():
    """S2 deals floor(ATK*3.80) arts damage (respecting target RES)."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = _enemy(hp=10000, res=0.0, pos=(1.0, 0.0))
    w.add_unit(enemy)
    op.__target__ = enemy

    burst_atk = int(math.floor(op.atk * 3.80))
    expected = max(1, int(burst_atk * 1.0))

    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)

    assert enemy.hp == enemy.max_hp - expected, (
        f"expected {expected} dmg, got {enemy.max_hp - enemy.hp}"
    )


def test_s2_hits_all_enemies_in_range():
    """S2 AOE arts burst hits every enemy in range simultaneously."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    op.atk_cd = 999.0
    w.add_unit(op)

    # LORD_RANGE: (0,0), (1,0), (2,0)
    e1 = _enemy(hp=5000, pos=(0.0, 0.0))   # dx=0 — in range
    e2 = _enemy(hp=5000, pos=(1.0, 0.0))   # dx=1 — in range
    e3 = _enemy(hp=5000, pos=(2.0, 0.0))   # dx=2 — in range
    e4 = _enemy(hp=5000, pos=(3.0, 0.0))   # dx=3 — out of range
    for e in (e1, e2, e3, e4):
        w.add_unit(e)
    op.__target__ = e1

    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)

    assert e1.hp < e1.max_hp, "e1 (dx=0) must be hit"
    assert e2.hp < e2.max_hp, "e2 (dx=1) must be hit"
    assert e3.hp < e3.max_hp, "e3 (dx=2) must be hit"
    assert e4.hp == e4.max_hp, "e4 (dx=3, out of range) must not be hit"


def test_sp_charges_on_attack():
    """AUTO_ATTACK SP mode: each basic attack charges +1 SP."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)
    op.deployed = True
    # start with initial_sp=10 would be set by deploy, but using add_unit bypass
    op.skill.sp = 0.0
    w.add_unit(op)

    enemy = _enemy(hp=999999)
    w.add_unit(enemy)
    op.__target__ = enemy

    sp_before = op.skill.sp
    # Let one attack land
    op.atk_cd = 0.0
    w.tick()
    w.tick()   # combat tick: attack fires, sp gains +1

    assert op.skill.sp > sp_before, "SP must increase after an attack"


def test_initial_sp_seeded_on_deploy():
    """initial_sp=10 is seeded when Ch'en is deployed via world.deploy()."""
    w = _world()
    op = make_chen()
    op.position = (0.0, 0.0)   # GROUND tile — melee allowed
    result = w.deploy(op)
    assert result is True
    assert op.skill.sp == 10.0, f"expected initial_sp=10, got {op.skill.sp}"
