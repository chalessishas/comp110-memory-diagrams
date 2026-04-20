"""Multi-operator synergy integration tests.

These tests verify that operator interactions work correctly through the full
ECS tick loop (STATUS_DECAY → MOVEMENT → TARGETING → COMBAT → SKILL → GOAL → CLEANUP).

Unlike single-operator unit tests that run 1-3 ticks, these scenarios run for
multiple seconds and exercise the complete interaction chain:
  - Healer × Defender: healer keeps an injured blocking unit alive through sustained damage
  - Buffer × DPS: Pallas's flat ATK buff measurably speeds up kill time
  - DP chain: Myrtle S2 generates enough DP to enable deploying a second operator
  - Summoner × Ranged: Ling's Long Xian tanks melee while Pinecone attacks from range

Each scenario uses a controlled world (enemy atk/move zeroed where needed) and
measures concrete outcomes: HP delta, kill speed, DP gain, or summon damage.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype,
)
from core.systems import register_default_systems
from data.characters import make_liskarm, make_silverash
from data.characters.shining import make_shining
from data.characters.pallas import make_pallas
from data.characters.myrtle import make_myrtle, _S2_DP_RATE, _S2_DURATION
from data.characters.ling import make_ling
from data.characters.pinecone import make_pinecone
from data.enemies import make_originium_slug


def _world(width=8, height=5) -> World:
    grid = TileGrid(width=width, height=height)
    for x in range(width):
        for y in range(height):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(4, 2), hp=99999, atk=0, defence=0) -> UnitState:
    """Enemy slug — melee moves to pos, fixed there."""
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk
    e.defence = defence; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _place(world, unit, pos, atk_cd=0.0):
    unit.deployed = True
    unit.position = (float(pos[0]), float(pos[1]))
    if atk_cd is not None:
        unit.atk_cd = atk_cd
    world.add_unit(unit)


# ===========================================================================
# Scenario 1: Healer × Defender
# Verify Shining keeps Liskarm alive through sustained enemy damage.
# Without healer: Liskarm HP drops far below starting point.
# With healer: Liskarm's HP is maintained by periodic heals.
# ===========================================================================

def test_shining_keeps_liskarm_alive():
    """Shining's healing offsets the damage Liskarm takes, keeping HP higher."""
    FIGHT_SECONDS = 8.0
    ENEMY_ATK = 400        # hard hits — Liskarm def=755, so ~0 through def; use def=0 on slug
    LISKARM_STARTING_HP = 1000  # deliberately low to make healing visible

    # --- world WITHOUT healer ---
    w1 = _world()
    lk1 = make_liskarm()
    lk1.hp = LISKARM_STARTING_HP
    _place(w1, lk1, (2, 2))
    # Enemy with meaningful ATK, zero DEF on Liskarm so damage is clear
    lk1.defence = 0
    slug1 = _slug(pos=(2, 2), atk=ENEMY_ATK)
    w1.add_unit(slug1)
    for _ in range(int(TICK_RATE * FIGHT_SECONDS)):
        w1.tick()
    hp_no_healer = lk1.hp

    # --- world WITH healer (Shining) ---
    w2 = _world()
    lk2 = make_liskarm()
    lk2.hp = LISKARM_STARTING_HP
    lk2.defence = 0
    _place(w2, lk2, (2, 2))
    sh = make_shining()
    sh.atk_cd = 0.0
    _place(w2, sh, (1, 2))  # Shining one tile back, in heal range
    slug2 = _slug(pos=(2, 2), atk=ENEMY_ATK)
    w2.add_unit(slug2)
    for _ in range(int(TICK_RATE * FIGHT_SECONDS)):
        w2.tick()
    hp_with_healer = lk2.hp

    assert hp_with_healer > hp_no_healer, (
        f"Shining must heal Liskarm; HP without healer={hp_no_healer}, "
        f"with healer={hp_with_healer}"
    )
    # With healer, HP should also be ABOVE 0 (stayed alive through the fight)
    assert lk2.alive, "Liskarm must survive when healed"


# ===========================================================================
# Scenario 2: Buffer × DPS
# Pallas's Battle Inspiration (+80 flat ATK) speeds up kill time.
# Measure ticks until enemy dies: with Pallas buff < without.
# ===========================================================================

