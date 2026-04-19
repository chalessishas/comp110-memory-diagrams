"""1v1 combat demo: SilverAsh S3 burst vs Arts Master.

Run from the arknights-sim/ directory:
    python -m examples.silver_ash_burst

Expected narrative:
    t=0-20s: SP ticks up, SilverAsh trades hits with Arts Master
    t~20s:   Truesilver Slash fires (+180% ATK)
    t<30s:   Arts Master falls before the skill window closes
"""
from __future__ import annotations
from core.battle import Battle
from data.enemies import make_arts_master
from data.operators import make_silverash


def main() -> None:
    silverash = make_silverash()
    arts_master = make_arts_master()

    battle = Battle(operators=[silverash], enemies=[arts_master], max_lives=3)
    result = battle.run(max_seconds=60.0)

    print(battle.log.dump())
    print()
    print(f"--- result: {result} ---")
    print(f"SilverAsh: {silverash.hp}/{silverash.max_hp} HP")
    print(f"Arts Master: {arts_master.hp}/{arts_master.max_hp} HP")
    print(f"Lives remaining: {battle.lives}/{battle.max_lives}")
    print(f"Elapsed: {battle.elapsed:.1f}s")


if __name__ == "__main__":
    main()
