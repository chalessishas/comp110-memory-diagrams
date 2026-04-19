"""P1 acceptance test: Liskarm (DEF=500) tanks 1 Originium Slug to death."""
import pytest
from core.operator import Operator
from core.enemy import Enemy
from core.battle import Battle


def make_liskarm() -> Operator:
    return Operator(
        name="Liskarm",
        max_hp=2000,
        atk=480,
        defence=500,
        res=0,
        atk_interval=1.05,
        block=1,
        attack_type="physical",
    )


def make_originium_slug() -> Enemy:
    # Originium Slug Alpha stats (approximate)
    return Enemy(
        name="Originium Slug",
        max_hp=1300,
        atk=280,
        defence=0,
        res=0,
        atk_interval=1.5,
        attack_type="physical",
    )


def test_liskarm_tanks_slug():
    liskarm = make_liskarm()
    slug = make_originium_slug()
    battle = Battle(operators=[liskarm], enemies=[slug], max_lives=3)
    result = battle.run()

    assert result == "win", f"Expected win, got {result}\n{battle.log.dump()}"
    assert liskarm.alive, "Liskarm should survive"
    assert not slug.alive, "Slug should be defeated"
    assert battle.lives == 3, "No lives should be lost"


def test_damage_floor():
    """Physical DMG = max(ATK*0.05, ATK-DEF). With huge DEF, floor applies."""
    from core.entity import Entity
    # The tank IS the target — attacker ATK=100 vs tank DEF=9999
    tank = Entity(name="Tank", max_hp=1000, atk=0, defence=9999,
                  res=0, atk_interval=1.0)
    dmg = tank.take_physical(raw_atk=100)
    assert dmg == max(1, int(100 * 0.05)), f"Floor damage wrong: {dmg}"


def test_magic_damage():
    from core.entity import Entity
    caster = Entity(name="Caster", max_hp=500, atk=600, defence=0,
                    res=0, atk_interval=1.0)
    target = Entity(name="Target", max_hp=2000, atk=0, defence=0,
                    res=50, atk_interval=1.0)
    dmg = target.take_magic(caster.atk)
    assert dmg == 300, f"Magic damage (50% RES) should be 300, got {dmg}"


def test_heal():
    from core.entity import Entity
    healer_atk = 700
    target = Entity(name="Target", max_hp=2000, atk=0, defence=0,
                    res=0, atk_interval=1.0)
    target.hp = 1000  # damaged
    healed = target.heal(healer_atk)
    assert healed == 700
    assert target.hp == 1700
