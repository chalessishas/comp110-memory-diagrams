"""arknights-sim v2 CLI — load a stage YAML and run it.

Usage (from arknights-sim/):
    python cli.py data/stages/main_0-1.yaml
    python cli.py data/stages/main_0-1.yaml --ops silverash,liskarm
    python cli.py data/stages/main_0-1.yaml --log json
    python cli.py data/stages/main_0-1.yaml --at 2,2 silverash --at 4,2 liskarm

Exit code: 0 = win, 1 = loss/timeout, 2 = bad args.
"""
from __future__ import annotations
import argparse
import json
import sys
from typing import Callable, Dict, List, Tuple

from core.state.unit_state import UnitState
from data.characters.registry import get_operator, has_operator, list_operators, operator_count
from stages.loader import load_and_build


_DEFAULT_OPS = ["silverash", "liskarm"]
_DEFAULT_POSITIONS = [(2, 2), (4, 2)]


def _parse_deploy_spec(spec: str) -> Tuple[int, int, str]:
    """Parse 'x,y=name' into (x, y, name). Used by --at flag."""
    try:
        pos, name = spec.split("=")
        x, y = pos.split(",")
        return int(x), int(y), name.strip().lower()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--at expects 'x,y=name' (got {spec!r})"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arknights-sim",
        description="Run an Arknights stage simulation (v2 ECS).",
    )
    parser.add_argument("stage", help="Path to stage YAML")
    parser.add_argument(
        "--log", choices=["text", "json"], default="text",
        help="Output format",
    )
    parser.add_argument(
        "--ops", default=",".join(_DEFAULT_OPS),
        help=f"Comma-separated operator handles "
             f"(default: {','.join(_DEFAULT_OPS)}). "
             f"Registry has {operator_count()} operators — use --list to browse.",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all available operator handles and exit.",
    )
    parser.add_argument(
        "--at", action="append", default=[], type=_parse_deploy_spec,
        help="Explicit deploy position: --at 2,2=silverash (repeatable)",
    )
    parser.add_argument(
        "--max-seconds", type=float, default=300.0,
        help="Max simulated time before timeout",
    )
    args = parser.parse_args(argv)

    if args.list:
        handles = list_operators()
        print(f"# {len(handles)} operators available:")
        for h in handles:
            try:
                op = get_operator(h)
                print(f"  {h:15s} {op.name:<12s}  HP={op.max_hp:5d} ATK={op.atk:4d}")
            except Exception as e:
                print(f"  {h:15s} <error: {e}>")
        return 0

    # Resolve operator + position pairs
    pairs: List[Tuple[int, int, str]] = list(args.at)
    if not pairs:
        op_names = [n.strip().lower() for n in args.ops.split(",")]
        for name, pos in zip(op_names, _DEFAULT_POSITIONS):
            pairs.append((pos[0], pos[1], name))

    # Validate + build operators
    operators: List[Tuple[Tuple[int, int], UnitState]] = []
    for x, y, name in pairs:
        if not has_operator(name):
            print(f"Unknown operator: {name!r}. Use --list to browse {operator_count()} options.",
                  file=sys.stderr)
            return 2
        operators.append(((x, y), get_operator(name)))

    # Build world from stage + deploy operators pre-battle
    stage, world = load_and_build(args.stage)
    for (x, y), op in operators:
        op.deployed = True
        op.position = (float(x), float(y))
        world.add_unit(op)

    result = world.run(max_seconds=args.max_seconds)

    if args.log == "json":
        out = {
            "stage": stage.id,
            "stage_name": stage.name,
            "result": result,
            "lives": world.global_state.lives,
            "max_lives": world.global_state.max_lives,
            "elapsed_s": round(world.global_state.elapsed, 2),
            "dp_final": world.global_state.dp,
            "damage_dealt": world.global_state.total_damage_dealt,
            "enemies_defeated": world.global_state.enemies_defeated,
            "operators": [
                {
                    "name": op.name, "hp": op.hp, "max_hp": op.max_hp,
                    "alive": op.alive, "position": op.position,
                }
                for _, op in operators
            ],
            "log": world.log_entries,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for line in world.log_entries:
            print(line)
        banner = "=" * 50
        print(f"\n{banner}")
        print(f"  {result.upper()}  —  {stage.id} ({stage.name})")
        print(f"  Lives:    {world.global_state.lives}/{world.global_state.max_lives}")
        print(f"  Time:     {world.global_state.elapsed:.1f}s")
        print(f"  Damage:   {world.global_state.total_damage_dealt}")
        print(f"  Defeated: {world.global_state.enemies_defeated}")
        print(banner)
        for _, op in operators:
            status = "alive" if op.alive else "DEAD"
            print(f"  {op.name:<12} {op.hp}/{op.max_hp} HP [{status}]")

    return 0 if result == "win" else 1


if __name__ == "__main__":
    sys.exit(main())
