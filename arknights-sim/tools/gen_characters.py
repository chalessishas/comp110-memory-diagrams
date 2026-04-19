#!/usr/bin/env python3
"""Generate data/characters/*.py from ArknightsGameData character_table.json.

Usage:
    python tools/gen_characters.py                  # regenerate TARGETS list
    python tools/gen_characters.py char_010_silverash char_204_liskarm

Source: https://github.com/Kengxxiao/ArknightsGameData
Stats: E2 max-level (phases[2].attributesKeyFrames[-1].data), trust 0 (no bonus).
"""
from __future__ import annotations
import json
import sys
import textwrap
import urllib.request
from pathlib import Path

AKGD_BASE = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData"
    "/master/zh_CN/gamedata/excel"
)
CHAR_TABLE_URL = f"{AKGD_BASE}/character_table.json"

# Operators to generate by default — internal ID → output filename
TARGETS: dict[str, str] = {
    "char_172_svrash": "silverash",    # 银灰  SilverAsh  6* Guard
    "char_107_liskam": "liskarm",      # 雷蛇  Liskarm    5* Defender
    "char_103_angel":  "exusiai",      # 能天使 Exusiai    6* Sniper
    "char_136_hsguma": "hoshiguma",    # 星熊  Hoshiguma  6* Defender
    "char_171_bldsk":  "warfarin",     # 华法琳 Warfarin   5* Medic
    "char_291_aglina": "angelina",     # 安洁莉娜 Angelina 6* Supporter
}

PROFESSION_MAP = {
    "MEDIC":       "Profession.MEDIC",
    "WARRIOR":     "Profession.GUARD",
    "SNIPER":      "Profession.SNIPER",
    "TANK":        "Profession.DEFENDER",
    "CASTER":      "Profession.CASTER",
    "SUPPORT":     "Profession.SUPPORTER",
    "SPECIAL":     "Profession.SPECIALIST",
    "PIONEER":     "Profession.VANGUARD",
}

# Generated files go to data/characters/generated/ to avoid clobbering
# manually-curated skill-aware files in data/characters/.
OUT_DIR = Path(__file__).parent.parent / "data" / "characters" / "generated"


def fetch_char_table(cache_path: Path | None = None) -> dict:
    if cache_path and cache_path.exists():
        print(f"[cache] loading {cache_path}")
        return json.loads(cache_path.read_text())
    print(f"[fetch] {CHAR_TABLE_URL} …", end=" ", flush=True)
    with urllib.request.urlopen(CHAR_TABLE_URL, timeout=30) as r:
        data = json.load(r)
    print("ok")
    if cache_path:
        cache_path.write_text(json.dumps(data))
        print(f"[cache] saved → {cache_path}")
    return data


def extract_e2_stats(entry: dict, trust100: bool = True) -> dict:
    """Pull E2 max-level stats from a character_table entry.

    trust100=True applies the full trust (favor) bonus — represents endgame
    operators as players actually use them. Set False for raw base stats.
    """
    phases = entry.get("phases", [])
    if len(phases) < 3:
        raise ValueError(f"No E2 phase for {entry.get('name')}")
    e2_frames = phases[2].get("attributesKeyFrames", [])
    data = e2_frames[-1]["data"]   # last keyframe = max level

    atk_speed = data.get("attackSpeed", 100.0)
    base_time = data.get("baseAttackTime", 1.0)
    atk_interval = round(base_time / (atk_speed / 100.0), 4)

    # Trust (favor) bonus at 100%
    trust_bonus: dict = {}
    if trust100:
        favor_kfs = entry.get("favorKeyFrames", [])
        if favor_kfs:
            trust_bonus = favor_kfs[-1].get("data", {})

    return {
        "max_hp":       int(data["maxHp"]) + int(trust_bonus.get("maxHp", 0)),
        "atk":          int(data["atk"]) + int(trust_bonus.get("atk", 0)),
        "defence":      int(data["def"]) + int(trust_bonus.get("def", 0)),
        "res":          float(data.get("magicResistance", 0.0)),
        "block":        int(data["blockCnt"]),
        "atk_interval": atk_interval,
        "ranged":       entry.get("position", "MELEE") == "RANGED",
        "profession":   PROFESSION_MAP.get(entry.get("profession", "WARRIOR"),
                                           "Profession.GUARD"),
        "cost":         int(entry.get("cost", 0)),
        "redeploy_cd":  float(entry.get("deployTimeInSeconds", 70.0)),
        "display_name": entry.get("name", "Unknown"),
        "trust100":     trust100,
    }


def render_py(char_id: str, filename: str, s: dict) -> str:
    ranged_line = "attack_range_melee=False," if s["ranged"] else "attack_range_melee=True,"
    trust_note = "trust 100" if s.get("trust100") else "trust 0"
    return textwrap.dedent(f"""\
        \"\"\"{s['display_name']} — generated from ArknightsGameData {char_id}.
        Source: E2 max-level, {trust_note}, no potentials, no module.
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
                {ranged_line}
                profession={s['profession']},
                attack_type=AttackType.PHYSICAL,
                block={s['block']},
                cost={s['cost']},
                redeploy_cd={s['redeploy_cd']},
            )
        """)


def main(argv: list[str]) -> None:
    cache = Path(__file__).parent / ".char_table_cache.json"
    table = fetch_char_table(cache)

    targets = {}
    if argv:
        for char_id in argv:
            fname = char_id.split("_", 2)[-1] if char_id.startswith("char_") else char_id
            targets[char_id] = fname
    else:
        targets = TARGETS

    for char_id, fname in targets.items():
        entry = table.get(char_id)
        if entry is None:
            print(f"[skip] {char_id} not found in character_table")
            continue
        try:
            stats = extract_e2_stats(entry)
        except (ValueError, KeyError, IndexError) as e:
            print(f"[err]  {char_id}: {e}")
            continue

        out = OUT_DIR / f"{fname}.py"
        out.write_text(render_py(char_id, fname, stats))
        print(f"[gen]  {out}  ({stats['display_name']}  "
              f"HP={stats['max_hp']} ATK={stats['atk']} DEF={stats['defence']})")


if __name__ == "__main__":
    main(sys.argv[1:])
