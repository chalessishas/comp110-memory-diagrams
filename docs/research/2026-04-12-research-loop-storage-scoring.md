# Research Loop — 2026-04-12
**Topics:** localStorage versioning · React context performance · TOEFL e-rater weights
**App context:** React 19 + Vite + localStorage only (no backend)

---

## Topic 1: localStorage Versioning & Migration

### Finding
The simplest battle-tested pattern is a **single migration manifest key** (`toefl-schema-version`) that stores the current version integer, combined with a sequential migration runner that executes transforms in order on startup. Key-suffixing (e.g., `toefl-score-history-v2`) is an alternative but forces all read/write paths to know the current suffix, creating coupling. A wrapper-with-version-field (storing `{ v: 2, data: [...] }`) is the most self-contained approach: each key carries its own version, so migrations are independent per key and require no global manifest.

The `migrate-local-storage` npm library demonstrates the migration-runner pattern cleanly: each migration is a numbered function, the runner reads the current version, applies only pending migrations in sequence, then writes the new version. Redux Persist uses the same idea (`stateReconciler` + `version` field).

For this app — 8 unversioned keys with no existing version numbers — the **wrapper-with-version-field** approach is the lowest-risk retrofit: wrap each `JSON.parse` call to detect `{ v, data }` vs a raw value, defaulting missing version to `v:0`. No key renames needed, no migrations for existing data that is still valid.

### Source
- https://github.com/CatChen/versioned-storage (versioned-storage npm)
- https://www.freecodecamp.org/news/how-to-use-redux-persist-when-migrating-your-states-a5dee16b5ead/ (Redux Persist migration pattern)
- https://www.linkedin.com/pulse/versioned-migration-local-data-react-native-amal-jose- (React Native AsyncStorage versioned migration walkthrough)

### Applicability
Wrap the 8 existing localStorage helpers to write `{ v: 1, data: payload }` going forward. On read, detect raw (legacy) vs wrapped, run per-key migration if needed. Zero backend needed, zero key renames, no breakage for existing users.

---

## Topic 2: React Context Performance — ThemeContext with 15+ Consumers

### Finding
Every consumer of a React context re-renders whenever the context *value reference* changes, regardless of whether the specific piece they use changed. For a ThemeContext where the value is `{ theme, setTheme }`, every toggle creates a new object reference, re-rendering all 15+ consumers.

Three solutions ranked by simplicity:

1. **Wrap value in `useMemo`** — `useMemo(() => ({ theme, setTheme }), [theme])`. This avoids the re-render caused by a new object reference on parent re-renders unrelated to theme. It does NOT help when `theme` itself changes — all consumers still re-render. Verdict: cheap win, but partial.

2. **Split state and dispatch** (Kent C. Dodds pattern) — Two separate contexts: `ThemeStateContext` (just the `theme` string) and `ThemeDispatchContext` (just `setTheme`). Components that only call `setTheme` (e.g., a toggle button) consume only the dispatch context and never re-render on theme changes. For a ThemeContext this is ideal since most consumers read `theme` but only one component writes it.

3. **Selector pattern / `use` hook** — Extract a selector hook and wrap consumers in `React.memo`. The upcoming `use(Context)` + context selectors RFC would allow subscribing to a subset of context, but is not stable in React 19 as of early 2026.

**Recommended for this app:** Split into `ThemeValueContext` + `ThemeDispatchContext`. The toggle button (1 component) uses dispatch only. All 15+ display components use value context. Combined with `React.memo` on leaf components, this eliminates cascading re-renders from the toggle.

### Source
- https://kentcdodds.com/blog/how-to-optimize-your-context-value
- https://www.developerway.com/posts/how-to-write-performant-react-apps-with-context
- https://interbolt.org/blog/react-use-selector-optimization/ (future `React.use` selector pattern)

### Applicability
ThemeContext split is a 30-minute refactor: add `ThemeDispatchContext`, update the provider, update the single toggle component. No change needed to the 15+ read-only consumers since they already call `useTheme()` — just update that hook to read from `ThemeValueContext`.

---

## Topic 3: TOEFL Writing Score Calibration — e-rater Dimension Weights

### Finding
The most concrete publicly available breakdown (via TOEFL Resources, citing historical ETS data) gives **8 macrofeatures** with these approximate weights:

| Dimension | Published Weight |
|-----------|-----------------|
| Organization | **32%** |
| Development | **29%** |
| Mechanics | 10% |
| Usage (collocations/idioms) | 8% |
| Grammar | 7% |
| Lexical Complexity — word length | 7% |
| Lexical Complexity — rare words | 7% |
| Style | 3% (not 7%) |

The app's current weights (Organization 32%, Development 30%, Vocabulary 14%, Mechanics 10%, Grammar 7%, Style 7%) are broadly aligned with ETS data for the two dominant dimensions (Org + Dev ≈ 61–62%). The divergence is:
- **Vocabulary is split in ETS into Usage (8%) + two Lexical Complexity features (7% + 7%) = 22%**, but the app collapses this to a single 14% "Vocabulary". Undercounting.
- **Style is 3% in ETS data, not 7%** as currently weighted. Overcounting by ~2x.
- ETS adds **Usage** (collocations/idioms) as a distinct dimension that the app does not model separately.

For TOEFL Essentials tasks (Write Email, Academic Discussion), ETS official rubrics add a **Task Completion / Communicative Goals** dimension that e-rater cannot score at all — this is the dominant human-score differentiator and currently absent from the app's automated scorer.

### Source
- https://www.toeflresources.com/how-does-the-toefl-e-rater-work/ (8-dimension breakdown with % weights)
- https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12061 (Attali 2015 — Automated Trait Scores for TOEFL Writing Tasks, ETS RR-15-14)
- https://www.ets.org/erater/how.html (ETS official e-rater feature list)

### Applicability
Two concrete fixes: (1) drop Style weight from 7% → 3%, redistribute ~4% to Vocabulary to reach ~18% total lexical weight. (2) Consider splitting Vocabulary into word-rarity (already implemented) and collocation/idiom detection (harder; could use phrase-level checks). The bigger opportunity is adding a simple Task Completion heuristic — checking that email subject/greeting/closing are present, or that the discussion response references the prompt — which would mirror the dominant ETS human-score dimension currently unscored.

---

*Research timestamp: 2026-04-12 12:57:25*
