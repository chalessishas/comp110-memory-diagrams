#!/usr/bin/env python3
"""Generate data/enemies/generated/*.py from ArknightsGameData enemy_database.json.

Usage:
    python tools/gen_enemies.py                              # generate all
    python tools/gen_enemies.py enemy_1007_slime             # single enemy
    python tools/gen_enemies.py --limit 100                  # first N
    python tools/gen_enemies.py --level 2                    # use level 2 stats (elite)

Source: https://github.com/Kengxxiao/ArknightsGameData
Path: zh_CN/gamedata/levels/enemydata/enemy_database.json

Each enemy in the database has 1-3 level variants (level 0/1/2). We default to
level 0 (base). Higher levels typically have bumped HP/ATK for elite or
extreme-mode variants.
"""
from __future__ import annotations
import argparse
import json
import sys
import textwrap
import urllib.request
from pathlib import Path
from typing import Optional

AKGD_URL = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData"
    "/master/zh_CN/gamedata/levels/enemydata/enemy_database.json"
)

CACHE = Path(__file__).parent / ".enemy_database_cache.json"
OUT_DIR = Path(__file__).parent.parent / "data" / "enemies" / "generated"


# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

def fetch_database() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    print(f"[fetch] {AKGD_URL} ...", end=" ", flush=True)
    with urllib.request.urlopen(AKGD_URL, timeout=60) as r:
        data = json.load(r)
    print("ok")
    CACHE.write_text(json.dumps(data))
    return data


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def _unwrap(box: Optional[dict], default=None):
    """akgd attributes are {'m_defined': bool, 'm_value': val}. Unwrap defensively."""
    if not isinstance(box, dict):
        return default
    return box.get("m_value", default)


def extract_enemy(entry: dict, level: int = 0) -> dict:
    """Pull fields for a given level variant. Returns a flat dict."""
    variants = entry["Value"]
    chosen = None
    for v in variants:
        if v.get("level") == level:
            chosen = v
            break
    if chosen is None:
        chosen = variants[0]

    ed = chosen["enemyData"]
    name = _unwrap(ed.get("name"), "Unknown")
    # Sanitize name — akgd sometimes has trailing \n or leading whitespace
    name = (name or "").strip().replace("\n", " ").replace("\r", "") or "Unknown"
    motion = _unwrap(ed.get("motion"), "WALK")
    apply_way = _unwrap(ed.get("applyWay"), "MELEE")
    life_reduce = _unwrap(ed.get("lifePointReduce"), 1) or 1

    attrs = ed.get("attributes", {}) or {}
    max_hp = int(_unwrap(attrs.get("maxHp"), 1) or 1)
    atk = int(_unwrap(attrs.get("atk"), 0) or 0)
    defence = int(_unwrap(attrs.get("def"), 0) or 0)
    magic_res = float(_unwrap(attrs.get("magicResistance"), 0.0) or 0.0)
    move_speed = float(_unwrap(attrs.get("moveSpeed"), 1.0) or 1.0)
    atk_speed = float(_unwrap(attrs.get("attackSpeed"), 100.0) or 100.0)
    base_time = float(_unwrap(attrs.get("baseAttackTime"), 1.0) or 1.0)
    # Avoid divide-by-zero when atk_speed is 0 (e.g. non-attackers)
    atk_interval = round(base_time / (atk_speed / 100.0), 4) if atk_speed > 0 else 99.0

    return {
        "name":          str(name),
        "max_hp":        max_hp,
        "atk":           atk,
        "defence":       defence,
        "res":           magic_res,
        "atk_interval":  atk_interval,
        "move_speed":    move_speed,
        "motion":        str(motion),     # WALK | FLY
        "apply_way":     str(apply_way),  # MELEE | RANGED | ALL | NONE
        "life_reduce":   int(life_reduce),
        "level":         level,
    }


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def _ascii_handle(enemy_key: str) -> str:
    """enemy_1007_slime -> slime (last underscore chunk)."""
    parts = enemy_key.rsplit("_", 1)
    return parts[-1] if len(parts) > 1 and parts[-1] else enemy_key


def render_py(enemy_key: str, handle: str, s: dict) -> str:
    mobility = "Mobility.AIRBORNE" if s["motion"] == "FLY" else "Mobility.GROUND"
    return textwrap.dedent(f"""\
        \"\"\"{s['name']} — generated from ArknightsGameData {enemy_key} level {s['level']}.
        motion={s['motion']}  applyWay={s['apply_way']}  lifeReduce={s['life_reduce']}
        Regenerate: python tools/gen_enemies.py {enemy_key}
        \"\"\"
        from __future__ import annotations
        from typing import List, Tuple
        from core.state.unit_state import UnitState
        from core.types import AttackType, Faction, Mobility


        def make_{handle}(path: List[Tuple[int, int]] | None = None) -> UnitState:
            e = UnitState(
                name={s['name']!r},
                faction=Faction.ENEMY,
                max_hp={s['max_hp']},
                atk={s['atk']},
                defence={s['defence']},
                res={s['res']},
                atk_interval={s['atk_interval']},
                move_speed={s['move_speed']},
                attack_type=AttackType.PHYSICAL,
                mobility={mobility},
                path=list(path) if path else [],
                deployed=True,
            )
            if e.path:
                e.position = (float(e.path[0][0]), float(e.path[0][1]))
            return e
        """)


# --------------------------------------------------------------------------
# Handle uniqueness — two enemies can share last segment; dedupe via full key fallback
# --------------------------------------------------------------------------

def _unique_handles(enemy_keys: list[str]) -> dict[str, str]:
    """Return a mapping enemy_key -> handle where handles are unique."""
    seen: dict[str, str] = {}
    handle_for: dict[str, str] = {}
    for ek in enemy_keys:
        h = _ascii_handle(ek)
        if h in seen:
            # Collision — include the numeric prefix for distinction
            parts = ek.split("_")
            if len(parts) >= 3:
                h = f"{parts[-1]}_{parts[-2]}"
            else:
                h = ek
        seen[h] = ek
        handle_for[ek] = h
    return handle_for


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("keys", nargs="*", help="Specific enemy keys (default: all)")
    parser.add_argument("--level", type=int, default=0,
                        help="Level variant to extract (0/1/2). Default 0.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only generate the first N enemies (useful for smoke testing).")
    args = parser.parse_args(argv)

    db = fetch_database()
    entries_by_key = {e["Key"]: e for e in db["enemies"]}

    if args.keys:
        targets = {k: entries_by_key[k] for k in args.keys if k in entries_by_key}
    else:
        targets = entries_by_key
        if args.limit:
            targets = dict(list(targets.items())[: args.limit])

    handles = _unique_handles(list(targets.keys()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = err = 0
    for key, entry in targets.items():
        try:
            stats = extract_enemy(entry, level=args.level)
        except Exception as e:
            print(f"[err]  {key}: {e}")
            err += 1
            continue
        handle = handles[key]
        (OUT_DIR / f"{handle}.py").write_text(render_py(key, handle, stats))
        ok += 1

    print(f"[done] {ok} generated, {err} errors → {OUT_DIR}")
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
