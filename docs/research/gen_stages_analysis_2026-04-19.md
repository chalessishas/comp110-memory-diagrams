# gen_stages.py — Level Data Analysis & Implementation Plan
*Research Loop @ 2026-04-19 19:03:07*

## Summary

Confirmed: ArknightsGameData has machine-readable level JSON for all main story stages. `gen_stages.py` is implementable with ~200 lines using the same cache-fetch pattern as `gen_enemies.py`.

## Data Source

URL pattern: `https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/levels/obt/main/level_main_{XX}-{NN}.json`

**Critical gotcha**: `stage_table` stores `levelId = "Obt/Main/..."` (uppercase), but the actual GitHub path uses lowercase `obt/main/`. Must `.lower()` the levelId before constructing URLs.

## Level JSON Structure

### Waves → Fragments → Actions

```
wave.preDelay              # seconds before this wave starts
  fragment.preDelay        # added to wave delay  
    action.preDelay        # added to fragment delay → absolute spawn time
    action.key             # enemy ID (e.g. "enemy_1007_slime")
    action.count           # number to spawn
    action.interval        # seconds between individual spawns
    action.routeIndex      # which route they walk
    action.actionType      # "SPAWN" (skip others like "STORY", "TRIGGER")
```

Absolute spawn time = `wave.preDelay + fragment.preDelay + action.preDelay`

### Routes

```
route.motionMode           # "WALK" | "FLY"
route.startPosition        # {row, col}
route.endPosition          # {row, col}
route.checkpoints          # [{type, position, time?}, ...]
  checkpoint.type          # "MOVE" | "WAIT_FOR_SECONDS" | "WAIT_CURRENT" | "DISAPPEAR"
  checkpoint.position      # {row, col}
```

Path extraction: start → MOVE checkpoints only → end. Skip WAIT_FOR_SECONDS (just delays on the tile, not a new waypoint). Our YAML path = `[[col, row], ...]`.

### Map Tiles

```
mapData.map                # 2D array [row][col] → index into mapData.tiles
mapData.tiles[i].tileKey   # e.g. "tile_road", "tile_start", "tile_end", "tile_wall"
mapData.tiles[i].heightType # "HIGHLAND" | "LOWLAND"
mapData.tiles[i].buildableType # "MELEE" | "RANGED" | "NONE"
```

Tile type mapping to our YAML:
| akgd tileKey | buildableType | heightType | our type |
|---|---|---|---|
| tile_road | NONE | LOWLAND | ground |
| tile_start | NONE | * | ground (spawn) |
| tile_end | NONE | * | goal |
| tile_flystart | NONE | * | ground (fly spawn) |
| any | MELEE | LOWLAND | deployment_melee |
| any | RANGED | HIGHLAND | deployment_ranged |
| tile_forbidden / tile_wall | * | * | (skip — no entry needed) |

## Implementation Plan for gen_stages.py

```python
# Key steps:
# 1. Load stage_table cache → find all MAIN stages for target zone (e.g. "main_0")
# 2. For each stage: levelId.lower() → fetch level JSON (cache by levelId)
# 3. Parse mapData → emit map: {width, height, tiles:[...]} block
# 4. Parse waves → flatten to list of (abs_time, key, count, interval, route_idx)
# 5. For each unique (key, route_idx): build enemy entry with path from routes
# 6. Group entries by route to deduplicate paths
# 7. Emit YAML

# Deduplication note: many spawn groups share the same route (same path).
# Merge same-route spawns into single YAML enemy entries where possible.
# But if different enemies share a route, they still need separate entries.
```

## Complexity Assessment

- **Easy**: wave flattening, route path extraction (MOVE checkpoints only)
- **Medium**: tile type mapping, handling multi-wave timing correctly
- **Hard**: WAIT_FOR_SECONDS checkpoints (enemy pauses mid-path — our path system doesn't support this yet)
- **Out of scope for v1**: `branches` field (conditional spawns), `randomSpawnGroupKey` (random waves)

## Recommended Scope for gen_stages.py v1

1. Generate YAML for all `stageType=MAIN` stages in a given zone
2. Skip stages with `branches` or randomSpawnGroup (mark as TODO)
3. Treat WAIT checkpoints as pass-through (enemy moves through without pausing)
4. Include map tile extraction for melee/ranged deployment zones
5. Cache individual level JSONs in `tools/.level_cache/`

## Current State

- 100 tests passing (0.21s)
- 417 operators, 1860 enemies in generated data
- 3 handcrafted stages (main_0-1, main_0-2, main_0-3)
- Next priority: gen_stages.py to unlock batch stage testing

## Other Potential Improvements

1. **Arts 致死 0-HP edge case** (noted in sonnet-0419AV): enemy survives at 1 HP when Arts damage reduced to 0 by 100% RES. Low priority but clean.
2. **Curated characters**: Only 7 curated operators (angelina, exusiai, hoshiguma, liskarm, silverash, warfarin, headb2). No S1 implementations for any operator.
3. **DP cost mechanic**: Operators in generated data don't have DP costs yet — not needed until we add an economy system.
