#!/usr/bin/env python3
import random
import os
import sys
import time
import string
import json
import re
from datetime import datetime

from fr import TRANSLATIONS_FR
from en import TRANSLATIONS_EN
from it import TRANSLATIONS_IT
from es import TRANSLATIONS_ES

WIDTH = 7
HEIGHT = 7
ALARM_THRESHOLD = 4
SHOW_STATUS_LINE = 1
# Will be set by difficulty selection
HACK_TIME = 30
COMBAT_TIME = 4
REFLEX_TIME = 2
DIFFICULTY_MULTIPLIER = 1
ROM_BONUS_SCORE = 15000
SAVES_DIR = "saves"

INTRO_ASCII_ART = r"""
 _   _ _____ ___  _   _    ____ ___  ____  _____
| \ | | ____/ _ \| \ | |  / ___/ _ \|  _ \| ____|
|  \| |  _|| | | |  \| | | |  | | | | |_) |  _|
| |\  | |__| |_| | |\  | | |__| |_| |  _ <| |___
|_| \_|_____\___/|_| \_|  \____\___/|_| \_\_____|
"""

DEFAULT_LANGUAGE = "fr"
CURRENT_LANGUAGE = DEFAULT_LANGUAGE
SUPPORTED_LANGUAGES = ("fr", "en", "it", "es")
LANGUAGE_LABELS = {
    "fr": "Francais",
    "en": "English",
    "it": "Italiano",
    "es": "Espanol",
}

TRANSLATIONS = {
    "fr": TRANSLATIONS_FR,
    "en": TRANSLATIONS_EN,
    "it": TRANSLATIONS_IT,
    "es": TRANSLATIONS_ES,
}

HEX_VALUES = ['7A', '3F', '9C', 'BD', 'E1', '55', '2D', '8B', '4E', 'AA', '6C', 'F2', '1D', 'C7', 'B4', '0F', 'D9', 'A3', '5E', '91']
player_profile = None
player_profile_path = None

class Room:
    def __init__(self, x, y):
        enemies = tr_value("content.enemies")
        items = tr_value("content.items")
        room_descriptions = tr_value("content.room_descriptions")
        self.x = x
        self.y = y
        self.desc = random.choice(room_descriptions)
        self.enemy = random.choice(enemies) if random.random() < 0.30 else None
        self.locked = random.random() < 0.25
        self.terminal = random.random() < 0.25
        self.item = random.choice(items) if random.random() < 0.20 else None
        self.visited = False
        self.core = False
        self.enemy_hp = 0
        self.rom_fragment = None
        self.echo_marker = None


def perimeter_spawn():
    edge = []
    for x in range(WIDTH):
        edge.append((x, 0))
        edge.append((x, HEIGHT - 1))
    for y in range(1, HEIGHT - 1):
        edge.append((0, y))
        edge.append((WIDTH - 1, y))
    return random.choice(edge)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def tr(key, default=None, **kwargs):
    text = TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(key)
    if text is None:
        text = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)
    if text is None:
        text = default if default is not None else key
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text


def tr_value(key, default=None):
    value = TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(key)
    if value is None:
        value = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)
    if value is None:
        return default
    return value


def get_intro_text():
    return tr_value("intro.full")


def choose_language():
    global CURRENT_LANGUAGE
    print("\n=== LANGUAGE SELECTION ===")
    print("Available codes:")
    for code in SUPPORTED_LANGUAGES:
        print(f"- {code} : {LANGUAGE_LABELS[code]}")

    while True:
        choice = input("Language (fr/en/it/es) > ").strip().lower()
        if choice in SUPPORTED_LANGUAGES:
            CURRENT_LANGUAGE = choice
            print(f"Active language: {choice} ({LANGUAGE_LABELS[choice]})")
            return
        print("Invalid code. Use fr, en, it, es.")


def sanitize_player_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return cleaned or "ANON"


def get_player_profile_path(name):
    safe_name = sanitize_player_name(name)
    return os.path.join(SAVES_DIR, f"{safe_name}.json")


def default_player_profile(name):
    now = datetime.now().isoformat(timespec="seconds")
    return {
        "player_name": name,
        "created_at": now,
        "last_seen": now,
        "total_runs": 0,
        "megastructures_visited": 0,
        "wins": 0,
        "losses": 0,
        "deaths": 0,
        "abandons": 0,
        "total_play_time_seconds": 0,
        "total_hacks_success": 0,
        "total_hacks_failed": 0,
        "total_rooms_visited": 0,
        "total_rom_fragments_collected": 0,
        "last_status": "NONE",
    }


def save_player_profile(profile, path):
    profile["last_seen"] = datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_or_create_player_profile(name):
    os.makedirs(SAVES_DIR, exist_ok=True)
    path = get_player_profile_path(name)
    defaults = default_player_profile(name)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if not isinstance(stored, dict):
                stored = {}
        except (json.JSONDecodeError, OSError):
            stored = {}

        profile = defaults.copy()
        profile.update(stored)
        profile["player_name"] = name
        if "created_at" not in profile or not profile["created_at"]:
            profile["created_at"] = defaults["created_at"]
        save_player_profile(profile, path)
        return profile, path, False

    profile = defaults.copy()
    save_player_profile(profile, path)
    return profile, path, True


