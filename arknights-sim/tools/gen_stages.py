#!/usr/bin/env python3
"""Generate data/stages/*.yaml from ArknightsGameData level JSONs.

Usage:
    python tools/gen_stages.py main_00-04            # single stage
    python tools/gen_stages.py main_00               # all stages in episode 0
    python tools/gen_stages.py main_00 main_01       # two zones
    python tools/gen_stages.py --zone 0 --zone 1     # same, via flag

Output: data/stages/{stageId}.yaml

Enemy IDs in YAML use registry handles — same key derivation as gen_enemies.py.
WAIT_FOR_SECONDS checkpoints are treated as pass-through (path geometry is kept,
timing pause is ignored — acceptable for v1).
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LEVEL_URL = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData"
    "/master/zh_CN/gamedata/levels/{level_id}.json"
)

CACHE_DIR = Path(__file__).parent / ".level_cache"
ENEMY_DB_CACHE = Path(__file__).parent / ".enemy_database_cache.json"
OUT_DIR = Path(__file__).parent.parent / "data" / "stages"


# --------------------------------------------------------------------------
# Enemy key → registry handle  (must match gen_enemies.py dedup logic)
# --------------------------------------------------------------------------

def _ascii_handle(enemy_key: str) -> str:
    parts = enemy_key.rsplit("_", 1)
    return parts[-1] if len(parts) > 1 and parts[-1] else enemy_key


def _build_handle_map(db_path: Path) -> Dict[str, str]:
    """Return {akgd_key: registry_handle} using the same dedup as gen_enemies.py."""
    if not db_path.exists():
        return {}
    db = json.loads(db_path.read_text())
    all_keys = [e["Key"] for e in db.get("enemies", [])]
    seen: Dict[str, str] = {}
    handle_for: Dict[str, str] = {}
    for ek in all_keys:
        h = _ascii_handle(ek)
        if h in seen:
            parts = ek.split("_")
            h = f"{parts[-1]}_{parts[-2]}" if len(parts) >= 3 else ek
        seen[h] = ek
        handle_for[ek] = h
    return handle_for


# --------------------------------------------------------------------------
# Fetch / cache
# --------------------------------------------------------------------------

def _fetch_level(level_id: str) -> Optional[dict]:
    CACHE_DIR.mkdir(exist_ok=True)
    safe = level_id.replace("/", "_")
    cache = CACHE_DIR / f"{safe}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    url = LEVEL_URL.format(level_id=level_id)
    print(f"[fetch] {url} ...", end=" ", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)
        print("ok")
        cache.write_text(json.dumps(data))
        return data
    except Exception as e:
        print(f"FAIL ({e})")
        return None


# --------------------------------------------------------------------------
# Tile parsing
# --------------------------------------------------------------------------

def _tile_type(tile: dict) -> Optional[str]:
    key = tile.get("tileKey", "")
    buildable = tile.get("buildableType", "NONE")
    passable = tile.get("passableMask", "ALL")

    if passable == "NONE" or key in ("tile_forbidden", "tile_wall", "tile_banned"):
        return None
    if key == "tile_end":
        return "goal"
    if key in ("tile_start", "tile_flystart"):
        return "ground"
    if buildable == "MELEE":
        return "deployment_melee"
    if buildable == "RANGED":
        return "deployment_ranged"
    if key in ("tile_road", "tile_corridor", "tile_floor"):
        return "ground"
    if passable in ("ALL", "GROUND_ONLY", "FLY_ONLY"):
        return "ground"
    return None


def _parse_tiles(level: dict) -> Tuple[int, int, List[dict]]:
    md = level.get("mapData") or {}
    raw_map = md.get("map") or []
    tile_defs = md.get("tiles") or []

    height = len(raw_map)
    width = max((len(row) for row in raw_map), default=0)

    tiles = []
    for row_idx, row in enumerate(raw_map):
        # mapData rows count from top; routes use rows from bottom — flip to align
        y = height - 1 - row_idx
        for col_idx, tile_i in enumerate(row):
            if not isinstance(tile_i, int) or tile_i < 0 or tile_i >= len(tile_defs):
                continue
            tt = _tile_type(tile_defs[tile_i])
            if tt is not None:
                tiles.append({"x": col_idx, "y": y, "type": tt})

    return width, height, tiles


# --------------------------------------------------------------------------
# Route / path parsing
# --------------------------------------------------------------------------

def _build_path(route: dict) -> List[Tuple[int, int]]:
    path: List[Tuple[int, int]] = []
    sp = route.get("startPosition") or {}
    if sp.get("col") is not None:
        path.append((int(sp["col"]), int(sp["row"])))

    for cp in route.get("checkpoints") or []:
        if cp.get("type") == "MOVE":
            p = cp.get("position") or {}
            if p.get("col") is not None:
                path.append((int(p["col"]), int(p["row"])))

    ep = route.get("endPosition") or {}
    if ep.get("col") is not None:
        end = (int(ep["col"]), int(ep["row"]))
        if not path or path[-1] != end:
            path.append(end)

    return path


# --------------------------------------------------------------------------
# Wave parsing
# --------------------------------------------------------------------------

def _parse_waves(level: dict, handle_map: Dict[str, str]) -> List[dict]:
    routes = level.get("routes") or []
    spawns = []

    for wave in level.get("waves") or []:
        wd = float(wave.get("preDelay") or 0.0)
        for frag in wave.get("fragments") or []:
            fd = float(frag.get("preDelay") or 0.0)
            for action in frag.get("actions") or []:
                if action.get("actionType") != "SPAWN":
                    continue
                ad = float(action.get("preDelay") or 0.0)
                spawns.append({
                    "first_delay": round(wd + fd + ad, 3),
                    "enemy_key": action.get("key", ""),
                    "count": int(action.get("count") or 1),
                    "interval": float(action.get("interval") or 1.0),
                    "route_idx": int(action.get("routeIndex") or 0),
                })

    spawns.sort(key=lambda s: s["first_delay"])

    result = []
    for sp in spawns:
        ri = sp["route_idx"]
        if ri >= len(routes):
            continue
        route = routes[ri]
        motion = route.get("motionMode", "WALK")
        if motion == "E_NUM":
            continue

        path = _build_path(route)
        if len(path) < 2:
            continue

        ek = sp["enemy_key"]
        handle = handle_map.get(ek) or _ascii_handle(ek)

        result.append({
            "id": handle,
            "count": sp["count"],
            "interval": sp["interval"],
            "first_delay": sp["first_delay"],
            "path": path,
        })

    return result


# --------------------------------------------------------------------------
# YAML emission
# --------------------------------------------------------------------------

def _emit_yaml(
    stage_id: str,
    name: str,
    width: int,
    height: int,
    tiles: List[dict],
    waves: List[dict],
    max_lives: int = 3,
    starting_dp: int = 10,
) -> str:
    lines = [
        f"id: {stage_id}",
        f'name: "{name}"',
        f"starting_dp: {starting_dp}",
        f"max_lives: {max_lives}",
        "map:",
        f"  width: {width}",
        f"  height: {height}",
        "  tiles:",
    ]
    for t in tiles:
        lines.append(f"    - {{x: {t['x']}, y: {t['y']}, type: {t['type']}}}")

    lines.append("enemies:")
    for w in waves:
        lines.append(f"  - id: {w['id']}")
        lines.append(f"    count: {w['count']}")
        lines.append(f"    interval: {w['interval']}")
        lines.append(f"    first_delay: {w['first_delay']}")
        lines.append(f"    path:")
        for x, y in w["path"]:
            lines.append(f"      - [{x}, {y}]")

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------

def generate_stage(stage_id: str, handle_map: Dict[str, str]) -> bool:
    level_id = f"obt/main/level_{stage_id}"
    level = _fetch_level(level_id)
    if level is None:
        return False

    width, height, tiles = _parse_tiles(level)
    waves = _parse_waves(level, handle_map)

    if not waves:
        print(f"[skip] {stage_id} — no SPAWN actions found")
        return False

    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / f"{stage_id}.yaml"
    out_path.write_text(_emit_yaml(stage_id, stage_id, width, height, tiles, waves))
    print(f"[gen]  {out_path}  ({len(waves)} wave entries, {len(tiles)} tiles)")
    return True


def _zone_to_prefix(zone: str) -> str:
    """'0' → 'main_00',  '1' → 'main_01',  'main_00' → 'main_00'."""
    if zone.isdigit():
        return f"main_{int(zone):02d}"
    return zone


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("targets", nargs="*",
                        help="Stage ID (main_00-04) or zone prefix (main_00)")
    parser.add_argument("--zone", action="append", dest="zones", default=[],
                        metavar="N", help="Zone number(s) to generate (0-13)")
    parser.add_argument("--max-stage", type=int, default=20,
                        help="Max stage number per zone when scanning (default 20)")
    args = parser.parse_args(argv)

    handle_map = _build_handle_map(ENEMY_DB_CACHE)
    if not handle_map:
        print("[warn] Enemy database cache not found — run gen_enemies.py first.")
        print("       Enemy IDs will use raw last-chunk handles.")

    targets: List[str] = list(args.targets) + [_zone_to_prefix(z) for z in args.zones]
    if not targets:
        parser.print_help()
        return 1

    # Expand zone prefixes into individual stage IDs
    stage_ids: List[str] = []
    for t in targets:
        if "-" in t.split("_")[-1]:
            stage_ids.append(t)
        else:
            prefix = _zone_to_prefix(t) if not t.startswith("main_") else t
            zone_num = prefix.replace("main_", "")
            for n in range(1, args.max_stage + 1):
                stage_ids.append(f"{prefix}-{n:02d}")

    ok = 0
    for sid in stage_ids:
        if generate_stage(sid, handle_map):
            ok += 1

    print(f"\nGenerated {ok}/{len(stage_ids)} stages → {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
