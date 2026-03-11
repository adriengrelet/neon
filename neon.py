#!/usr/bin/env python3
import random
import os
import sys
import time
import json
from termfx import color as color_text, color_choice_line, normalize_ansi_escapes, supports_ansi
from console import launch_console
from player_manage import (
    load_or_create_player_profile as pm_load_or_create_player_profile,
    update_profile_after_run as pm_update_profile_after_run,
    save_player_profile as pm_save_player_profile,
    format_inventory_counts,
    get_bank_inventory_for_run as pm_get_bank_inventory_for_run,
    sync_profile_inventory_from_player as pm_sync_profile_inventory_from_player,
    build_profile_lines,
    ensure_progression as pm_ensure_progression,
    allocate_attribute_point as pm_allocate_attribute_point,
    get_profile_attribute_bonuses as pm_get_profile_attribute_bonuses,
    take_from_room as pm_take_from_room,
    use_inventory_item as pm_use_inventory_item,
    show_inventory as pm_show_inventory,
    show_runtime_player_stats as pm_show_runtime_player_stats,
    save_run_score as pm_save_run_score,
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
from world import (
    current_room as world_current_room,
    draw_map as world_draw_map,
    get_echo_marker as world_get_echo_marker,
    describe as world_describe,
    move as world_move,
    scan as world_scan,
    echo_scan as world_echo_scan,
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASCII_ART_REGISTRY_PATH = os.path.join(BASE_DIR, "ascii_art_registry.json")
INTRO_ASCII_ART_ID = "intro_neon_core_v1"
ASCII_ART_REGISTRY_CACHE = None

DEFAULT_LANGUAGE = "fr"
CURRENT_LANGUAGE = DEFAULT_LANGUAGE
SUPPORTED_LANGUAGES = ("fr", "en", "it", "es")
LANGUAGE_LABELS = {
    "fr": "Francais",
    "en": "English",
    "it": "Italiano",
    "es": "Espanol",
}

LANG_DIR = os.path.join(BASE_DIR, "lang")


def load_translations():
    loaded = {}
    for code in SUPPORTED_LANGUAGES:
        path = os.path.join(LANG_DIR, f"{code}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                loaded[code] = data
            else:
                loaded[code] = {}
        except (OSError, json.JSONDecodeError):
            loaded[code] = {}
    return loaded


def load_ascii_art_registry(force_reload=False):
    global ASCII_ART_REGISTRY_CACHE
    if not force_reload and isinstance(ASCII_ART_REGISTRY_CACHE, dict):
        return ASCII_ART_REGISTRY_CACHE

    try:
        with open(ASCII_ART_REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            ASCII_ART_REGISTRY_CACHE = data
            return ASCII_ART_REGISTRY_CACHE
    except (OSError, json.JSONDecodeError):
        pass

    ASCII_ART_REGISTRY_CACHE = {}
    return ASCII_ART_REGISTRY_CACHE


def terminal_supports_ansi():
    return supports_ansi()


def normalize_ansi_sequences(text):
    return normalize_ansi_escapes(text)


def menu_text(text):
    return color_choice_line(text)


def stats_text(text):
    return color_text(text, "yellow")


def format_mail_with_colored_timestamp(mail_text):
    timestamp_prefix = f"{tr('quest.mail.timestamp')}:"
    lines = []
    for line in str(mail_text).splitlines():
        if line.startswith(timestamp_prefix):
            lines.append(color_text(line, "green"))
        else:
            lines.append(line)
    return "\n".join(lines)


def get_ascii_art_text(art_id, prefer_ansi=True):
    registry = load_ascii_art_registry()
    artworks = registry.get("artworks", {})
    if not isinstance(artworks, dict):
        return ""

    entry = artworks.get(art_id)
    if not isinstance(entry, dict):
        return ""

    variants = entry.get("variants", {})
    if not isinstance(variants, dict):
        return ""

    if prefer_ansi:
        variant_order = registry.get("default_variant_order", ["ansi", "plain"])
        if not isinstance(variant_order, list):
            variant_order = ["ansi", "plain"]
    else:
        variant_order = ["plain", "ansi"]

    for variant_name in variant_order:
        variant = variants.get(variant_name)
        if not isinstance(variant, dict):
            continue
        if variant.get("enabled") is False:
            continue
        lines = variant.get("lines")
        if isinstance(lines, list) and lines:
            text = "\n".join(str(line) for line in lines)
            if variant_name == "ansi":
                text = normalize_ansi_sequences(text)
            return text

    return ""


def get_ascii_art_id_for_zone(zone_key, fallback_id=""):
    registry = load_ascii_art_registry()
    zone_index = registry.get("zone_index", {})
    if not isinstance(zone_index, dict):
        return fallback_id

    zone_id = zone_index.get(zone_key)
    if isinstance(zone_id, str) and zone_id.strip():
        return zone_id
    return fallback_id


def print_ascii_art_by_id(art_id, prefer_ansi=True):
    if not art_id:
        return False

    use_ansi = bool(prefer_ansi and terminal_supports_ansi())
    art = get_ascii_art_text(art_id, prefer_ansi=use_ansi)
    if not art and use_ansi:
        art = get_ascii_art_text(art_id, prefer_ansi=False)
    if not art:
        return False

    print(art)
    return True


def enemy_zone_key(enemy_name):
    enemy = str(enemy_name or "").strip().lower()
    if not enemy:
        return "encounter.enemy.default"
    if "core sentinel" in enemy:
        return "encounter.enemy.core_sentinel"
    if "proxy" in enemy:
        return "encounter.enemy.proxy_hunter"
    if "sentry" in enemy or "sentinela" in enemy or "sentinella" in enemy:
        return "encounter.enemy.sentry_bot"
    if "guard" in enemy or "guardia" in enemy:
        return "encounter.enemy.guard"
    if "drone" in enemy or enemy.startswith("dron"):
        return "encounter.enemy.drone"
    return "encounter.enemy.default"


def show_enemy_encounter_ascii(enemy_name):
    zone_key = enemy_zone_key(enemy_name)
    art_id = get_ascii_art_id_for_zone(zone_key, fallback_id="enemy_unknown_v1")
    print_ascii_art_by_id(art_id, prefer_ansi=True)


def show_hack_request_ascii():
    art_id = get_ascii_art_id_for_zone("action.hack.request", fallback_id="hack_terminal_request_v1")
    print_ascii_art_by_id(art_id, prefer_ansi=True)


def show_core_discovery_ascii():
    art_id = get_ascii_art_id_for_zone("discover.core.first_contact", fallback_id="discover_core_v1")
    print_ascii_art_by_id(art_id, prefer_ansi=True)


TRANSLATIONS = load_translations()

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
    print("\n" + menu_text("=== LANGUAGE SELECTION ==="))
    print(menu_text("Available codes:"))
    for code in SUPPORTED_LANGUAGES:
        print(menu_text(f"- {code} : {LANGUAGE_LABELS[code]}"))

    while True:
        choice = input(menu_text("Language (fr/en/it/es) > ")).strip().lower()
        if choice in SUPPORTED_LANGUAGES:
            CURRENT_LANGUAGE = choice
            print(menu_text(f"Active language: {choice} ({LANGUAGE_LABELS[choice]})"))
            return
        print(menu_text("Invalid code. Use fr, en, it, es."))


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


def show_win_end_sequence(summary_lines):
    gagne_line = " ".join(["WINNER"] * 15)
    typewriter_print(color_text(gagne_line, "red"), char_delay=0.01, line_delay=0.35, speed_factor=0.6)
    for line in summary_lines:
        typewriter_print(line)


def normalize_credits():
    player['credits'] = round_int(player['credits'])


def normalize_primary_stats():
    max_hp = int(player.get('max_hp', 100))
    max_energy = int(player.get('max_energy', 100))
    player['hp'] = min(max_hp, round_int(player['hp']))
    player['energy'] = max(0, min(max_energy, round_int(player['energy'])))
    player['hack'] = min(100, round_int(player['hack']))


def effective_energy_cost(base_cost):
    profile_scale = float(player.get('endurance_energy_scale', 1.0))
    scaled_cost = max(1, round_int(base_cost * WORLD_RULES.get('energy_cost_scale', 1.0) * profile_scale))
    if player.get('energy_dissipator_bought'):
        return max(1, scaled_cost // 2)
    return scaled_cost


def choose_difficulty():
    global HACK_TIME, COMBAT_TIME, REFLEX_TIME, DIFFICULTY_MULTIPLIER
    print("\n" + menu_text(tr("startup.difficulty_title")))
    print(menu_text(tr("startup.difficulty_1")))
    print(menu_text(tr("startup.difficulty_2")))
    print(menu_text(tr("startup.difficulty_3")))
    print(menu_text(tr("startup.difficulty_4")))

    difficulty = input(menu_text(tr("startup.difficulty_prompt"))).strip()
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
        print(menu_text(tr("startup.difficulty_invalid")))
        HACK_TIME = 30
        COMBAT_TIME = 4
        REFLEX_TIME = 2
        DIFFICULTY_MULTIPLIER = 3


def evolution_menu():
    global player_profile
    if player_profile is None or player_profile_path is None:
        return

    while True:
        pm_ensure_progression(player_profile)
        attrs = player_profile.get('attributes', {})
        print("\n" + menu_text(tr("startup.evo.title", default="=== EVOLUTION ===")))
        print(menu_text(tr(
            "startup.evo.level",
            default="Level {level} | XP {xp}/{req} | Points: {points}",
            level=int(player_profile.get('level', 1)),
            xp=int(player_profile.get('xp_in_level', 0)),
            req=int(player_profile.get('xp_next_level_requirement', 12000)),
            points=int(player_profile.get('evolution_points', 0)),
        )))
        print(menu_text(tr("startup.evo.vitality", default="1. Vitality (+5 max HP)") + f" [{int(attrs.get('vitality', 0))}]"))
        print(menu_text(tr("startup.evo.endurance", default="2. Endurance (+5 max EN, -1% energy costs)") + f" [{int(attrs.get('endurance', 0))}]"))
        print(menu_text(tr("startup.evo.intrusion", default="3. Intrusion (+2 base HK)") + f" [{int(attrs.get('intrusion', 0))}]"))
        print(menu_text(tr("startup.evo.composure", default="4. Composure (+1 alarm cap each 3 pts)") + f" [{int(attrs.get('composure', 0))}]"))
        print(menu_text(tr("startup.evo.back", default="0. Back")))
        choice = input(menu_text(tr("startup.evo.prompt", default="Choice > "))).strip()
        key_map = {
            '1': 'vitality',
            '2': 'endurance',
            '3': 'intrusion',
            '4': 'composure',
        }
        if choice == '0':
            pm_save_player_profile(player_profile, player_profile_path)
            return
        attr_key = key_map.get(choice)
        if not attr_key:
            print(menu_text(tr("startup.evo.invalid", default="Invalid choice.")))
            continue
        if pm_allocate_attribute_point(player_profile, attr_key):
            pm_save_player_profile(player_profile, player_profile_path)
            print(tr("startup.evo.applied", default="Attribute point invested."))
        else:
            print(tr("startup.evo.no_points", default="No evolution points available."))


def startup_hub(selected_structure, mail_data):
    mission_modifiers = {}
    pending_pre_run_upgrades = []
    seen_mail = False
    mission_ready = False
    mission_pack_applied = False

    while True:
        print("\n" + menu_text(tr("startup.hub.title", default="=== PRE-RUN HUB ===")))
        if selected_structure:
            print(menu_text(tr("startup.hub.new_mail", default="You have a new mail.")))
        print(menu_text(tr("startup.hub.opt_mail", default="1. Read mission mail")))
        print(menu_text(tr("startup.hub.opt_console", default="2. Open personal console")))
        print(menu_text(tr("startup.hub.opt_shop", default="3. Pre-run shop")))
        print(menu_text(tr("startup.hub.opt_evo", default="4. Evolution")))
        print(menu_text(tr("startup.hub.opt_run", default="5. Quick run")))
        if mission_ready:
            print(menu_text(tr("startup.hub.opt_run_mail", default="6. Run Mission Mail")))
        print(menu_text(tr("startup.hub.opt_quit", default="0. QUIT GAME")))
        choice = input(menu_text(tr("startup.hub.prompt", default="Choice > "))).strip()

        if choice == '1':
            if selected_structure is None or mail_data is None:
                print(tr("startup.hub.no_mail", default="No mission mail available."))
                continue
            seen_mail = True
            print("\n" + tr("quest.mail.title"))
            print(format_mail_with_colored_timestamp(mail_data['text']))
            mail_path = copy_mail_to_console(CURRENT_LANGUAGE, mail_data)
            print("\n" + tr("quest.mail.copied", path=mail_path))
            infiltrate = input("\n" + menu_text(tr("quest.infiltrate_prompt"))).strip().lower()
            if infiltrate == 'y':
                mission_ready = True
                mission_modifiers = dict(mail_data.get('modifiers', {}))
                if not mission_pack_applied:
                    apply_starter_pack_to_profile(
                        player_profile,
                        player_profile_path,
                        pm_save_player_profile,
                        mail_data.get('starter_credits', 0),
                        mail_data.get('starter_items', []),
                    )
                    mission_pack_applied = True
                    print("\n" + tr("quest.mission_pack"))
                print("\n" + tr("startup.hub.mission_ready", default="Mission ready. You can now choose 6. Run Mission Mail."))
            else:
                if mission_ready:
                    print("\n" + tr("startup.hub.mission_still_ready", default="Mission remains armed. Choose 6. Run Mission Mail when ready."))
                else:
                    mission_modifiers = {}
                    print("\n" + tr("quest.mission_skipped"))
        elif choice == '2':
            open_personal_console()
        elif choice == '3':
            pending_pre_run_upgrades = run_pre_run_shop(
                player_profile,
                player_profile_path,
                tr,
                pm_save_player_profile,
                format_inventory_counts,
                ask_confirmation=False,
            )
        elif choice == '4':
            evolution_menu()
        elif choice == '5':
            if selected_structure and not seen_mail:
                print(tr("startup.hub.mail_reminder", default="You still have unread mission mail."))
            return mission_modifiers, pending_pre_run_upgrades, False
        elif choice == '6':
            if not mission_ready:
                print(tr("startup.hub.mission_not_ready", default="Read and accept mission mail first."))
                continue
            return mission_modifiers, pending_pre_run_upgrades, False
        elif choice == '0':
            return {}, [], True
        else:
            print(menu_text(tr("startup.hub.invalid", default="Invalid choice.")))


def show_status_line():
    if SHOW_STATUS_LINE:
        normalize_primary_stats()
        normalize_credits()
        print(stats_text(tr(
            "statusline.compact",
            hp=player['hp'],
            energy=player['energy'],
            hack=player['hack'],
            alarm=player['alarm'],
            credits=player['credits'],
            fragments=len(player['rom_fragments']),
        )))


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
        print("\n" + color_text(tr("fragments.unlocked"), "red"))
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
        read_story = input(menu_text(tr("fragments.read_prompt"))).strip().lower()
        if read_story == 'y':
            show_story_log(story)
    else:
        print("\n" + tr("fragments.incomplete"))


def status():
    normalize_primary_stats()
    normalize_credits()
    print("\n" + stats_text(tr("status.title")))
    if player['synaptique_bought']:
        print(stats_text(tr("status.synaptique")))
    if player['surcharge_bought']:
        print(stats_text(tr("status.surcharge")))
    if player['interface_bought']:
        print(stats_text(tr("status.interface")))
    if player['combat_chip_bought']:
        print(stats_text(tr("status.combat_chip")))
    if player['force_bought']:
        print(stats_text(tr("status.force")))
    if player['vitesse_bought']:
        print(stats_text(tr("status.vitesse")))
    if player['energy_dissipator_bought']:
        print(stats_text(tr("status.dissipateur")))
    if not any([
        player['synaptique_bought'],
        player['surcharge_bought'],
        player['interface_bought'],
        player['combat_chip_bought'],
        player['force_bought'],
        player['vitesse_bought'],
        player['energy_dissipator_bought'],
    ]):
        print(stats_text(tr("status.none")))
    pm_show_runtime_player_stats(player, tr, normalize_primary_stats, normalize_credits)


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



def core_check():
    room = world_current_room(world, player)
    if room.core and not room.enemy and player['core_hacked']:
        print("\n" + tr("core.pirated"))
        score_result = pm_save_run_score(
            player=player,
            player_name=player_name,
            status="WIN",
            end_reason="win",
            hack_time=HACK_TIME,
            difficulty_multiplier=DIFFICULTY_MULTIPLIER,
            rom_bonus_score=ROM_BONUS_SCORE,
            tr=tr,
            normalize_primary_stats=normalize_primary_stats,
            normalize_credits=normalize_credits,
            update_profile_callback=update_profile_after_run,
            print_summary=False,
        )
        summary_lines = []
        if isinstance(score_result, dict):
            summary_lines = score_result.get("summary_lines", [])
        show_win_end_sequence(summary_lines)
        return True
    return False


def main():
    clear()
    intro_art_id = get_ascii_art_id_for_zone("startup.intro", fallback_id=INTRO_ASCII_ART_ID)
    intro_art = get_ascii_art_text(intro_art_id, prefer_ansi=terminal_supports_ansi())
    print(intro_art if intro_art else "NEON CORE")
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
    pm_ensure_progression(player_profile)
    pm_save_player_profile(player_profile, player_profile_path)
    while True:
        selected_structure = choose_structure_for_run(player_profile, MEGASTRUCTURES)
        mail_data = None
        if selected_structure:
            if player_profile is not None and player_profile_path is not None:
                player_profile['active_structure_id'] = selected_structure.get('id')
                pm_save_player_profile(player_profile, player_profile_path)
            mail_data = build_briefing_mail(player_name, selected_structure, tr, CURRENT_LANGUAGE)

        mission_modifiers, pending_pre_run_upgrades, quit_requested = startup_hub(selected_structure, mail_data)
        if quit_requested:
            return

        choose_difficulty()

        WORLD_RULES = build_world_rules(mission_modifiers)
        profile_bonuses = pm_get_profile_attribute_bonuses(player_profile)
        WORLD_RULES['energy_cost_scale'] = WORLD_RULES.get('energy_cost_scale', 1.0) * profile_bonuses['energy_cost_scale']
        ALARM_THRESHOLD = WORLD_RULES['alarm_reinforcement_threshold']
        ALARM_MAX = WORLD_RULES['alarm_max'] + int(profile_bonuses['alarm_max_bonus'])

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
        starting_inventory = pm_get_bank_inventory_for_run(player_profile)
        player = {
            "x": spawn_x,
            "y": spawn_y,
            "hp": int(profile_bonuses['max_hp']),
            "energy": int(profile_bonuses['max_energy']),
            "hack": int(profile_bonuses['base_hack']),
            "max_hp": int(profile_bonuses['max_hp']),
            "max_energy": int(profile_bonuses['max_energy']),
            "endurance_energy_scale": float(profile_bonuses['energy_cost_scale']),
            "profile_attributes": dict(profile_bonuses['attributes']),
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
        # New run starts at full resources according to profile-derived maxima.
        player['hp'] = int(player.get('max_hp', 100))
        player['energy'] = int(player.get('max_energy', 100))
        player_profile = pm_sync_profile_inventory_from_player(player_profile, player_profile_path, player)

        intro()
        print("\n" + tr("main.story_channel", story_id=player['active_story']['id']))
        world_describe(
            world,
            player,
            tr,
            on_enemy_encounter=show_enemy_encounter_ascii,
            on_core_discovered=show_core_discovery_ascii,
        )

        def do_enemy_turn():
            run_enemy_turn(
                player=player,
                alarm_threshold=ALARM_THRESHOLD,
                reinforcement_chance=player.get('alarm_reinforcement_chance', 0.25),
                tr=tr,
                tr_value=tr_value,
                get_current_room=lambda: world_current_room(world, player),
            )

        while True:
            if player['hp'] <= 0:
                print(tr("main.death"))
                pm_save_run_score(
                    player=player,
                    player_name=player_name,
                    status="LOOSE",
                    end_reason="death",
                    hack_time=HACK_TIME,
                    difficulty_multiplier=DIFFICULTY_MULTIPLIER,
                    rom_bonus_score=ROM_BONUS_SCORE,
                    tr=tr,
                    normalize_primary_stats=normalize_primary_stats,
                    normalize_credits=normalize_credits,
                    update_profile_callback=update_profile_after_run,
                )
                break
            if player['alarm'] >= ALARM_MAX:
                print(tr("main.alarm_game_over"))
                pm_save_run_score(
                    player=player,
                    player_name=player_name,
                    status="LOOSE",
                    end_reason="alarm",
                    hack_time=HACK_TIME,
                    difficulty_multiplier=DIFFICULTY_MULTIPLIER,
                    rom_bonus_score=ROM_BONUS_SCORE,
                    tr=tr,
                    normalize_primary_stats=normalize_primary_stats,
                    normalize_credits=normalize_credits,
                    update_profile_callback=update_profile_after_run,
                )
                break
            if core_check():
                break
            show_status_line()
            player['attacked_this_turn'] = False
            cmd = input(tr("ui.command_prompt")).strip().lower()
            if cmd in ('north', 'n'):
                world_move(
                    world,
                    player,
                    WIDTH,
                    HEIGHT,
                    0,
                    -1,
                    tr,
                    do_enemy_turn,
                    on_enemy_encounter=show_enemy_encounter_ascii,
                    on_core_discovered=show_core_discovery_ascii,
                )
            elif cmd in ('south', 's'):
                world_move(
                    world,
                    player,
                    WIDTH,
                    HEIGHT,
                    0,
                    1,
                    tr,
                    do_enemy_turn,
                    on_enemy_encounter=show_enemy_encounter_ascii,
                    on_core_discovered=show_core_discovery_ascii,
                )
            elif cmd in ('east', 'e'):
                world_move(
                    world,
                    player,
                    WIDTH,
                    HEIGHT,
                    1,
                    0,
                    tr,
                    do_enemy_turn,
                    on_enemy_encounter=show_enemy_encounter_ascii,
                    on_core_discovered=show_core_discovery_ascii,
                )
            elif cmd in ('west', 'w'):
                world_move(
                    world,
                    player,
                    WIDTH,
                    HEIGHT,
                    -1,
                    0,
                    tr,
                    do_enemy_turn,
                    on_enemy_encounter=show_enemy_encounter_ascii,
                    on_core_discovered=show_core_discovery_ascii,
                )
            elif cmd in ('scan', 'sc'):
                world_scan(
                    world,
                    player,
                    tr,
                    tr_value,
                    WORLD_RULES,
                    effective_energy_cost,
                    do_enemy_turn,
                )
            elif cmd in ('echo', 'ec'):
                world_echo_scan(world, player, WIDTH, HEIGHT, tr, effective_energy_cost)
                world_draw_map(world, player, WIDTH, HEIGHT, tr, show_legend=True)
            elif cmd in ('hack', 'h'):
                show_hack_request_ascii()
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
                    get_current_room=lambda: world_current_room(world, player),
                    get_echo_marker=world_get_echo_marker,
                    draw_map=lambda show_legend=True: world_draw_map(world, player, WIDTH, HEIGHT, tr, show_legend=show_legend),
                    effective_energy_cost=effective_energy_cost,
                    normalize_primary_stats=normalize_primary_stats,
                    normalize_credits=normalize_credits,
                    round_int=round_int,
                )
            elif cmd in ('attack', 'at'):
                run_attack(
                    player=player,
                    combat_time=COMBAT_TIME,
                    reflex_time=REFLEX_TIME,
                    tr=tr,
                    get_current_room=lambda: world_current_room(world, player),
                    normalize_primary_stats=normalize_primary_stats,
                )
                player['attacked_this_turn'] = True
            elif cmd in ('take', 't'):
                pm_take_from_room(
                    player,
                    world_current_room(world, player),
                    tr,
                    lambda: pm_sync_profile_inventory_from_player(player_profile, player_profile_path, player),
                )
            elif cmd.startswith('use ') or cmd.startswith('u '):
                pm_use_inventory_item(
                    player,
                    cmd.split(' ', 1)[1],
                    tr,
                    normalize_primary_stats,
                    lambda: pm_sync_profile_inventory_from_player(player_profile, player_profile_path, player),
                )
            elif cmd in ('inventory', 'inv'):
                pm_show_inventory(player, tr)
            elif cmd in ('status', 'stat'):
                status()
            elif cmd in ('profile', 'pro'):
                show_profile_stats()
            elif cmd in ('fragments', 'fra'):
                fragments_menu()
            elif cmd in ('map', 'm'):
                world_draw_map(world, player, WIDTH, HEIGHT, tr)
            elif cmd in ('shop', 'sh'):
                run_in_game_shop(
                    player,
                    tr,
                    normalize_credits,
                    lambda: pm_sync_profile_inventory_from_player(player_profile, player_profile_path, player),
                )
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
                    pm_save_run_score(
                        player=player,
                        player_name=player_name,
                        status='QUIT',
                        end_reason='quit',
                        hack_time=HACK_TIME,
                        difficulty_multiplier=DIFFICULTY_MULTIPLIER,
                        rom_bonus_score=ROM_BONUS_SCORE,
                        tr=tr,
                        normalize_primary_stats=normalize_primary_stats,
                        normalize_credits=normalize_credits,
                        update_profile_callback=update_profile_after_run,
                    )
                    break
            else:
                print(tr("ui.unknown_command"))
            normalize_primary_stats()
            normalize_credits()
            if not player['attacked_this_turn'] and world_current_room(world, player).enemy:
                run_enemy_attack(
                    player=player,
                    tr=tr,
                    get_current_room=lambda: world_current_room(world, player),
                    normalize_primary_stats=normalize_primary_stats,
                )

        show_leaderboard()
        print("\n" + tr("ui.return_hub", default="Returning to pre-run hub..."))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(tr("error.unhandled", error=e))
        import traceback
        traceback.print_exc()
