#!/usr/bin/env python3
import os
import re
import json
import shutil
import time
from datetime import datetime
from termfx import color as color_text


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SAVES_DIR = os.path.join(BASE_DIR, "saves")
SHARED_STATS_DIR = os.path.join(BASE_DIR, "stats")
LEADERBOARD_PATH = os.path.join(BASE_DIR, "leaderboard.md")
SUPPORTED_CONSOLE_LANGUAGES = ("fr", "en", "es", "it")


ATTRIBUTE_KEYS = ("vitality", "endurance", "intrusion", "composure")


def _is_within_root(path, root):
    real_path = os.path.realpath(path)
    real_root = os.path.realpath(root)
    try:
        return os.path.commonpath([real_root, real_path]) == real_root
    except ValueError:
        return False


def _mount_stats_link(console_stats_path, shared_stats_dir):
    if os.path.islink(console_stats_path):
        if os.path.realpath(console_stats_path) == os.path.realpath(shared_stats_dir):
            return
        os.unlink(console_stats_path)
    elif os.path.isdir(console_stats_path):
        for name in sorted(os.listdir(console_stats_path)):
            src = os.path.join(console_stats_path, name)
            dst = os.path.join(shared_stats_dir, name)
            if os.path.isfile(src):
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
        try:
            os.rmdir(console_stats_path)
        except OSError:
            # Keep directory fallback if it cannot be replaced by a link.
            return
    elif os.path.exists(console_stats_path):
        return

    try:
        os.symlink(shared_stats_dir, console_stats_path)
    except OSError:
        os.makedirs(console_stats_path, exist_ok=True)


def _ensure_console_stats_links(shared_stats_dir):
    for lang in SUPPORTED_CONSOLE_LANGUAGES:
        console_root = os.path.join(BASE_DIR, f"console_{lang}")
        os.makedirs(console_root, exist_ok=True)
        _mount_stats_link(os.path.join(console_root, "stats"), shared_stats_dir)


def sync_stats_exports(
    saves_dir=DEFAULT_SAVES_DIR,
    shared_stats_dir=SHARED_STATS_DIR,
    leaderboard_path=LEADERBOARD_PATH,
):
    os.makedirs(shared_stats_dir, exist_ok=True)

    exported_json_names = set()
    if os.path.isdir(saves_dir):
        for name in sorted(os.listdir(saves_dir)):
            src = os.path.join(saves_dir, name)
            if not (os.path.isfile(src) and name.lower().endswith(".json")):
                continue
            if not _is_within_root(src, saves_dir):
                continue
            shutil.copy2(src, os.path.join(shared_stats_dir, name))
            exported_json_names.add(name)

    for name in sorted(os.listdir(shared_stats_dir)):
        dst = os.path.join(shared_stats_dir, name)
        if not (os.path.isfile(dst) and name.lower().endswith(".json")):
            continue
        if name not in exported_json_names:
            os.remove(dst)

    leaderboard_dst = os.path.join(shared_stats_dir, "leaderboard.md")
    if os.path.isfile(leaderboard_path):
        shutil.copy2(leaderboard_path, leaderboard_dst)
    elif os.path.exists(leaderboard_dst):
        os.remove(leaderboard_dst)

    _ensure_console_stats_links(shared_stats_dir)


def xp_requirement_for_level(level):
    """XP needed to go from `level` to `level + 1`."""
    lvl = max(1, int(level))
    if lvl == 1:
        return 12000
    if lvl == 2:
        return 15000
    if lvl == 3:
        return 20000
    return 20000 + ((lvl - 3) * 5000)


def _sanitize_attributes(attributes):
    if not isinstance(attributes, dict):
        attributes = {}
    sanitized = {}
    for key in ATTRIBUTE_KEYS:
        sanitized[key] = max(0, int(attributes.get(key, 0)))
    return sanitized


def compute_level_progress(xp_total):
    xp_pool = max(0, int(xp_total))
    level = 1
    while True:
        req = xp_requirement_for_level(level)
        if xp_pool < req:
            return {
                "level": level,
                "xp_in_level": xp_pool,
                "xp_to_next": req - xp_pool,
                "xp_required_next": req,
            }
        xp_pool -= req
        level += 1


