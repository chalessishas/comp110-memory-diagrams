"""Arknights combat simulator CLI.

Usage (from arknights-sim/ directory):
    python cli.py data/stages/main_0-1.yaml
    python cli.py data/stages/main_0-1.yaml --log json
    python cli.py data/stages/main_0-1.yaml --ops liskarm,hoshiguma

Exit code: 0 = win, 1 = loss or timeout.
"""
from __future__ import annotations
import argparse
import json
import sys
from stages.loader import load_stage, stage_to_battle

_OP_REGISTRY: dict = {}

try:
    from data.operators import make_liskarm, make_hoshiguma, make_exusiai, make_silverash
    _OP_REGISTRY = {
        "liskarm": make_liskarm,
        "hoshiguma": make_hoshiguma,
        "exusiai": make_exusiai,
        "silverash": make_silverash,
    }
except ImportError:
    pass

_DEFAULT_OPS = ["liskarm", "hoshiguma"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arknights-sim",
        description="Run an Arknights stage simulation.",
    )
    parser.add_argument("stage", help="Path to stage YAML file")
    parser.add_argument(
        "--log", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--ops", default=",".join(_DEFAULT_OPS),
        help=f"Comma-separated operator names (default: {','.join(_DEFAULT_OPS)}). "
             f"Available: {', '.join(_OP_REGISTRY)}",
    )
    args = parser.parse_args(argv)

    # Build operator list
    op_names = [name.strip().lower() for name in args.ops.split(",")]
    operators = []
    for name in op_names:
        factory = _OP_REGISTRY.get(name)
        if factory is None:
            print(f"Unknown operator: {name!r}. Available: {list(_OP_REGISTRY)}", file=sys.stderr)
            return 2
        operators.append(factory())

    stage = load_stage(args.stage)
    battle = stage_to_battle(stage, operators=operators)
    result = battle.run()

    if args.log == "json":
        output = {
            "stage": stage.id,
            "result": result,
            "lives": battle.lives,
            "max_lives": battle.max_lives,
            "elapsed_s": round(battle.elapsed, 2),
            "operators": [
                {"name": op.name, "hp": op.hp, "max_hp": op.max_hp, "alive": op.alive}
                for op in battle.operators
            ],
            "log": battle.log.entries,
        }
        print(json.dumps(output, indent=2))
    else:
        if battle.log.entries:
            print(battle.log.dump())
        print(f"\n--- {result.upper()} ---")
        print(f"Stage : {stage.id} — {stage.name}")
        print(f"Lives : {battle.lives}/{battle.max_lives}")
        print(f"Time  : {battle.elapsed:.1f}s")
        for op in battle.operators:
            status = "alive" if op.alive else "DEAD"
            print(f"  {op.name}: {op.hp}/{op.max_hp} HP [{status}]")

    return 0 if result == "win" else 1


if __name__ == "__main__":
    sys.exit(main())
