# NEON NODE

A terminal-based cyber infiltration game written in Python.

You infiltrate a 7x7 megastructure, reach the Central Core, survive the Sentinel, hack the Core, and extract alive.

Loots to find and also 10+ ROM histories to discover by retreiving fragments in rooms you'll walk in.

## Quick Start

Requirements:
- Python 3

Run:

```bash
python3 neon.py
```

Don't forget to make neon.py launchable :

```bash
chmod +x neon.py
```

At launch, you choose:
- Language: `fr`, `en`, `it`, `es`
- Player name
- Difficulty (1 to 4)

## Objective

To win, all these conditions must be true in the Core room:
- The room is the Central Core
- The `CORE Sentinel` enemy is neutralized
- The Core terminal has been successfully hacked

Then the run is saved with status `WIN`.

## World and Room Generation

- Grid size: `7 x 7`
- Spawn point: random perimeter tile
- Core: random tile at least Manhattan distance 3 from spawn
- Each room can randomly contain:
  - Enemy (about 30%)
  - Lock (about 25%)
  - Terminal (about 25%)
  - Item (about 20%)
- Core room is special:
  - Enemy forced to `CORE Sentinel` with 75 HP
  - Terminal forced ON
  - Not locked

## Core Stats and Resources

Main player stats:
- HP (health)
- EN (energy)
- HK (hack)
- AL (alarm)
- CR (credits)

Starting values:
- `HP 100`, `EN 100`, `HK 55`, `AL 0`, `CR 0`

Important thresholds:
- Alarm reinforcement pressure starts at `AL >= 4`
- Immediate game over at `AL >= 5`
- Game over if `HP <= 0`

## Commands

### Movement and Exploration
- `north` / `n`
- `south` / `s`
- `east` / `e`
- `west` / `w`
- `map` / `m` : show map
- `scan` / `sc` : consume energy to inspect current room
- `echo` / `ec` : consume energy to reveal tactical markers in adjacent rooms

### Action Commands
- `hack` / `h` : hack terminal or remove lock
- `attack` / `at` : fight enemy in current room
- `take` / `t` : collect visible item and/or ROM fragment
- `use <item>` / `u <item>` : use inventory item

### Information and Meta
- `inventory` / `inv`
- `status` / `stat`
- `fragments` / `fra`
- `shop` / `sh`
- `leaderboard` / `lead`
- `help` / `he`
- `quit` / `q`

## Hacking System

When hacking succeeds or fails, it affects alarm, credits, and progression.

### Intrusion Matrix Rules
The mini-game is 3-step:
1. Step 1: free pick
2. Step 2: must be in the same column as step 1
3. Step 3: must be in the same row as step 2

If wrong code, wrong alignment, or timeout: hack fails.

### Hack Time by Difficulty
- Difficulty 1: 60s
- Difficulty 2: 45s
- Difficulty 3: 30s
- Difficulty 4: 20s

### Matrix Size and Hack Stat
Base matrix size depends on `HK`:
- `HK >= 70` -> 4x4
- `HK > 55` -> 5x5
- `HK == 55` -> 6x6
- `40 <= HK < 55` -> 7x7
- `< 40` -> 8x8

`Enhanced neural interface` reduces size by 1.
Core hacks add +1 size penalty.

### Hack Failure Effects
- Energy is consumed
- Alarm +1
- At alarm level 3, an enemy can be deployed in the room if empty
- Hack stat decreases by 10 (minimum 10)

### Hack Success Effects
- Energy is consumed
- Alarm decreases by 1 (minimum 0)
- Locked room gets unlocked
- Terminal is consumed
- Core terminal success sets `core_hacked = True`

On non-core terminals, you get loot choice:
- `A` credits
- `B` +25 HP
- `C` +5 HK
- `D` +10 HP (cybernetic heal)

Credits from hack are speed-sensitive: faster hacks grant more credits.

## Combat System

If an enemy is present and you do not attack during your turn, the enemy attacks after your command.

During `attack`:
- Enemy stance is random (`aggressive`, `defensive`, `unstable`)
- You choose action `A`, `B`, or `C` within combat timer
- Choice quality changes damage taken
- Sometimes a reflex prompt appears (type a random char quickly)

Combat timers by difficulty:
- Difficulty 1: 10s
- Difficulty 2: 6s
- Difficulty 3: 4s
- Difficulty 4: 3s

Reflex limit by difficulty:
- 6s / 4s / 2s / 3s

Special Core behavior:
- Attacking `CORE Sentinel` damages Sentinel HP
- Sentinel counterattacks while alive
- You must still hack Core terminal after Sentinel dies

## Inventory and Items

Items:
- `medkit`: +25 HP
- `energy_cell`: +25 EN
- `exploit_chip`: +10 HK

Accepted use aliases:
- `use exploit` -> `exploit_chip`
- `use energy` -> `energy_cell`

## ROM Fragments (Narrative System)

Each run selects one story file from the ROM archive.
That story has exactly 3 fragments.

Placement:
- The 3 fragments are placed in random rooms
- Never on spawn or Core room

Collection:
- Use `take` in a room containing a fragment
- Fragment is added to your collection and removed from room

Fragment menu (`fragments` / `fra`):
- Shows collected count and checklist
- At 3/3, unlocks full story log (optional read prompt)

Extra interactions:
- `scan` can detect fragment signature in current room
- `echo` can reveal fragment markers in adjacent unvisited rooms
- Successful terminal hacks can sometimes reveal unknown fragment markers across the map

Scoring bonus:
- Collecting all 3 fragments grants a large ROM bonus (`15000`) in final score.

## Echo and Map Markers

Map legend:
- `P` player
- `C` discovered Core
- `.` visited room
- `#` unknown room
- `E` enemy marker
- `L` loot marker
- `F` fragment marker
- `M` multiple signatures in one room

`echo` marks nearby unvisited rooms only.

## Shop and Upgrades

Use credits to buy permanent run upgrades:

1. Synaptic augment (100): +10s hack time
2. Overload augment (100): improves action `C`
3. Enhanced neural interface (150): matrix size -1
4. Combat chip (150): doubles combat decision timer
5. Strength augment (100): improves action `A`
6. Speed augment (100): improves action `B`
7. Energy dissipator (300): halves energy costs of actions

## Score and Leaderboard

Scores are appended to `leaderboard.md` with timestamp, name, score, rooms, duration, and status.

Status values observed in save flow:
- `WIN` (win)
- `LOOSE` (loss)
- `QUIT` (manual quit)

Final score combines:
- Survival stats (HP, EN, HK)
- Credits
- Rooms visited
- Hack success/failure counts
- Alarm penalty
- ROM full-set bonus
- Global time bonus
- Hack speed bonus
- Difficulty multiplier

## End Conditions

Run ends when one of these happens:
- Win condition in Core room
- `HP <= 0`
- `AL >= 5`
- Player confirms quit

After each run:
- Score is saved
- Leaderboard is displayed
- Replay prompt appears