def update_profile_after_run(status, duration, end_reason=None):
    global player_profile, player_profile_path
    if not player_profile or not player_profile_path:
        return

    player_profile["total_runs"] = int(player_profile.get("total_runs", 0)) + 1
    player_profile["megastructures_visited"] = int(player_profile.get("megastructures_visited", 0)) + 1
    player_profile["total_play_time_seconds"] = int(player_profile.get("total_play_time_seconds", 0)) + int(duration)
    player_profile["total_hacks_success"] = int(player_profile.get("total_hacks_success", 0)) + int(player.get("hacks_success", 0))
    player_profile["total_hacks_failed"] = int(player_profile.get("total_hacks_failed", 0)) + int(player.get("hacks_failed", 0))
    player_profile["total_rooms_visited"] = int(player_profile.get("total_rooms_visited", 0)) + int(player.get("rooms_visited", 0))
    player_profile["total_rom_fragments_collected"] = int(player_profile.get("total_rom_fragments_collected", 0)) + len(player.get("rom_fragments", []))
    player_profile["last_status"] = status

    if status == "WIN":
        player_profile["wins"] = int(player_profile.get("wins", 0)) + 1
    elif status == "QUIT":
        player_profile["abandons"] = int(player_profile.get("abandons", 0)) + 1
    elif status == "LOOSE":
        player_profile["losses"] = int(player_profile.get("losses", 0)) + 1

    if end_reason == "death":
        player_profile["deaths"] = int(player_profile.get("deaths", 0)) + 1

    save_player_profile(player_profile, player_profile_path)


def round_int(value):
    if value >= 0:
        return int(value + 0.5)
    return int(value - 0.5)