def ensure_progression(profile):
    if not isinstance(profile, dict):
        return profile, 0

    profile["xp_total"] = max(0, int(profile.get("xp_total", 0)))
    profile["xp_last_gain"] = max(0, int(profile.get("xp_last_gain", 0)))
    profile["attributes"] = _sanitize_attributes(profile.get("attributes"))

    progress = compute_level_progress(profile["xp_total"])
    old_level = max(1, int(profile.get("level", progress["level"])))
    new_level = progress["level"]
    gained_levels = max(0, new_level - old_level)

    spent_points = sum(profile["attributes"].values())
    if "evolution_points" in profile:
        evolution_points = max(0, int(profile.get("evolution_points", 0)))
    else:
        evolution_points = max(0, (new_level - 1) - spent_points)

    if gained_levels > 0:
        evolution_points += gained_levels

    profile["level"] = new_level
    profile["evolution_points"] = evolution_points
    profile["xp_in_level"] = progress["xp_in_level"]
    profile["xp_to_next_level"] = progress["xp_to_next"]
    profile["xp_next_level_requirement"] = progress["xp_required_next"]

    bonuses = get_profile_attribute_bonuses(profile)
    profile["max_hp"] = int(bonuses["max_hp"])
    profile["max_energy"] = int(bonuses["max_energy"])
    profile["base_hack"] = int(bonuses["base_hack"])
    profile["alarm_max_bonus"] = int(bonuses["alarm_max_bonus"])
    profile["endurance_energy_scale"] = float(bonuses["energy_cost_scale"])
    return profile, gained_levels


def allocate_attribute_point(profile, attribute_key):
    if attribute_key not in ATTRIBUTE_KEYS:
        return False
    ensure_progression(profile)
    points = int(profile.get("evolution_points", 0))
    if points <= 0:
        return False
    attributes = _sanitize_attributes(profile.get("attributes"))
    attributes[attribute_key] += 1
    profile["attributes"] = attributes
    profile["evolution_points"] = points - 1
    return True


def get_profile_attribute_bonuses(profile):
    attrs = _sanitize_attributes(profile.get("attributes") if isinstance(profile, dict) else None)
    vitality = attrs["vitality"]
    endurance = attrs["endurance"]
    intrusion = attrs["intrusion"]
    composure = attrs["composure"]

    return {
        "max_hp": 100 + vitality * 5,
        "max_energy": 100 + endurance * 5,
        "base_hack": 55 + intrusion * 2,
        "alarm_max_bonus": composure // 3,
        "energy_cost_scale": max(0.65, 1.0 - endurance * 0.01),
        "attributes": attrs,
    }


def sanitize_player_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return cleaned or "ANON"


def get_player_profile_path(name, saves_dir):
    safe_name = sanitize_player_name(name)
    return os.path.join(saves_dir, f"{safe_name}.json")


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
        "bank_credits": 0,
        "bank_inventory": [],
        "xp_total": 0,
        "xp_last_gain": 0,
        "level": 1,
        "evolution_points": 0,
        "attributes": {
            "vitality": 0,
            "endurance": 0,
            "intrusion": 0,
            "composure": 0,
        },
        "xp_in_level": 0,
        "xp_to_next_level": 12000,
        "xp_next_level_requirement": 12000,
        "visited_structures": [],
        "next_structure_id": None,
        "active_structure_id": None,
    }


def save_player_profile(profile, path):
    ensure_progression(profile)
    profile["last_seen"] = datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    try:
        sync_stats_exports()
    except OSError:
        pass


def load_or_create_player_profile(name, saves_dir):
    os.makedirs(saves_dir, exist_ok=True)
    path = get_player_profile_path(name, saves_dir)
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
        if not isinstance(profile.get("bank_inventory"), list):
            profile["bank_inventory"] = []
        profile["bank_credits"] = int(profile.get("bank_credits", 0))
        profile["xp_total"] = int(profile.get("xp_total", 0))
        profile["xp_last_gain"] = int(profile.get("xp_last_gain", 0))
        profile["level"] = int(profile.get("level", 1))
        profile["evolution_points"] = int(profile.get("evolution_points", 0))
        profile["attributes"] = _sanitize_attributes(profile.get("attributes"))
        if not isinstance(profile.get("visited_structures"), list):
            profile["visited_structures"] = []
        next_structure_id = profile.get("next_structure_id")
        profile["next_structure_id"] = next_structure_id if isinstance(next_structure_id, str) and next_structure_id else None
        active_structure_id = profile.get("active_structure_id")
        profile["active_structure_id"] = active_structure_id if isinstance(active_structure_id, str) and active_structure_id else None
        if "created_at" not in profile or not profile["created_at"]:
            profile["created_at"] = defaults["created_at"]
        ensure_progression(profile)
        save_player_profile(profile, path)
        return profile, path, False

    profile = defaults.copy()
    save_player_profile(profile, path)
    return profile, path, True


