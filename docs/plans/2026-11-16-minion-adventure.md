# Minion Adventure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A funny Twine-style choose-your-own-adventure in one HTML file where the player helps Gru beat Dr. Snoozemonger.

**Architecture:** `index.html` holds styling, a tiny passage engine, and the story as a JS object inside `<script id="story">`. A Node test script extracts that script, evaluates it, and checks story integrity (links resolve, characters present, endings reachable).

**Tech Stack:** Plain HTML/CSS/JS, Node (built-in `node:test`) for checks. No dependencies.

**Spec:** `docs/design.md`

## Global Constraints
- Single file, double-click to play from `file://` — no network, no external assets.
- Must feature: Gru, Lucy, Margo, Edith, Agnes, Kyle, the Minions, the fluffy unicorn, the fart gun.
- Villain: Dr. Snoozemonger, Eternal Nap Ray, stealing every banana on Earth.
- ~25–30 passages, ~4 chapters, 2–3 choices per non-ending passage.
- Stats: `chaos` and `bananas`; final ending chosen by them.
- Original story; no movie-plot recreation.

## Review Focus
- Broken link (choice targets a missing passage) → must never happen; test pins it.
- Dead-end passage with no choices that isn't an ending → test pins it.
- Restart mid-game must reset stats → test pins `resetState()`.
- Orphan passages unreachable from start → test pins reachability.
- Stat display going negative → clamp at 0; test pins it.

---

### Task 1: Engine + story + tests

**Files:**
- Create: `index.html`
- Test: `tests/story.test.mjs`

**Interfaces:**
- `STORY = { start: string, passages: { [id]: { title, text, choices: [{ label, to, effects?: {chaos?, bananas?} }], ending?: true } } }` defined in `<script id="story">`.
- `pickFinale(state) -> passageId` in the story script: picks among final endings by `bananas` and `chaos`.
- `applyEffects(state, effects) -> state` (clamps ≥ 0), `resetState() -> {chaos:0, bananas:0}` in the story script.

- [ ] **Step 1: Write failing tests** in `tests/story.test.mjs`: every `to` exists (or is `"@finale"`); every non-ending passage has ≥2 choices; all passages reachable from `start`; ≥1 ending; passage count 25–35; full story text mentions each of `Gru, Lucy, Margo, Edith, Agnes, Kyle, Minion, unicorn, fart gun, Snoozemonger`; `applyEffects({chaos:0,bananas:0},{bananas:-5}).bananas === 0`; `resetState()` deep-equals `{chaos:0,bananas:0}`; `pickFinale` returns an existing ending id for (0,0) and (99,99).
- [ ] **Step 2: Run** `node --test tests/` — expect FAIL (no index.html).
- [ ] **Step 3: Implement `index.html`**: retro Twine look (dark bg, monospace headings, yellow/blue Minion palette), passage render with fade, stats bar, restart button, keyboard 1–3 for choices, light/dark safe.
- [ ] **Step 4: Run** `node --test tests/` — expect all PASS.
- [ ] **Step 5: Open in browser and play one path to an ending.**