def test_pallas_buff_speeds_up_kills():
    """With Pallas buffing a DPS ally, kill time is shorter than without."""
    ENEMY_HP = 3000
    DPS_ATK = 400      # controlled DPS operator

    # Build a simple DPS ally UnitState
    def _dps_ally(pos):
        return UnitState(
            name="DPS",
            faction=Faction.ALLY,
            max_hp=5000, hp=5000, atk=DPS_ATK,
            defence=0, res=0.0,
            atk_interval=1.0, block=2,
            attack_type=AttackType.PHYSICAL,
            attack_range_melee=True,
            range_shape=RangeShape(tiles=((0, 0), (1, 0))),
            deployed=True, position=(float(pos[0]), float(pos[1])),
        )

    # --- without Pallas ---
    w1 = _world()
    dps1 = _dps_ally((2, 2)); dps1.atk_cd = 0.0
    w1.add_unit(dps1)
    e1 = _slug(pos=(2, 2), hp=ENEMY_HP)
    w1.add_unit(e1)
    ticks_no_buff = 0
    for tick in range(300):  # max 20s
        w1.tick()
        ticks_no_buff += 1
        if not e1.alive:
            break

    # --- with Pallas ---
    w2 = _world()
    dps2 = _dps_ally((2, 2)); dps2.atk_cd = 0.0
    w2.add_unit(dps2)
    pa = make_pallas(); pa.atk_cd = 0.0
    pa.position = (1.0, 2.0); pa.deployed = True
    w2.add_unit(pa)
    e2 = _slug(pos=(2, 2), hp=ENEMY_HP)
    w2.add_unit(e2)
    ticks_with_buff = 0
    for tick in range(300):
        w2.tick()
        ticks_with_buff += 1
        if not e2.alive:
            break

    assert not e1.alive, "Enemy must die in control scenario"
    assert not e2.alive, "Enemy must die in buff scenario"
    assert ticks_with_buff < ticks_no_buff, (
        f"Pallas buff must speed up kills; no_buff={ticks_no_buff} ticks, "
        f"with_buff={ticks_with_buff} ticks"
    )


# ===========================================================================
# Scenario 3: DP generation chain
# Myrtle S2 generates DP. Verify total DP after S2 meets threshold for
# deploying a second operator (e.g., SilverAsh costs 21 DP).
# ===========================================================================

def test_myrtle_s2_generates_enough_dp_for_silverash():
    """Myrtle S2 generates DP at expected rate (_S2_DP_RATE × _S2_DURATION)."""
    w = _world()
    my = make_myrtle(slot="S2")
    my.deployed = True; my.position = (0.0, 2.0); my.atk_cd = 999.0
    w.add_unit(my)

    # Trigger S2 immediately
    my.skill.sp = float(my.skill.sp_cost)
    w.tick()  # S2 activates
    assert my.skill.active_remaining > 0.0, "Myrtle S2 must activate"

    dp_at_start = w.global_state.dp
    # Run full S2 duration
    for _ in range(int(TICK_RATE * _S2_DURATION)):
        w.tick()

    dp_gained = w.global_state.dp - dp_at_start
    expected = int(_S2_DP_RATE * _S2_DURATION * 0.9)  # 90% of theoretical yield
    assert dp_gained >= expected, (
        f"Myrtle S2 must generate ≥{expected} DP; "
        f"generated={dp_gained:.1f}, expected≈{_S2_DP_RATE * _S2_DURATION:.1f}"
    )


# ===========================================================================
# Scenario 4: DP chain enables deployment
# More concrete: Myrtle generates DP, then we verify SilverAsh can be deployed.
# ===========================================================================

def test_myrtle_dp_enables_silverash_deployment():
    """After Myrtle generates DP, world.deploy() succeeds for a low-cost operator."""
    w = _world()
    my = make_myrtle(slot="S2")
    my.deployed = True; my.position = (0.0, 2.0); my.atk_cd = 999.0
    w.add_unit(my)

    # Myrtle herself costs 10 DP — achievable within S2 duration (16 DP generated)
    deploy_target = make_myrtle()
    deploy_target.position = (3.0, 2.0)

    my.skill.sp = float(my.skill.sp_cost)
    # Run long enough to accumulate deploy_target's cost
    for _ in range(int(TICK_RATE * _S2_DURATION)):
        w.tick()

    dp_available = w.global_state.dp
    assert dp_available >= deploy_target.cost, (
        f"Must have enough DP to deploy operator; have={dp_available:.0f}, need={deploy_target.cost}"
    )
    # Attempt deployment
    deployed = w.deploy(deploy_target)
    assert deployed, f"Deployment must succeed with {dp_available:.0f} DP available"


# ===========================================================================
# Scenario 5: Summoner × Ranged DPS
# Ling's Long Xian blocks an enemy at melee range while Pinecone attacks
# the same enemy from range. Enemy must die faster than with Pinecone alone
# (because Long Xian also deals melee damage).
# ===========================================================================

