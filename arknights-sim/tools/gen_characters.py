#!/usr/bin/env python3
"""Generate data/characters/generated/*.py from ArknightsGameData character_table.json.

Usage:
    python tools/gen_characters.py                         # regenerate curated TARGETS
    python tools/gen_characters.py char_172_svrash         # regenerate single operator
    python tools/gen_characters.py --rarity TIER_6         # all 6-star playable
    python tools/gen_characters.py --rarity TIER_5 TIER_6  # both tiers combined

Source: https://github.com/Kengxxiao/ArknightsGameData (zh_CN/gamedata/excel)
Stats: E2 max-level (phases[2].attributesKeyFrames[-1].data), trust 100 bonus included.
"""
from __future__ import annotations
import argparse
import json
import sys
import textwrap
import unicodedata
import urllib.request
from pathlib import Path
from typing import Iterable

AKGD_BASE = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData"
    "/master/zh_CN/gamedata/excel"
)
CHAR_TABLE_URL = f"{AKGD_BASE}/character_table.json"

# Short handles for curated operators (we hand-maintain skill layers on top of these)
TARGETS: dict[str, str] = {
    "char_172_svrash": "silverash",
    "char_107_liskam": "liskarm",
    "char_103_angel":  "exusiai",
    "char_136_hsguma": "hoshiguma",
    "char_171_bldsk":  "warfarin",
    "char_291_aglina": "angelina",
}

PROFESSION_MAP = {
    "MEDIC":   "Profession.MEDIC",
    "WARRIOR": "Profession.GUARD",
    "SNIPER":  "Profession.SNIPER",
    "TANK":    "Profession.DEFENDER",
    "CASTER":  "Profession.CASTER",
    "SUPPORT": "Profession.SUPPORTER",
    "SPECIAL": "Profession.SPECIALIST",
    "PIONEER": "Profession.VANGUARD",
}

PLAYABLE_PROFESSIONS = set(PROFESSION_MAP.keys())

OUT_DIR = Path(__file__).parent.parent / "data" / "characters" / "generated"


# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

def fetch_char_table(cache_path: Path | None = None) -> dict:
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text())
    print(f"[fetch] {CHAR_TABLE_URL} …", end=" ", flush=True)
    with urllib.request.urlopen(CHAR_TABLE_URL, timeout=60) as r:
        data = json.load(r)
    print("ok")
    if cache_path:
        cache_path.write_text(json.dumps(data))
    return data


# --------------------------------------------------------------------------
# Stat extraction
# --------------------------------------------------------------------------

def extract_stats(entry: dict, *, phase: int = 2, trust100: bool = True) -> dict:
    """Pull E<phase> max-level stats. Includes cost + redeploy time from akgd data."""
    phases = entry.get("phases", [])
    if len(phases) <= phase:
        # Fall back to highest available phase (some low-tier ops only have E0 or E1)
        phase = len(phases) - 1
    if phase < 0:
        raise ValueError("no phases")
    frames = phases[phase].get("attributesKeyFrames", [])
    if not frames:
        raise ValueError("no attribute keyframes")
    data = frames[-1]["data"]   # last keyframe = level max of this phase

    atk_speed = data.get("attackSpeed", 100.0)
    base_time = data.get("baseAttackTime", 1.0)
    atk_interval = round(base_time / (atk_speed / 100.0), 4)

    trust_bonus: dict = {}
    if trust100:
        favor_kfs = entry.get("favorKeyFrames", []) or []
        if favor_kfs:
            trust_bonus = favor_kfs[-1].get("data", {}) or {}

    return {
        "max_hp":       int(data["maxHp"]) + int(trust_bonus.get("maxHp", 0)),
        "atk":          int(data["atk"]) + int(trust_bonus.get("atk", 0)),
        "defence":      int(data["def"]) + int(trust_bonus.get("def", 0)),
        "res":          float(data.get("magicResistance", 0.0)),
        "block":        int(data.get("blockCnt", 1)),
        "atk_interval": atk_interval,
        "move_speed":   float(data.get("moveSpeed", 1.0)),
        "cost":         int(data.get("cost", 0)),
        "redeploy_cd":  float(data.get("respawnTime", 70.0)),
        "ranged":       entry.get("position", "MELEE") == "RANGED",
        "profession":   PROFESSION_MAP.get(entry.get("profession", "WARRIOR"),
                                           "Profession.GUARD"),
        "display_name": entry.get("name", "Unknown"),
        "rarity":       entry.get("rarity", ""),
        "phase_used":   phase,
        "trust100":     trust100,
    }


