# NEON CORE

Terminal cyber-infiltration game in Python.

In each run, you infiltrate a 7x7 megastructure, fight through pressure and alarms, neutralize the CORE Sentinel, hack the Central CORE, then extract alive.

## Quick Start

Requirements:
- Python 3 (no external dependencies)

Run:

```bash
python3 neon.py
```

Optional:

```bash
chmod +x neon.py
```

## What Is New

- In-game personal console (`console` or `ssh <player>@console`)
- Localized console files for `fr`, `en`, `es`, `it`
- Persistent meta-progression:
  - Banked credits (CR)
  - Persistent inventory between runs
  - XP accumulation (`10%` of final score, even on death)
- Pre-run shop to buy starting consumables
- Expanded lore, logs, mails, and tutorial-style mission files in all console languages

## Core Gameplay

- Grid: `7x7`
- Core objective:
  - reach CORE room
  - neutralize `CORE Sentinel`
  - hack CORE terminal
- Loss conditions:
  - `HP <= 0`
  - `AL >= 5`

Main resources:
- `HP`, `EN`, `HK`, `AL`, `CR`

## Main Commands

Movement and exploration:
- `n/s/e/w` (or `north/south/east/west`)
- `scan`, `echo`, `map`

Actions:
- `hack`, `attack`, `take`, `use <item>`

Information:
- `inventory`, `status`, `profile`, `fragments`, `shop`, `leaderboard`, `help`, `quit`

Console access:
- `console`
- `ssh <player>@console`

## In-Game Console

The console is a sandboxed mini-shell with real files.

Available commands:
- `ls`, `cd`, `pwd`, `cat`, `tree`, `help`, `exit`
- `status`, `history`, `whoami`, `mail`, `nano <file>`

Language roots:
- `console_fr/`
- `console_en/`
- `console_es/`
- `console_it/`

Each root contains:
- `logs/`, `mail/`, `missions/`, `lore/`, `archive/`, `notes/`, `stats/`

## Persistence Model

Profile save is stored in `saves/<player>.json`.

Persisted elements include:
- run statistics (wins/losses/deaths, hacks, visited rooms, etc.)
- `bank_credits`
- `bank_inventory`
- `xp_total` and last XP gain

Rules:
- On victory: run CR are added to bank CR
- On death/loss: carried run CR are lost
- Inventory is synchronized in save during run updates (`take`/`use`), so interruption keeps state aligned

## Pre-Run Shop

Before difficulty selection, you can spend banked CR.

Current pre-run items:
- `medkit` (`100 CR`)
- `energy_cell` (`100 CR`)

Bought items are available at run start.

## Narrative Layer

- ROM fragments are scattered in rooms
- Completing all 3 fragments in a run unlocks a full story file
- Additional worldbuilding is available through console lore/log/mail files

## Scoring and XP

At end of run, score is computed from survival, hack performance, exploration, credits, alarms, and bonuses.

- Leaderboard is appended to `leaderboard.md`
- XP gained per run: `10%` of final score (minimum `0`)

## Notes

- Project is intentionally lightweight and modular.
- `console.py` contains the console system and is integrated from `neon.py`.
- Content can be extended by editing text files in console language folders without changing game code.
