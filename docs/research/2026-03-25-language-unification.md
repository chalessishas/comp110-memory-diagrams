# Research: Writing Center Language Unification

Date: 2026-03-25
Context: User's original complaint — "中文英文混在一起不可接受." The UI mixes Chinese block names, English descriptions, English category labels, and mixed buttons like "Start with 论点锤炼 →".

## Current Language Mixing (Audit)

| Location | Chinese | English | Mixed |
|----------|---------|---------|-------|
| Block names | `nameZh` used everywhere | `name` exists but unused in UI | — |
| Block descriptions | — | All English | — |
| Category labels | `nameZh` shown | `name` shown right after | "构思Pre-Writing" |
| Block `aiRole` | — | All English | — |
| Preset names | `nameZh` shown | — | — |
| Preset descriptions | — | All English | — |
| Buttons | — | — | "Start with 论点锤炼 →" |
| AutoExecutor checkpoints | Both zh/en supported | Both zh/en supported | Controlled by `language` state |
| WritingCenter toolbar | — | Genre labels in English | — |

**Pattern:** Block/preset names are Chinese, everything else is English. This creates jarring juxtaposition like "Start with 论点锤炼 →" and "构思Pre-Writing".

## Two Approaches

### Approach A: Full i18n with react-i18next

Source: https://react.i18next.com/

- Install `i18next` + `react-i18next` (~15KB gzipped)
- Create `/public/locales/en/writing.json` and `/public/locales/zh/writing.json`
- Replace all hardcoded strings with `t('key')` calls
- Language toggle switches everything at once

**Pros:** Proper, scalable, industry standard
**Cons:** Overkill for one panel in one app. ~200 string replacements across 10 files. Heavy refactor.

### Approach B: Inline language-aware rendering (recommended)

All data already has both `name` and `nameZh`. Just need a `locale` state and conditional rendering.

**Implementation:**
```tsx
// In WritingCenter or a context
const [locale, setLocale] = useState<'en' | 'zh'>('zh'); // Default Chinese for target users

// Helper used everywhere
const t = (en: string, zh: string) => locale === 'zh' ? zh : en;

// In Workbench:
{t(def.name, def.nameZh)}                    // "Thesis" or "论点锤炼"
{t(def.description, def.descriptionZh)}       // Need to add descriptionZh to BlockDef
{t(`Start with ${def.name}`, `开始：${def.nameZh}`)}
```

**What needs `Zh` counterparts added:**
1. `BlockDef.descriptionZh` — 21 blocks × 1 line each
2. `BlockPreset.descriptionZh` — 6 presets × 1 line each
3. `CATEGORY_LABELS` — already has both `name` and `nameZh`
4. UI strings in Workbench/WritingCenter/AutoExecutor — ~30 strings

**Effort:** ~2 hours. No new dependencies. Consistent with existing `nameZh` pattern.

**Pros:** Zero dependencies, uses existing data pattern, small surface area
**Cons:** Not scalable to 10+ languages (but we only need 2)

## Approach B Detailed Plan

### Step 1: Add missing Chinese translations to data

```ts
// blocks.ts — add descriptionZh to BlockDef
{
  type: "brainstorm",
  name: "Brainstorm",
  nameZh: "头脑风暴",
  description: "Explore ideas freely with AI asking probing questions",
  descriptionZh: "AI 提问引导，自由探索写作方向",
  // ...
}

// Block presets
{
  id: "academic",
  name: "Academic Essay",
  nameZh: "学术论文",
  description: "Full process for argumentative essays",
  descriptionZh: "议论文完整写作流程",
  // ...
}
```

### Step 2: Add locale state + helper to WritingCenter

```tsx
const [locale, setLocale] = useState<'en' | 'zh'>('zh');
// Pass locale to all child components as prop or context
```

### Step 3: Replace hardcoded mixed strings

Before: `{def.nameZh}` + `{def.description}`
After: `{locale === 'zh' ? def.nameZh : def.name}` + `{locale === 'zh' ? def.descriptionZh : def.description}`

Or with helper: `{t(def.name, def.nameZh)}` + `{t(def.description, def.descriptionZh)}`

### Step 4: Category labels

Already have both — just use conditional:
```tsx
{locale === 'zh' ? nameZh : name}
// Instead of current: {nameZh}<span>{name}</span>
```

### Step 5: Add language toggle

Small toggle in the top-right of Workbench header: `EN | 中`

## Priority Assessment

This is a **UX fix**, not a feature. The user explicitly called this out as unacceptable. Should be done before any post-MVP feature work (streaming, voice input, etc.).

**Recommended order:**
1. Language unification (this fix) — addresses user's original complaint
2. Merged checkpoints (from input-friction research) — reduces auto-mode friction
3. Cross-language pipeline (from bilingual research) — new capability
4. Streaming for draft block — smoother UX

Sources:
- [react-i18next](https://react.i18next.com/)
- [React i18n Guide 2026](https://www.glorywebs.com/blog/internationalization-in-react)
- [Lightweight i18n Patterns](https://dev.to/myogeshchavan97/how-to-build-multi-language-react-apps-with-internationalization-i18n-1o2d)