# --------------------------------------------------------------------------
# Filename sanitization
# --------------------------------------------------------------------------

def _ascii_slug(s: str) -> str:
    """Turn Chinese/special chars into a safe Python module name."""
    # Try NFKD decomposition + ASCII-only
    normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    out = "".join(c.lower() if c.isalnum() else "_" for c in normalized)
    return out.strip("_") or "unknown"


def default_filename(char_id: str, entry: dict) -> str:
    """Derive a module filename from char id. Falls back to ascii slug of char_id."""
    # char_172_svrash -> svrash
    parts = char_id.split("_", 2)
    if len(parts) == 3 and parts[0] == "char":
        return parts[2] or _ascii_slug(char_id)
    return _ascii_slug(char_id)


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def render_py(char_id: str, filename: str, s: dict) -> str:
    ranged_line = "attack_range_melee=False," if s["ranged"] else "attack_range_melee=True,"
    trust_note = "trust 100" if s.get("trust100") else "trust 0"
    phase_note = f"E{s['phase_used']} max-level"
    return textwrap.dedent(f"""\
        \"\"\"{s['display_name']} — generated from ArknightsGameData {char_id}.
        Source: {phase_note}, {trust_note}, no potentials, no module.
        Regenerate: python tools/gen_characters.py {char_id}
        \"\"\"
        from __future__ import annotations
        from core.state.unit_state import UnitState
        from core.types import AttackType, Faction, Profession


        def make_{filename}() -> UnitState:
            return UnitState(
                name={s['display_name']!r},
                faction=Faction.ALLY,
                max_hp={s['max_hp']},
                atk={s['atk']},
                defence={s['defence']},
                res={s['res']},
                atk_interval={s['atk_interval']},
                move_speed={s['move_speed']},
                {ranged_line}
                profession={s['profession']},
                attack_type=AttackType.PHYSICAL,
                block={s['block']},
                cost={s['cost']},
                redeploy_cd={s['redeploy_cd']},
            )
        """)


# --------------------------------------------------------------------------
# Target resolution
# --------------------------------------------------------------------------

def filter_playable(table: dict, rarities: Iterable[str] | None) -> dict[str, str]:
    rarities_set = set(rarities) if rarities else None
    out: dict[str, str] = {}
    for char_id, entry in table.items():
        if entry.get("profession") not in PLAYABLE_PROFESSIONS:
            continue
        if rarities_set and entry.get("rarity") not in rarities_set:
            continue
        if entry.get("isNotObtainable"):
            continue
        out[char_id] = default_filename(char_id, entry)
    return out


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("ids", nargs="*", help="Specific char_ids to regenerate")
    parser.add_argument(
        "--rarity", nargs="+", default=None,
        help="Filter by rarity (e.g. TIER_5 TIER_6). Triggers bulk mode.",
    )
    parser.add_argument(
        "--trust100", action="store_true", default=True,
        help="Apply trust 100%% stat bonus (default on).",
    )
    parser.add_argument(
        "--no-trust", dest="trust100", action="store_false",
        help="Use raw base stats without trust bonus.",
    )
    args = parser.parse_args(argv)

    cache = Path(__file__).parent / ".char_table_cache.json"
    table = fetch_char_table(cache)

    # Pick targets
    if args.rarity:
        targets = filter_playable(table, args.rarity)
        print(f"[filter] rarity={args.rarity}: {len(targets)} matching playable operators")
    elif args.ids:
        targets = {}
        for cid in args.ids:
            if cid not in table:
                print(f"[skip] {cid} not in table")
                continue
            targets[cid] = default_filename(cid, table[cid])
    else:
        targets = TARGETS

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = err = 0
    for char_id, fname in targets.items():
        entry = table.get(char_id)
        if entry is None:
            print(f"[skip] {char_id} not in table")
            err += 1
            continue
        try:
            stats = extract_stats(entry, trust100=args.trust100)
        except (ValueError, KeyError, IndexError) as e:
            print(f"[err]  {char_id} ({entry.get('name')!r}): {e}")
            err += 1
            continue
        (OUT_DIR / f"{fname}.py").write_text(render_py(char_id, fname, stats))
        ok += 1

    print(f"[done] {ok} generated, {err} errors → {OUT_DIR}")
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