def update_profile_after_run(profile, path, player, status, duration, end_reason=None, score=0):
    if not profile or not path:
        return profile

    profile["total_runs"] = int(profile.get("total_runs", 0)) + 1
    profile["megastructures_visited"] = int(profile.get("megastructures_visited", 0)) + 1
    profile["total_play_time_seconds"] = int(profile.get("total_play_time_seconds", 0)) + int(duration)
    profile["total_hacks_success"] = int(profile.get("total_hacks_success", 0)) + int(player.get("hacks_success", 0))
    profile["total_hacks_failed"] = int(profile.get("total_hacks_failed", 0)) + int(player.get("hacks_failed", 0))
    profile["total_rooms_visited"] = int(profile.get("total_rooms_visited", 0)) + int(player.get("rooms_visited", 0))
    profile["total_rom_fragments_collected"] = int(profile.get("total_rom_fragments_collected", 0)) + len(player.get("rom_fragments", []))
    profile["last_status"] = status

    if status == "WIN":
        profile["wins"] = int(profile.get("wins", 0)) + 1
    elif status == "QUIT":
        profile["abandons"] = int(profile.get("abandons", 0)) + 1
    elif status == "LOOSE":
        profile["losses"] = int(profile.get("losses", 0)) + 1

    if end_reason == "death":
        profile["deaths"] = int(profile.get("deaths", 0)) + 1

    xp_gain = max(0, int(int(score) * 0.10))
    profile["xp_last_gain"] = xp_gain
    profile["xp_total"] = int(profile.get("xp_total", 0)) + xp_gain
    ensure_progression(profile)

    if status == "WIN":
        profile["bank_credits"] = int(profile.get("bank_credits", 0)) + int(player.get("credits", 0))

    save_player_profile(profile, path)
    return profile


