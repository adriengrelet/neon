#!/usr/bin/env python3
import random
import os
import sys
import time
from datetime import datetime

from fr import TRANSLATIONS_FR
from en import TRANSLATIONS_EN
from it import TRANSLATIONS_IT
from es import TRANSLATIONS_ES
from console import launch_console
from player_manage import (
    load_or_create_player_profile as pm_load_or_create_player_profile,
    update_profile_after_run as pm_update_profile_after_run,
    save_player_profile as pm_save_player_profile,
    format_inventory_counts,
    get_bank_inventory_for_run as pm_get_bank_inventory_for_run,
    sync_profile_inventory_from_player as pm_sync_profile_inventory_from_player,
    build_profile_lines,
)
from shop import run_pre_run_shop, run_in_game_shop, apply_upgrade_ids_to_player
from hack import run_hack
from fight import run_attack, run_enemy_attack, run_enemy_turn
from quest import (
    BASE_WORLD_RULES,
    load_megastructures,
    choose_structure_for_run,
    build_briefing_mail,
    copy_mail_to_console,
    build_world_rules,
    apply_starter_pack_to_profile,
    unlock_next_structure,
    copy_discovery_to_console,
)

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
WORLD_RULES = dict(BASE_WORLD_RULES)
ALARM_MAX = BASE_WORLD_RULES['alarm_max']
MEGASTRUCTURES = []

class Room:
    def __init__(self, x, y):
        enemies = tr_value("content.enemies")
        items = tr_value("content.items")
        room_descriptions = tr_value("content.room_descriptions")
        self.x = x
        self.y = y
        self.desc = random.choice(room_descriptions)
        self.enemy = random.choice(enemies) if random.random() < WORLD_RULES['enemy_chance'] else None
        self.locked = random.random() < WORLD_RULES['locked_chance']
        self.terminal = random.random() < WORLD_RULES['terminal_chance']
        self.item = random.choice(items) if random.random() < WORLD_RULES['item_chance'] else None
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


def load_or_create_player_profile(name):
    return pm_load_or_create_player_profile(name, SAVES_DIR)


def update_profile_after_run(status, duration, end_reason=None, score=0):
    global player_profile, player_profile_path
    player_profile = pm_update_profile_after_run(
        player_profile,
        player_profile_path,
        player,
        status,
        duration,
        end_reason=end_reason,
        score=score,
    )


def pre_run_shop():
    global player_profile, player_profile_path
    return run_pre_run_shop(
        player_profile,
        player_profile_path,
        tr,
        pm_save_player_profile,
        format_inventory_counts,
    )


def get_bank_inventory_for_run():
    return pm_get_bank_inventory_for_run(player_profile)


