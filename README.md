# NEON CORE

NEON CORE is a terminal cyber-infiltration game built in Python.
You infiltrate procedural megastructures, manage pressure (HP/EN/HK/AL), survive combat + timed hacks, and complete a clear end-chain:

1. gather cryptodata fragments,
2. neutralize the CORE Sentinel,
3. hack the Central CORE,
4. extract alive.

The game is run-based but persistent: your profile, bank credits, inventory, XP, and evolution attributes carry over. The world is multilingual and delivered through an in-game console packed with logs, mail, missions, and lore.

## Core Features

- Procedural sparse map on a canvas with connected active rooms (`None` void cells outside the layout), perimeter spawn, dynamic enemies/locks/terminals/items.
- Map profile system:
  - Quick run uses a 12x12 canvas with selectable active room count (25/40/60/80).
  - Mission runs derive map size/style from mission mail tone and world modifiers (with difficulty scaling).
- Map generation styles include dense, hybrid, corridor, and branching topologies.
- Pressure systems: HP, Energy (EN), Hack power (HK), Alarm (AL), Credits.
- Timed matrix hacking and reflex combat.
- Mission-driven world modifiers (mail briefings can alter generation rules).
- In-run loot choices and consumable item economy.
- Persistent progression: profile, bank credits/inventory, XP, evolution attributes.
- Pre-run hub loop (shop/evolution/console/mission launch) between runs.
- Leaderboard tracking in `leaderboard.md`.

## Run Loop

Pre-run flow:

- Enter pre-run hub.
- Optionally read mission mail, accept mission modifiers and starter pack.
- Optional pre-run shop and evolution allocation.
- Launch either:
  - `5. Quick run (no mission)`
  - `6. Run Mission Mail` (after mission acceptance)
  - `0. QUIT GAME`

End of run flow:

- Score is saved.
- Leaderboard is displayed.
- Game returns automatically to pre-run hub (no language/player re-selection).

## Progression

- XP is gained each run (including non-win outcomes).
- Evolution system includes attribute points and derived bonuses.
- Core persistent fields include:
  - `bank_credits`
  - `bank_inventory`
  - `xp_total`
  - `level`
  - `attributes`
  - derived stats (`max_hp`, `max_energy`, `base_hack`, etc.)

Notable gameplay detail:

- Standard hack loot option `D` is now cybernetic energy regeneration (`+10 EN`).
- Collecting fragment `3/3` triggers a recomposition notification message.

## In-Game Console and Lore

The in-game console is a major pillar of identity. You can enter it with console commands during a run and navigate a mini-shell style environment. It is not decorative: it hosts mission context, world archives, logs, and personal traces that deepen the fiction.

Supported console language roots:

- console_fr/
- console_en/
- console_es/
- console_it/

Typical folders include logs, mail, missions, lore, archive, notes, and stats. This structure lets narrative depth grow through content files without forcing heavy code changes.

## Main Commands

Movement and exploration:

- n/s/e/w or north/south/east/west
- scan, echo, map

Action layer:

- hack, attack, take, use <item>

Information and systems:

- inventory, status, profile, fragments, shop, leaderboard, help, quit

Console access:

- console
- ssh <player>@console

## Quick Start

Requirements:

- Python 3
- No external dependencies

Run:

```bash
python3 neon.py
```

## Persistence Model

Player data is stored in `saves/<player>.json`.

Persistent data includes:

- run history and core statistics
- bank_credits
- bank_inventory
- xp_total / level / attributes
- latest XP gain and progression state

Rules:

- Victory converts carried run credits into bank credits.
- Defeat or death drops carried run credits.
- Inventory syncs during run updates so state remains coherent.

## Versioning

Below is a practical changelog. The section above explains the game fantasy and player experience; this section tracks concrete updates.

### 2026-03-12

- Console stats routing fixed: `stats` is now resolved as a shared global location from any language console root.
- Removed fallback behavior that could recreate local `console_*/stats` folders when symlink creation failed.
- Root console listing and tree output now expose `stats/` virtually even without a physical local folder.
- Existing duplicated local stats directories were cleaned up and consolidated to the shared `stats/` directory.
- Quest mission text and localization strings were refined for EN/ES/FR/IT mission mails and discovery wording.
- Italian console lore, mail, and mission files were expanded/refined for narrative consistency with other locales.
- Reworked map generation from fixed full-grid layout to sparse connected room topology on a canvas.
- Quick runs now include a room-count selector (25/40/60/80) and style-aware generation.
- Mission runs now use mail-driven map profile metadata (size/style), with difficulty-adjusted room count.
- Mission mails now expose map envelope/style in EN/ES/FR/IT for clearer RP briefing context.

Global behavior changes:

- There is now one canonical stats storage location: `stats/`.
- In-console navigation to stats remains available (`cd stats`, `ls`, `tree`) without requiring per-console physical folders.
- This reduces cross-language desync risk and prevents accidental duplicate stat files.
- Map layout is no longer a fixed full-grid square: active rooms are generated as a connected subset over a canvas, varying by run mode and mission profile.

### 2026-03-11

- Added multilingual JSON-based i18n packs in `lang/`.
- Added pre-run hub with mission flow, shop, evolution, quick run, mission run, and direct quit.
- Added automatic end-of-run return to pre-run hub.
- Added evolution attributes and derived stat bonuses.
- Added mission-mail-driven procedural world modifiers.
- Added/expanded modular architecture:
  - `console.py`
  - `player_manage.py`
  - `shop.py`
  - `hack.py`
  - `fight.py`
  - `quest.py`
  - `world.py`
- Added multilingual console content roots (`console_fr`, `console_en`, `console_es`, `console_it`).
- Updated standard hack loot D to EN regeneration and improved fragment completion feedback.

### Earlier Baseline

- Core terminal gameplay loop established (explore, fight, hack, survive).
- Score and leaderboard persistence in leaderboard.md.