def count_inventory_items(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def format_inventory_counts(items):
    counts = count_inventory_items(items)
    if not counts:
        return "[]"
    chunks = []
    for key in sorted(counts.keys()):
        chunks.append(f"{key} x{counts[key]}")
    return ", ".join(chunks)


def get_bank_inventory_for_run(profile):
    if not profile:
        return []
    bank_inventory = profile.get("bank_inventory", [])
    if not isinstance(bank_inventory, list):
        bank_inventory = []
    return list(bank_inventory)


def sync_profile_inventory_from_player(profile, path, player):
    if not profile or not path:
        return profile
    if not isinstance(profile.get("bank_inventory"), list):
        profile["bank_inventory"] = []
    profile["bank_inventory"] = list(player.get("inventory", []))
    save_player_profile(profile, path)
    return profile


def build_profile_lines(profile, player_name, tr, format_duration_hms):
    ensure_progression(profile)
    attrs = profile.get("attributes", {})
    endurance_scale = float(profile.get("endurance_energy_scale", 1.0))
    endurance_reduction_percent = int(round((1.0 - endurance_scale) * 100))
    return [
        "\n" + tr("profile.title"),
        tr("profile.name", value=profile.get("player_name", player_name)),
        tr("profile.total_runs", value=profile.get("total_runs", 0)),
        tr("profile.megastructures", value=profile.get("megastructures_visited", 0)),
        tr("profile.wins", value=profile.get("wins", 0)),
        tr("profile.losses", value=profile.get("losses", 0)),
        tr("profile.deaths", value=profile.get("deaths", 0)),
        tr("profile.abandons", value=profile.get("abandons", 0)),
        tr("profile.play_time", value=format_duration_hms(profile.get("total_play_time_seconds", 0))),
        tr("profile.hacks_success", value=profile.get("total_hacks_success", 0)),
        tr("profile.hacks_failed", value=profile.get("total_hacks_failed", 0)),
        tr("profile.rooms_visited", value=profile.get("total_rooms_visited", 0)),
        tr("profile.fragments", value=profile.get("total_rom_fragments_collected", 0)),
        tr("profile.last_status", value=profile.get("last_status", "NONE")),
        tr("profile.bank_credits", value=int(profile.get("bank_credits", 0))),
        tr("profile.active_structure", value=profile.get("active_structure_id") or "NONE"),
        tr("profile.next_structure", value=profile.get("next_structure_id") or "NONE"),
        tr("profile.xp_total", value=int(profile.get("xp_total", 0)), gain=int(profile.get("xp_last_gain", 0))),
        f"Level: {int(profile.get('level', 1))} | Evolution points: {int(profile.get('evolution_points', 0))}",
        f"XP toward next level: {int(profile.get('xp_in_level', 0))}/{int(profile.get('xp_next_level_requirement', 12000))}",
        (
            "Max stats: "
            f"HP {int(profile.get('max_hp', 100))} | "
            f"END/EN {int(profile.get('max_energy', 100))} | "
            f"Base HK {int(profile.get('base_hack', 55))}"
        ),
        f"END bonus: -{max(0, endurance_reduction_percent)}% energy costs",
        (
            "Attributes: "
            f"VIT {int(attrs.get('vitality', 0))} | "
            f"END {int(attrs.get('endurance', 0))} | "
            f"INT {int(attrs.get('intrusion', 0))} | "
            f"COM {int(attrs.get('composure', 0))}"
        ),
        tr("profile.bank_inventory", value=format_inventory_counts(profile.get("bank_inventory", []))),
    ]


def take_from_room(player, room, tr, sync_inventory_callback):
    took_anything = False

    if room.rom_fragment:
        frag = room.rom_fragment
        if frag['id'] not in player['rom_fragments']:
            player['rom_fragments'].append(frag['id'])
            print(tr("take.fragment", fragment_id=frag['id'], count=len(player['rom_fragments'])))
            if len(player['rom_fragments']) == 3:
                print(tr("take.fragments_complete"))
        room.rom_fragment = None
        took_anything = True

    if room.item:
        player['inventory'].append(room.item)
        print(tr("take.item", item=room.item))
        room.item = None
        took_anything = True

    if took_anything:
        sync_inventory_callback()
    else:
        print(tr("take.none"))


def use_inventory_item(player, item, tr, normalize_primary_stats, sync_inventory_callback):
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
    sync_inventory_callback()
    print(tr("use.used", item=item))


def show_inventory(player, tr):
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


def show_runtime_player_stats(player, tr, normalize_primary_stats, normalize_credits):
    normalize_primary_stats()
    normalize_credits()
    attrs = player.get('profile_attributes', {})
    print("\n" + color_text(tr("status.characteristics"), "yellow"))
    print(color_text(
        f"\nHP:{player['hp']}/{int(player.get('max_hp', 100))} "
        f"EN:{player['energy']}/{int(player.get('max_energy', 100))} "
        f"HK:{player['hack']} AL:{player['alarm']} CR:{player['credits']}"
    , "yellow"))
    print(color_text(
        "ATTR "
        f"VIT:{int(attrs.get('vitality', 0))} "
        f"END:{int(attrs.get('endurance', 0))} "
        f"INT:{int(attrs.get('intrusion', 0))} "
        f"COM:{int(attrs.get('composure', 0))}"
    , "yellow"))
    print(color_text(tr("status.fragments", count=len(player['rom_fragments'])), "yellow"))


def save_run_score(
    *,
    player,
    player_name,
    status,
    end_reason,
    hack_time,
    difficulty_multiplier,
    rom_bonus_score,
    tr,
    normalize_primary_stats,
    normalize_credits,
    update_profile_callback,
    leaderboard_path="leaderboard.md",
    print_summary=True,
):
    normalize_primary_stats()
    normalize_credits()
    duration = int(time.time() - player['start_time'])
    rom_bonus = rom_bonus_score if len(player['rom_fragments']) == 3 else 0
    base_score = (
        (player['hp'] + player['energy']) * 10
        + player['hack'] * 20
        + player['credits'] * 10
        + player['hacks_success'] * 200
        - player['hacks_failed'] * 50
        + player['rooms_visited'] * 100
        - player['alarm'] * 20
        + rom_bonus
    )
    time_bonus = max(0, (3600 - duration) // 60)
    hack_time_bonus = 0
    if player['hacks_success'] > 0:
        avg_hack_time = player['total_hack_time'] / player['hacks_success']
        hack_time_bonus = max(0, (hack_time - avg_hack_time) * 20)

    score = int((base_score + time_bonus + hack_time_bonus) * difficulty_multiplier)
    line = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {player_name} | "
        f"score:{score} | rooms:{player['rooms_visited']} | {duration}s | status:{status}\n"
    )
    with open(leaderboard_path, "a") as f:
        f.write(line)

    entries = []
    with open(leaderboard_path, "r") as f:
        for l in f:
            parts = [p.strip() for p in l.split("|")]
            sc = 0
            for p in parts:
                if p.startswith("score:"):
                    try:
                        sc = int(p.split(":")[1])
                    except ValueError:
                        sc = 0
            entries.append((sc, l.strip()))

    entries.sort(key=lambda x: x[0], reverse=True)
    rank = next((i + 1 for i, e in enumerate(entries) if e[1] == line.strip()), None)

    summary_lines = [
        "\n" + tr("score.title"),
        tr("score.base", score=base_score),
        tr("score.rom_bonus", bonus=rom_bonus),
        tr("score.time_bonus", bonus=time_bonus),
        tr("score.hack_bonus", bonus=hack_time_bonus),
        line.rstrip("\n"),
    ]
    if rank:
        summary_lines.append(tr("score.rank", rank=rank))

    if print_summary:
        for summary_line in summary_lines:
            print(summary_line)

    update_profile_callback(status=status, duration=duration, end_reason=end_reason, score=score)
    try:
        sync_stats_exports()
    except OSError:
        pass
    return {
        "score": score,
        "rank": rank,
        "duration": duration,
        "summary_lines": summary_lines,
    }