def sync_profile_inventory_from_player():
    global player_profile, player_profile_path
    player_profile = pm_sync_profile_inventory_from_player(player_profile, player_profile_path, player)


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
    scaled_cost = max(1, round_int(base_cost * WORLD_RULES.get('energy_cost_scale', 1.0)))
    if player.get('energy_dissipator_bought'):
        return max(1, scaled_cost // 2)
    return scaled_cost


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
    if random.random() < WORLD_RULES.get('scan_item_discovery_chance', 0.35) and not room.item:
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
    global player_profile, player_profile_path
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
        if not player.get('next_structure_unlocked'):
            next_structure = unlock_next_structure(
                player_profile,
                player_profile_path,
                pm_save_player_profile,
                MEGASTRUCTURES,
                story.get('id'),
            )
            if next_structure:
                note_path = copy_discovery_to_console(CURRENT_LANGUAGE, story, next_structure, tr)
                print("\n" + tr("quest.discovery.header"))
                print(tr("quest.discovery.target", structure_id=next_structure.get('id'), title=next_structure.get('title')))
                print(tr("quest.discovery.note", path=note_path))
            player['next_structure_unlocked'] = True
        read_story = input(tr("fragments.read_prompt")).strip().lower()
        if read_story == 'y':
            show_story_log(story)
    else:
        print("\n" + tr("fragments.incomplete"))


def hack():
    run_hack(
        player=player,
        world=world,
        width=WIDTH,
        height=HEIGHT,
        core_x=core_x,
        core_y=core_y,
        hex_values=HEX_VALUES,
        hack_time=HACK_TIME,
        difficulty_multiplier=DIFFICULTY_MULTIPLIER,
        tr=tr,
        tr_value=tr_value,
        get_current_room=current_room,
        get_echo_marker=get_echo_marker,
        draw_map=draw_map,
        effective_energy_cost=effective_energy_cost,
        normalize_primary_stats=normalize_primary_stats,
        normalize_credits=normalize_credits,
        round_int=round_int,
    )


def attack():
    run_attack(
        player=player,
        combat_time=COMBAT_TIME,
        reflex_time=REFLEX_TIME,
        tr=tr,
        get_current_room=current_room,
        normalize_primary_stats=normalize_primary_stats,
    )


def enemy_attack():
    run_enemy_attack(
        player=player,
        tr=tr,
        get_current_room=current_room,
        normalize_primary_stats=normalize_primary_stats,
    )


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

    if took_anything:
        sync_profile_inventory_from_player()

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
    sync_profile_inventory_from_player()
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

    lines = build_profile_lines(player_profile, player_name, tr, format_duration_hms)

    if typewriter:
        for line in lines:
            typewriter_print(line)
    else:
        for line in lines:
            print(line)


def help_cmd():
    print(tr("help.commands"))


def should_open_ssh_console(cmd):
    if not cmd.startswith("ssh "):
        return False
    parts = cmd.split(maxsplit=1)
    if len(parts) != 2:
        return False
    target = parts[1].strip().lower()
    return target.endswith("@console")


def open_personal_console():
    launch_console(
        player_name=player_name,
        language=CURRENT_LANGUAGE,
        status_callback=status,
    )


def shop():
    run_in_game_shop(
        player,
        tr,
        normalize_credits,
        sync_profile_inventory_from_player,
        profile=player_profile,
        profile_path=player_profile_path,
        save_profile=pm_save_player_profile,
    )


def enemy_turn():
    run_enemy_turn(
        player=player,
        alarm_threshold=ALARM_THRESHOLD,
        reinforcement_chance=player.get('alarm_reinforcement_chance', 0.25),
        tr=tr,
        tr_value=tr_value,
        get_current_room=current_room,
    )


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
    update_profile_after_run(status=status, duration=duration, end_reason=end_reason, score=score)



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
    global world, player, player_name, core_x, core_y, HACK_TIME, COMBAT_TIME, REFLEX_TIME, DIFFICULTY_MULTIPLIER, player_profile, player_profile_path, WORLD_RULES, ALARM_THRESHOLD, ALARM_MAX, MEGASTRUCTURES
    player_name = input(tr("startup.player_name_prompt")).strip() or "ANON"
    print(tr("startup.player_name_echo", name=player_name))
    player_profile, player_profile_path, is_new_profile = load_or_create_player_profile(player_name)
    MEGASTRUCTURES = load_megastructures(CURRENT_LANGUAGE)
    if is_new_profile:
        print(tr("profile.new_hacker"))
    else:
        print(tr("profile.access_granted"))
        show_profile_stats(typewriter=True)

    mission_modifiers = {}
    selected_structure = choose_structure_for_run(player_profile, MEGASTRUCTURES)
    if selected_structure:
        if player_profile is not None and player_profile_path is not None:
            player_profile['active_structure_id'] = selected_structure.get('id')
            pm_save_player_profile(player_profile, player_profile_path)
        read_mail = input("\n" + tr("quest.new_mail_prompt")).strip().lower()
        if read_mail == 'y':
            mail_data = build_briefing_mail(player_name, selected_structure, tr, CURRENT_LANGUAGE)
            print("\n" + tr("quest.mail.title"))
            print(mail_data['text'])
            mail_path = copy_mail_to_console(CURRENT_LANGUAGE, mail_data)
            print("\n" + tr("quest.mail.copied", path=mail_path))
            infiltrate = input("\n" + tr("quest.infiltrate_prompt")).strip().lower()
            if infiltrate == 'y':
                mission_modifiers = dict(mail_data.get('modifiers', {}))
                apply_starter_pack_to_profile(
                    player_profile,
                    player_profile_path,
                    pm_save_player_profile,
                    mail_data.get('starter_credits', 0),
                    mail_data.get('starter_items', []),
                )
                print("\n" + tr("quest.mission_pack"))
            else:
                print("\n" + tr("quest.mission_skipped"))

    pending_pre_run_upgrades = pre_run_shop()
    
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

    WORLD_RULES = build_world_rules(mission_modifiers)
    ALARM_THRESHOLD = WORLD_RULES['alarm_reinforcement_threshold']
    ALARM_MAX = WORLD_RULES['alarm_max']
    
    # Reset world
    world = [[Room(x, y) for x in range(WIDTH)] for y in range(HEIGHT)]
    if selected_structure is None:
        fallback_story = random.choice(tr_value("content.rom_story_archive"))
        selected_structure = {
            'id': fallback_story.get('id', 'UNKNOWN'),
            'title': fallback_story.get('title', 'Unknown'),
            'hacker': fallback_story.get('hacker', 'N/A'),
            'bio': fallback_story.get('bio', ''),
            'logs': list(fallback_story.get('logs', [])),
            'epilogue': fallback_story.get('epilogue', ''),
            'fragments': list(fallback_story.get('fragments', [])),
        }
    active_story = selected_structure
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
    world[core_y][core_x].enemy_hp = WORLD_RULES.get('core_enemy_hp', 75)
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
    starting_inventory = get_bank_inventory_for_run()
    player = {
        "x": spawn_x,
        "y": spawn_y,
        "hp": 100,
        "energy": 100,
        "hack": 55,
        "inventory": starting_inventory,
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
        "next_structure_unlocked": False,
        "alarm_step": WORLD_RULES['alarm_step'],
        "alarm_reinforcement_chance": WORLD_RULES['alarm_reinforcement_chance'],
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
    apply_upgrade_ids_to_player(player, pending_pre_run_upgrades)
    sync_profile_inventory_from_player()
    
    intro()
    print("\n" + tr("main.story_channel", story_id=player['active_story']['id']))
    describe()
    while True:
        if player['hp'] <= 0:
            print(tr("main.death"))
            save_score(status="LOOSE", end_reason="death")
            break
        if player['alarm'] >= ALARM_MAX:
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
        elif cmd == 'console' or should_open_ssh_console(cmd):
            open_personal_console()
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