def format_duration_hms(total_seconds):
    total_seconds = max(0, int(total_seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def typewriter_print(text, char_delay=0.003, line_delay=0.04, speed_factor=0.7):
    # speed_factor < 1.0 means slower output
    safe_speed = max(0.01, float(speed_factor))
    effective_char_delay = char_delay / safe_speed
    effective_line_delay = line_delay / safe_speed
    for ch in str(text):
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(effective_char_delay)
    sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(effective_line_delay)


def normalize_credits():
    player['credits'] = round_int(player['credits'])


def normalize_primary_stats():
    player['hp'] = min(100, round_int(player['hp']))
    player['energy'] = max(0, min(100, round_int(player['energy'])))
    player['hack'] = min(100, round_int(player['hack']))


def effective_energy_cost(base_cost):
    if player.get('energy_dissipator_bought'):
        return max(1, base_cost // 2)
    return base_cost


def show_status_line():
    if SHOW_STATUS_LINE:
        normalize_primary_stats()
        normalize_credits()
        print(tr(
            "statusline.compact",
            hp=player['hp'],
            energy=player['energy'],
            hack=player['hack'],
            alarm=player['alarm'],
            credits=player['credits'],
            fragments=len(player['rom_fragments']),
        ))


def show_leaderboard():
    print("\n" + tr("leaderboard.title"))
    try:
        entries = []
        with open("leaderboard.md", "r") as f:
            for l in f:
                parts = [p.strip() for p in l.split("|")]
                sc = 0
                st = ""
                for p in parts:
                    if p.startswith("score:"):
                        try:
                            sc = int(p.split(":")[1])
                        except ValueError:
                            sc = 0
                    if p.startswith("status:"):
                        st = p.split(":")[1]
                entries.append((sc, l.strip(), st))
        entries.sort(key=lambda x: x[0], reverse=True)
        for idx, entry in enumerate(entries, start=1):
            print(tr("leaderboard.entry", idx=idx, line=entry[1]))
    except FileNotFoundError:
        print(tr("leaderboard.none"))


def intro():
    clear()
    show_leaderboard()
    print(get_intro_text())
    input(tr("intro.press_enter"))


def current_room():
    return world[player['y']][player['x']]


def draw_map(show_legend=True):
    print("\n" + tr("map.title"))
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            room = world[y][x]
            if player['x'] == x and player['y'] == y:
                line += "P "
            elif room.core and room.visited:
                line += "C "
            elif room.visited:
                line += ". "
            elif room.echo_marker:
                line += f"{room.echo_marker} "
            else:
                line += "# "
        print(line)
    if show_legend:
        print("\n" + tr("map.legend"))


def get_echo_marker(room):
    signatures = 0
    if room.enemy:
        signatures += 1
    if room.item:
        signatures += 1
    if room.rom_fragment:
        signatures += 1

    if signatures >= 2:
        return 'M'
    if room.enemy:
        return 'E'
    if room.item:
        return 'L'
    if room.rom_fragment:
        return 'F'
    return None


def describe():
    room = current_room()
    if not room.visited:
        print(f"\n{room.desc}")
        room.visited = True
        player['rooms_visited'] += 1
    if room.enemy:
        print(tr("describe.enemy_present", enemy=room.enemy))
        if room.enemy == "CORE Sentinel":
            print(tr("describe.core_hp", hp=room.enemy_hp))
    if room.locked:
        print(tr("describe.locked"))
    if room.terminal:
        print(tr("describe.terminal"))
    if room.item:
        print(tr("describe.item_visible", item=room.item))
    if room.rom_fragment:
        print(tr("describe.fragment_visible", fragment_id=room.rom_fragment['id']))
    if room.core:
        print(tr("describe.core_detected"))


def move(dx, dy):
    room = current_room()
    if room.locked:
        print(tr("move.locked_exit"))
        return
    nx = player['x'] + dx
    ny = player['y'] + dy
    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
        player['x'] = nx
        player['y'] = ny
        enemy_turn()
        describe()
    else:
        print(tr("move.wall"))


def scan():
    room = current_room()
    print(tr("scan.title"))
    scan_cost = effective_energy_cost(random.randint(1, 10))
    player['energy'] = max(0, player['energy'] - scan_cost)
    print(tr("scan.cost", cost=scan_cost))
    found = False
    if random.random() < 0.35 and not room.item:
        hidden = random.choice(tr_value("content.items"))
        room.item = hidden
        print(tr("scan.object_found", item=hidden))
        found = True
    if room.locked:
        print(tr("scan.lock_pulse"))
        found = True
    if room.terminal:
        print(tr("scan.ports_open"))
        found = True
    if room.rom_fragment:
        print(tr("scan.rom_signature"))
        found = True
    if not found:
        print(tr("scan.nothing"))
    enemy_turn()


def echo_scan():
    print(tr("echo.title"))
    echo_cost = effective_energy_cost(random.randint(1, 10))
    player['energy'] = max(0, player['energy'] - echo_cost)
    print(tr("echo.cost", cost=echo_cost))

    detected = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = player['x'] + dx
            ny = player['y'] + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                room = world[ny][nx]
                if room.visited:
                    continue
                marker = get_echo_marker(room)
                if marker:
                    detected += 1
                room.echo_marker = marker

    if detected:
        print(tr("echo.detected", count=detected))
    else:
        print(tr("echo.none"))

    draw_map(show_legend=True)


def reveal_unknown_fragment_markers():
    marked = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            room = world[y][x]
            if room.visited or not room.rom_fragment:
                continue
            if room.rom_fragment['id'] in player['rom_fragments']:
                continue
            marker = get_echo_marker(room)
            if marker:
                room.echo_marker = marker
                marked += 1
    return marked


def show_story_log(story):
    print("\n" + tr("story.title"))
    print(tr("story.id", id=story['id']))
    print(tr("story.name", title=story['title']))
    print(tr("story.hacker", hacker=story['hacker']))
    print(tr("story.context", context=story['bio']))
    print("\n" + tr("story.logs"))
    for line in story['logs']:
        print(line)
    print("\n" + tr("story.epilogue"))
    print(story['epilogue'])


def fragments_menu():
    story = player['active_story']
    total = len(story['fragments'])
    found_count = len(player['rom_fragments'])

    print("\n" + tr("fragments.title"))
    print(tr("fragments.count", found=found_count, total=total))
    for frag in story['fragments']:
        mark = "OK" if frag['id'] in player['rom_fragments'] else "--"
        print(tr("fragments.line", mark=mark, id=frag['id'], label=frag['label']))

    if found_count == total:
        print("\n" + tr("fragments.unlocked"))
        read_story = input(tr("fragments.read_prompt")).strip().lower()
        if read_story == 'y':
            show_story_log(story)
    else:
        print("\n" + tr("fragments.incomplete"))


def hack_grid_size():
    h = player['hack']
    if h >= 70:
        size = 4
    elif h > 55:
        size = 5
    elif h == 55:
        size = 6
    elif 40 <= h < 55:
        size = 7
    else:
        size = 8
    return max(3, size - player['matrix_reduction'])


def mini_hack_success(core_bonus=False):
    size = hack_grid_size() + (1 if core_bonus else 0)
    rows = [chr(ord('A') + i) for i in range(size)]
    cols = [str(i+1) for i in range(size)]
    grid = [[random.choice(HEX_VALUES) for _ in range(size)] for _ in range(size)]
    a = (random.randint(0, size - 1), random.randint(0, size - 1))

    while True:
        b = (random.randint(0, size - 1), a[1])
        if b != a:
            break

    while True:
        c = (b[0], random.randint(0, size - 1))
        if c != b:
            break
    forced = random.sample(HEX_VALUES, 3)
    grid[a[0]][a[1]] = forced[0]
    grid[b[0]][b[1]] = forced[1]
    grid[c[0]][c[1]] = forced[2]
    target = [grid[a[0]][a[1]], grid[b[0]][b[1]], grid[c[0]][c[1]]]

    print("\n" + tr("hack.matrix.title"))
    # use two leading spaces so columns align under row labels (single letter + space)
    header = "  " + " ".join([f"{col:>3}" for col in cols])
    print(header)
    for i in range(size):
        line = f"{rows[i]} " + " ".join([f"{grid[i][j]:>3}" for j in range(size)])
        print(line)

    print("\n" + tr("hack.matrix.sequence", sequence=" -> ".join(target)))
    print(tr("hack.matrix.rules"))

    start = time.time()
    prev_row = None
    prev_col = None

    prev_row = None
    prev_col = None

    for step in range(3):
        choice = input(tr("hack.matrix.step_prompt", step=step + 1)).strip().upper()
        if time.time() - start > HACK_TIME + player['hack_time_bonus']:
            print(tr("hack.matrix.timeout"))
            return False, 0
        if len(choice) < 2:
            return False, 0

        r = choice[0]
        cnum = choice[1:]

        if cnum.isdigit():
            cnum = str(int(cnum))

        if r not in rows or cnum not in cols:
            return False, 0

        rr = rows.index(r)
        cc = cols.index(cnum)

        if grid[rr][cc] != target[step]:
            print(tr("hack.matrix.incorrect"))
            return False, 0

        if step == 1 and cc != prev_col:
            print(tr("hack.matrix.same_column"))
            return False, 0

        if step == 2 and rr != prev_row:
            print(tr("hack.matrix.same_row"))
            return False, 0

        prev_row = rr
        prev_col = cc

    return True, int((time.time() - start) * 1000)


def get_core_hint():
    dx = core_x - player['x']
    dy = core_y - player['y']
    if abs(dx) > abs(dy):
        if dx > 0:
            return tr("core_hint.east")
        else:
            return tr("core_hint.west")
    else:
        if dy > 0:
            return tr("core_hint.south")
        else:
            return tr("core_hint.north")


def hack():
    room = current_room()
    normalize_primary_stats()
    normalize_credits()
    if room.core and room.enemy:
        print(tr("hack.blocked_core"))
        return
    if not (room.locked or room.terminal):
        print(tr("hack.nothing"))
        return
    print("\n" + tr("hack.title"))
    cost = effective_energy_cost(random.randint(1, 5))
    player['energy'] = max(0, player['energy'] - cost)

    result = mini_hack_success(core_bonus=room.core)
    if not result[0]:
        print(tr("hack.cost", cost=cost))
        old_alarm = player['alarm']
        player['alarm'] += 1
        if player['alarm'] > old_alarm:
            print(tr("hack.alarm_triggered", alarm=player['alarm']))
        if player['alarm'] == 3:
            room = current_room()
            if not room.enemy:
                room.enemy = random.choice(tr_value("content.enemies"))
                print(tr("hack.alarm_enemy"))
        player['hack'] = max(10, player['hack'] - 10)
        player['hacks_failed'] += 1
        normalize_primary_stats()
        print(tr("hack.reduced", hack=player['hack']))
        return
    print(tr("hack.cost", cost=cost))
    player['hacks_success'] += 1
    player['total_hack_time'] += result[1]
    is_standard_hack = room.terminal and not room.core
    base_credits = random.randint(50, 100)
    speed_bonus = max(0, 125 - (result[1] / 1000) * 5)
    credit_gain = round_int(base_credits + int(speed_bonus) / DIFFICULTY_MULTIPLIER)

    if is_standard_hack:
        print(tr("hack.standard_success"))
        print(tr("hack.loot.a"))
        print(tr("hack.loot.b"))
        print(tr("hack.loot.c"))
        print(tr("hack.loot.d"))
        loot_choice = input(tr("hack.loot.prompt")).strip().upper()

        if loot_choice == 'B':
            player['hp'] += 25
            print(tr("hack.loot.heal"))
        elif loot_choice == 'C':
            player['hack'] += 5
            print(tr("hack.loot.upgrade"))
        elif loot_choice == 'D':
            player['hp'] += 10
            print(tr("hack.loot.cyber_heal"))
        else:
            player['credits'] += credit_gain
            print(tr("hack.loot.credits", credits=credit_gain))

        if random.random() < 0.25:
            revealed = reveal_unknown_fragment_markers()
            if revealed > 0:
                print(tr("hack.fragment_ping", count=revealed))
                draw_map(show_legend=True)
            else:
                print(tr("hack.fragment_ping_none"))
    else:
        player['credits'] += credit_gain
        print(tr("hack.success.credits", credits=credit_gain))

    player['alarm'] = max(0, player['alarm'] - 1)
    print(tr("hack.alarm_reduced"))
    if room.locked:
        room.locked = False
        print(tr("hack.unlock_room"))
    if room.terminal:
        room.terminal = False
        if room.core:
            player['core_hacked'] = True
            print(tr("hack.core_pirated"))
        else:
            print(get_core_hint())

    normalize_primary_stats()
    normalize_credits()
    print(tr("hack.done_ms", ms=result[1]))


def attack():
    normalize_primary_stats()
    room = current_room()
    if not room.enemy:
        print(tr("attack.no_target"))
        return
    stance = random.choice(['aggressive', 'defensive', 'unstable'])
    if stance == 'aggressive':
        print(tr("attack.stance.aggressive"))
    elif stance == 'defensive':
        print(tr("attack.stance.defensive"))
    else:  # unstable
        print(tr("attack.stance.unstable"))
    effective_time = COMBAT_TIME * player['combat_time_bonus']
    print("\n" + tr("attack.prompt", time=effective_time))
    start = time.time()
    choice = input(tr("attack.choice_prompt")).strip().upper()
    elapsed = time.time() - start
    if elapsed > effective_time:
        print(tr("attack.timeout"))
        choice = random.choice(['A', 'B', 'C'])
    outcome = 'neutral'
    if (choice == 'A' and stance == 'unstable') or (choice == 'B' and stance == 'aggressive') or (choice == 'C' and stance == 'defensive'):
        outcome = 'good'
    elif (choice == 'A' and stance == 'defensive') or (choice == 'B' and stance == 'unstable') or (choice == 'C' and stance == 'aggressive'):
        outcome = 'bad'
    if random.random() < 0.30:
        reflex_char = random.choice(string.ascii_letters + string.digits)
        print(tr("attack.reflex_prompt", char=reflex_char))
        start = time.time()
        reflex = input(tr("ui.reflex_input_prompt")).strip()
        reaction_time = time.time() - start
        reaction_ms = int(reaction_time * 1000)
        if reflex == reflex_char and reaction_time < REFLEX_TIME:
            print(tr("attack.reflex.success", ms=reaction_ms))
            taken = max(0, int(reaction_time * 5))  # faster = less damage, up to 10
        else:
            print(tr("attack.reflex.failure", ms=reaction_ms))
            taken = random.randint(10, 20)
    else:
        if outcome == 'good':
            taken = random.randint(0, 5)
        elif outcome == 'bad':
            taken = random.randint(10, 20)
        else:
            taken = random.randint(5, 10)
    if player['surcharge_bought'] and choice == 'C':
        taken = max(0, taken - 3)
        print(tr("attack.bonus.surcharge"))
    if player['force_bought'] and choice == 'A':
        taken = max(0, taken - 3)
        print(tr("attack.bonus.force"))
    if player['vitesse_bought'] and choice == 'B':
        taken = max(0, taken - 3)
        print(tr("attack.bonus.vitesse"))
    if room.enemy == "CORE Sentinel":
        damage_to_core = random.randint(15, 35)
        room.enemy_hp -= damage_to_core
        print(tr("attack.core.hit", damage=damage_to_core))
        if room.enemy_hp > 0:
            print(tr("attack.core.hp", hp=room.enemy_hp))
            core_damage = random.randint(10, 20)
            player['hp'] -= core_damage
            print(tr("attack.core.counter", damage=core_damage))
        else:
            print(tr("attack.core.neutralized"))
            room.enemy = None
            if not player['core_hacked']:
                print(tr("attack.core.remaining_hack"))
    else:
        print(tr("attack.neutralize", enemy=room.enemy))
        room.enemy = None
        player['hp'] -= taken
        print(tr("attack.taken", damage=taken))
    normalize_primary_stats()


def enemy_attack():
    normalize_primary_stats()
    room = current_room()
    if not room.enemy:
        return
    if room.enemy == "CORE Sentinel":
        damage = random.randint(10, 20)
        player['hp'] -= damage
        print(tr("enemy_attack.core", damage=damage))
    else:
        damage = random.randint(10, 20)
        player['hp'] -= damage
        print(tr("enemy_attack.normal", enemy=room.enemy, damage=damage))
    normalize_primary_stats()


def take():
    room = current_room()
    took_anything = False

    if room.rom_fragment:
        frag = room.rom_fragment
        if frag['id'] not in player['rom_fragments']:
            player['rom_fragments'].append(frag['id'])
            print(tr("take.fragment", fragment_id=frag['id'], count=len(player['rom_fragments'])))
        room.rom_fragment = None
        took_anything = True

    if room.item:
        player['inventory'].append(room.item)
        print(tr("take.item", item=room.item))
        room.item = None
        took_anything = True

    if not took_anything:
        print(tr("take.none"))


def use(item):
    aliases = {
        'exploit': 'exploit_chip',
        'energy': 'energy_cell'
    }
    item = aliases.get(item, item)

    if item not in player['inventory']:
        print(tr("use.absent"))
        return
    if item == 'medkit':
        player['hp'] += 25
    elif item == 'energy_cell':
        player['energy'] += 25
    elif item == 'exploit_chip':
        player['hack'] += 10
    normalize_primary_stats()
    player['inventory'].remove(item)
    print(tr("use.used", item=item))


def inventory():
    print("\n" + tr("inventory.title"))
    if not player['inventory']:
        print(tr("inventory.empty"))
        return
    for obj in player['inventory']:
        if obj == 'medkit':
            print(tr("inventory.medkit"))
        elif obj == 'energy_cell':
            print(tr("inventory.energy_cell"))
        elif obj == 'exploit_chip':
            print(tr("inventory.exploit_chip"))


def status():
    normalize_primary_stats()
    normalize_credits()
    print("\n" + tr("status.title"))
    if player['synaptique_bought']:
        print(tr("status.synaptique"))
    if player['surcharge_bought']:
        print(tr("status.surcharge"))
    if player['interface_bought']:
        print(tr("status.interface"))
    if player['combat_chip_bought']:
        print(tr("status.combat_chip"))
    if player['force_bought']:
        print(tr("status.force"))
    if player['vitesse_bought']:
        print(tr("status.vitesse"))
    if player['energy_dissipator_bought']:
        print(tr("status.dissipateur"))
    if not any([
        player['synaptique_bought'],
        player['surcharge_bought'],
        player['interface_bought'],
        player['combat_chip_bought'],
        player['force_bought'],
        player['vitesse_bought'],
        player['energy_dissipator_bought'],
    ]):
        print(tr("status.none"))
    print("\n" + tr("status.characteristics"))
    print("\n" + tr(
        "status.line",
        hp=player['hp'],
        energy=player['energy'],
        hack=player['hack'],
        alarm=player['alarm'],
        credits=player['credits'],
    ))
    print(tr("status.fragments", count=len(player['rom_fragments'])))


def show_profile_stats(typewriter=False):
    if not player_profile:
        if typewriter:
            typewriter_print(tr("profile.no_data"))
        else:
            print(tr("profile.no_data"))
        return

    lines = [
        "\n" + tr("profile.title"),
        tr("profile.name", value=player_profile.get("player_name", player_name)),
        tr("profile.total_runs", value=player_profile.get("total_runs", 0)),
        tr("profile.megastructures", value=player_profile.get("megastructures_visited", 0)),
        tr("profile.wins", value=player_profile.get("wins", 0)),
        tr("profile.losses", value=player_profile.get("losses", 0)),
        tr("profile.deaths", value=player_profile.get("deaths", 0)),
        tr("profile.abandons", value=player_profile.get("abandons", 0)),
        tr("profile.play_time", value=format_duration_hms(player_profile.get("total_play_time_seconds", 0))),
        tr("profile.hacks_success", value=player_profile.get("total_hacks_success", 0)),
        tr("profile.hacks_failed", value=player_profile.get("total_hacks_failed", 0)),
        tr("profile.rooms_visited", value=player_profile.get("total_rooms_visited", 0)),
        tr("profile.fragments", value=player_profile.get("total_rom_fragments_collected", 0)),
        tr("profile.last_status", value=player_profile.get("last_status", "NONE")),
    ]

    if typewriter:
        for line in lines:
            typewriter_print(line)
    else:
        for line in lines:
            print(line)


def help_cmd():
    print(tr("help.commands"))


def shop():
    normalize_credits()
    print("\n" + tr("shop.title"))
    print(tr("shop.credits", credits=player['credits']))
    print("\n" + tr("shop.items"))
    if not player['synaptique_bought']:
        print(tr("shop.item.1"))
    if not player['surcharge_bought']:
        print(tr("shop.item.2"))
    if not player['interface_bought']:
        print(tr("shop.item.3"))
    if not player['combat_chip_bought']:
        print(tr("shop.item.4"))
    if not player['force_bought']:
        print(tr("shop.item.5"))
    if not player['vitesse_bought']:
        print(tr("shop.item.6"))
    if not player['energy_dissipator_bought']:
        print(tr("shop.item.7"))
    print(tr("shop.item.0"))
    
    choice = input(tr("shop.prompt")).strip()
    if choice == '1' and not player['synaptique_bought'] and player['credits'] >= 100:
        player['credits'] -= 100
        player['synaptique_bought'] = True
        player['hack_time_bonus'] += 10
        print(tr("shop.buy.1"))
    elif choice == '2' and not player['surcharge_bought'] and player['credits'] >= 100:
        player['credits'] -= 100
        player['surcharge_bought'] = True
        print(tr("shop.buy.2"))
    elif choice == '3' and not player['interface_bought'] and player['credits'] >= 150:
        player['credits'] -= 150
        player['interface_bought'] = True
        player['matrix_reduction'] += 1
        print(tr("shop.buy.3"))
    elif choice == '4' and not player['combat_chip_bought'] and player['credits'] >= 150:
        player['credits'] -= 150
        player['combat_chip_bought'] = True
        player['combat_time_bonus'] = 2
        print(tr("shop.buy.4"))
    elif choice == '5' and not player['force_bought'] and player['credits'] >= 100:
        player['credits'] -= 100
        player['force_bought'] = True
        print(tr("shop.buy.5"))
    elif choice == '6' and not player['vitesse_bought'] and player['credits'] >= 100:
        player['credits'] -= 100
        player['vitesse_bought'] = True
        print(tr("shop.buy.6"))
    elif choice == '7' and not player['energy_dissipator_bought'] and player['credits'] >= 300:
        player['credits'] -= 300
        player['energy_dissipator_bought'] = True
        print(tr("shop.buy.7"))
    elif choice == '0':
        return
    else:
        print(tr("shop.invalid"))


def enemy_turn():
    room = current_room()
    if player['alarm'] >= ALARM_THRESHOLD and random.random() < 0.25 and not room.enemy:
        room.enemy = random.choice(tr_value("content.enemies"))
        print(tr("enemy_turn.reinforcement"))


def save_score(status="QUIT", end_reason=None):
    normalize_primary_stats()
    normalize_credits()
    duration = int(time.time() - player['start_time'])
    rom_bonus = ROM_BONUS_SCORE if len(player['rom_fragments']) == 3 else 0
    base_score = (player['hp'] + player['energy']) * 10 + player['hack'] * 20 + player['credits'] * 10 + player['hacks_success'] * 200 - player['hacks_failed'] * 50 + player['rooms_visited'] * 100 - player['alarm'] * 20 + rom_bonus
    time_bonus = max(0, (3600 - duration) // 60)  # 1 point per minute saved (max 60 points for instant finish)
    hack_time_bonus = 0
    if player['hacks_success'] > 0:
        avg_hack_time = player['total_hack_time'] / player['hacks_success']
        hack_time_bonus = max(0, (HACK_TIME - avg_hack_time) * 20)  # bonus for fast hacks
    score = int((base_score + time_bonus + hack_time_bonus) * DIFFICULTY_MULTIPLIER)
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {player_name} | score:{score} | rooms:{player['rooms_visited']} | {duration}s | status:{status}\n"
    with open("leaderboard.md", "a") as f:
        f.write(line)

    # compute ranking
    entries = []
    with open("leaderboard.md", "r") as f:
        for l in f:
            parts = [p.strip() for p in l.split("|")]
            # find score and status
            sc = 0
            st = ""
            for p in parts:
                if p.startswith("score:"):
                    try:
                        sc = int(p.split(":")[1])
                    except ValueError:
                        sc = 0
                if p.startswith("status:"):
                    st = p.split(":")[1]
            entries.append((sc, l.strip(), st))
    # sort descending
    entries.sort(key=lambda x: x[0], reverse=True)
    rank = next((i+1 for i,e in enumerate(entries) if e[1]==line.strip()), None)

    print("\n" + tr("score.title"))
    print(tr("score.base", score=base_score))
    print(tr("score.rom_bonus", bonus=rom_bonus))
    print(tr("score.time_bonus", bonus=time_bonus))
    print(tr("score.hack_bonus", bonus=hack_time_bonus))
    print(line)
    if rank:
        print(tr("score.rank", rank=rank))
    update_profile_after_run(status=status, duration=duration, end_reason=end_reason)



def core_check():
    room = current_room()
    if room.core and not room.enemy and player['core_hacked']:
        print("\n" + tr("core.pirated"))
        save_score(status="WIN", end_reason="win")
        return True
    return False


def main():
    clear()
    print(INTRO_ASCII_ART)
    choose_language()
    print(tr("startup.launching"))
    global world, player, player_name, core_x, core_y, HACK_TIME, COMBAT_TIME, REFLEX_TIME, DIFFICULTY_MULTIPLIER, player_profile, player_profile_path
    player_name = input(tr("startup.player_name_prompt")).strip() or "ANON"
    print(tr("startup.player_name_echo", name=player_name))
    player_profile, player_profile_path, is_new_profile = load_or_create_player_profile(player_name)
    if is_new_profile:
        print(tr("profile.new_hacker"))
    else:
        print(tr("profile.access_granted"))
        show_profile_stats(typewriter=True)
    
    # Difficulty selection
    print("\n" + tr("startup.difficulty_title"))
    print(tr("startup.difficulty_1"))
    print(tr("startup.difficulty_2"))
    print(tr("startup.difficulty_3"))
    print(tr("startup.difficulty_4"))
    
    difficulty = input(tr("startup.difficulty_prompt")).strip()
    if difficulty == '1':
        HACK_TIME = 60
        COMBAT_TIME = 10
        REFLEX_TIME = 6
        DIFFICULTY_MULTIPLIER = 1
    elif difficulty == '2':
        HACK_TIME = 45
        COMBAT_TIME = 6
        REFLEX_TIME = 4
        DIFFICULTY_MULTIPLIER = 2
    elif difficulty == '3':
        HACK_TIME = 30
        COMBAT_TIME = 4
        REFLEX_TIME = 2
        DIFFICULTY_MULTIPLIER = 3
    elif difficulty == '4':
        HACK_TIME = 20
        COMBAT_TIME = 3
        REFLEX_TIME = 3
        DIFFICULTY_MULTIPLIER = 4
    else:
        print(tr("startup.difficulty_invalid"))
        HACK_TIME = 30
        COMBAT_TIME = 4
        REFLEX_TIME = 2
        DIFFICULTY_MULTIPLIER = 3
    
    # Reset world
    world = [[Room(x, y) for x in range(WIDTH)] for y in range(HEIGHT)]
    active_story = random.choice(tr_value("content.rom_story_archive"))
    spawn_x, spawn_y = perimeter_spawn()
    print(tr("main.spawn", x=spawn_x, y=spawn_y))
    
    while True:
        core_x = random.randint(0, WIDTH - 1)
        core_y = random.randint(0, HEIGHT - 1)
        if abs(core_x - spawn_x) + abs(core_y - spawn_y) >= 3 and (core_x, core_y) != (spawn_x, spawn_y):
            break
    print(tr("main.core", x=core_x, y=core_y))
    
    world[core_y][core_x].core = True
    world[core_y][core_x].enemy = "CORE Sentinel"
    world[core_y][core_x].enemy_hp = 75
    world[core_y][core_x].locked = False
    world[core_y][core_x].terminal = True

    # Place 3 ROM fragments from the active story in random rooms (excluding spawn/core).
    candidate_rooms = [
        (x, y) for y in range(HEIGHT) for x in range(WIDTH)
        if (x, y) != (spawn_x, spawn_y) and (x, y) != (core_x, core_y)
    ]
    random.shuffle(candidate_rooms)
    for frag, (fx, fy) in zip(active_story['fragments'], candidate_rooms[:3]):
        world[fy][fx].rom_fragment = frag
    
    global player
    player = {
        "x": spawn_x,
        "y": spawn_y,
        "hp": 100,
        "energy": 100,
        "hack": 55,
        "inventory": [],
        "credits": 0,
        "alarm": 0,
        "hacks_success": 0,
        "hacks_failed": 0,
        "rooms_visited": 0,
        "start_time": time.time(),
        "core_hint_given": False,
        "core_hacked": False,
        "active_story": active_story,
        "rom_fragments": [],
        "synaptique_bought": False,
        "surcharge_bought": False,
        "interface_bought": False,
        "hack_time_bonus": 0,
        "matrix_reduction": 0,
        "combat_chip_bought": False,
        "combat_time_bonus": 1,
        "force_bought": False,
        "vitesse_bought": False,
        "energy_dissipator_bought": False,
        "total_hack_time": 0
    }
    
    intro()
    print("\n" + tr("main.story_channel", story_id=player['active_story']['id']))
    describe()
    while True:
        if player['hp'] <= 0:
            print(tr("main.death"))
            save_score(status="LOOSE", end_reason="death")
            break
        if player['alarm'] >= 5:
            print(tr("main.alarm_game_over"))
            save_score(status="LOOSE", end_reason="alarm")
            break
        if core_check():
            break
        show_status_line()
        player['attacked_this_turn'] = False
        cmd = input(tr("ui.command_prompt")).strip().lower()
        if cmd in ('north', 'n'):
            move(0, -1)
        elif cmd in ('south', 's'):
            move(0, 1)
        elif cmd in ('east', 'e'):
            move(1, 0)
        elif cmd in ('west', 'w'):
            move(-1, 0)
        elif cmd in ('scan', 'sc'):
            scan()
        elif cmd in ('echo', 'ec'):
            echo_scan()
        elif cmd in ('hack', 'h'):
            hack()
        elif cmd in ('attack', 'at'):
            attack()
            player['attacked_this_turn'] = True
        elif cmd in ('take', 't'):
            take()
        elif cmd.startswith('use ') or cmd.startswith('u '):
            use(cmd.split(' ', 1)[1])
        elif cmd in ('inventory', 'inv'):
            inventory()
        elif cmd in ('status', 'stat'):
            status()
        elif cmd in ('profile', 'pro'):
            show_profile_stats()
        elif cmd in ('fragments', 'fra'):
            fragments_menu()
        elif cmd in ('map', 'm'):
            draw_map()
        elif cmd in ('shop', 'sh'):
            shop()
        elif cmd in ('leaderboard', 'lead'):
            show_leaderboard()
        elif cmd in ('help', 'he'):
            help_cmd()
        elif cmd in ('quit', 'q'):
            confirm = input(tr("ui.quit_confirm")).strip().lower()
            if confirm == 'y':
                player['status'] = 'QUIT'
                save_score(status='QUIT', end_reason='quit')
                break
        else:
            print(tr("ui.unknown_command"))
        normalize_primary_stats()
        normalize_credits()
        if not player['attacked_this_turn'] and current_room().enemy:
            enemy_attack()
    show_leaderboard()
    replay = input(tr("ui.replay_prompt")).strip().lower()
    if replay == 'y':
        main()
    else:
        return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(tr("error.unhandled", error=e))
        import traceback
        traceback.print_exc()