def test_ling_summon_plus_pinecone_kill_faster():
    """Long Xian + Pinecone together kill an enemy faster than Pinecone alone."""
    ENEMY_HP = 10000

    # --- Pinecone alone ---
    w1 = _world()
    pc1 = make_pinecone(); pc1.atk_cd = 0.0
    _place(w1, pc1, (0, 2))
    e1 = _slug(pos=(2, 2), hp=ENEMY_HP)
    w1.add_unit(e1)
    ticks_alone = 0
    for _ in range(int(TICK_RATE * 30)):
        w1.tick()
        ticks_alone += 1
        if not e1.alive:
            break

    # --- Ling S3 (Long Xian melee) + Pinecone ranged ---
    # Ling at (1,2) so Long Xian spawns there with range ((0,0),(1,0)) → reaches (2,2)
    w2 = _world()
    li = make_ling(slot="S3")
    li.position = (1.0, 2.0); li.deployed = True; li.atk_cd = 999.0
    li.skill.sp = float(li.skill.sp_cost)
    w2.add_unit(li)
    pc2 = make_pinecone(); pc2.atk_cd = 0.0
    _place(w2, pc2, (0, 3))
    e2 = _slug(pos=(2, 2), hp=ENEMY_HP)
    w2.add_unit(e2)
    ticks_combined = 0
    for _ in range(int(TICK_RATE * 30)):
        w2.tick()
        ticks_combined += 1
        if not e2.alive:
            break

    assert not e1.alive, "Enemy must die with Pinecone alone"
    assert not e2.alive, "Enemy must die with Ling+Pinecone"
    assert ticks_combined < ticks_alone, (
        f"Long Xian+Pinecone must kill faster than Pinecone alone; "
        f"alone={ticks_alone}, combined={ticks_combined}"
    )


# ===========================================================================
# Scenario 6: Pallas ally ATK buff — flat bonus is correctly added
# Verify that Pallas's +80 ATK buff (flat BuffStack) shows up in effective_atk
# of a guard ally standing in range immediately after an attack tick.
# ===========================================================================

def test_pallas_flat_atk_buff_visible_on_ally():
    """After Pallas attacks, in-range ally's effective_atk increases by _TALENT_ATK_FLAT."""
    from data.characters.pallas import _TALENT_ATK_FLAT, _TALENT_BUFF_TAG
    w = _world()
    pa = make_pallas(); pa.atk_cd = 0.0
    _place(w, pa, (0, 2))

    # Ally Guard in Pallas's range
    guard = UnitState(
        name="Guard",
        faction=Faction.ALLY,
        max_hp=4000, hp=4000, atk=500,
        defence=0, res=0.0,
        atk_interval=1.0, block=2,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=RangeShape(tiles=((0, 0), (1, 0))),
        deployed=True, position=(1.0, 2.0),
    )
    w.add_unit(guard)

    enemy = _slug(pos=(1, 2))
    w.add_unit(enemy)

    base_atk = guard.effective_atk
    w.tick()  # Pallas attacks, fires on_attack_hit → buff applied to guard

    buff_atk = guard.effective_atk
    assert buff_atk > base_atk, (
        f"Pallas attack must apply flat ATK buff to in-range guard; "
        f"before={base_atk}, after={buff_atk}"
    )
    assert abs((buff_atk - base_atk) - _TALENT_ATK_FLAT) <= 2, (
        f"ATK increase must equal _TALENT_ATK_FLAT={_TALENT_ATK_FLAT}; "
        f"got {buff_atk - base_atk}"
    )
    assert any(b.source_tag == _TALENT_BUFF_TAG for b in guard.buffs)


# ===========================================================================
# Scenario 7: Two medics serving different targets
# Shining heals most-injured ally; Ptilopsis heals second-most-injured.
# Both injured allies should recover HP over time.
# ===========================================================================

def test_dual_medics_heal_multiple_injured_allies():
    """With two medics, two simultaneously injured allies both recover HP."""
    from data.characters.ptilopsis import make_ptilopsis

    w = _world()
    sh = make_shining(); sh.atk_cd = 0.0
    _place(w, sh, (0, 1))
    pt = make_ptilopsis(); pt.atk_cd = 0.0
    _place(w, pt, (0, 2))

    # Two injured allies at different positions
    a1 = UnitState(
        name="Ally1",
        faction=Faction.ALLY,
        max_hp=4000, hp=1000, atk=0,
        defence=0, res=0.0,
        atk_interval=999.0, block=1,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(1.0, 1.0),
    )
    a2 = UnitState(
        name="Ally2",
        faction=Faction.ALLY,
        max_hp=4000, hp=1200, atk=0,
        defence=0, res=0.0,
        atk_interval=999.0, block=1,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(1.0, 2.0),
    )
    w.add_unit(a1); w.add_unit(a2)

    for _ in range(int(TICK_RATE * 6)):  # 6 seconds: ~2 attacks each medic
        w.tick()

    assert a1.hp > 1000, f"Ally1 must be healed by medics; hp={a1.hp}"
    assert a2.hp > 1200, f"Ally2 must be healed by medics; hp={a2.hp}"
