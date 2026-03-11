#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime


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
        "visited_structures": [],
        "next_structure_id": None,
        "active_structure_id": None,
    }


def save_player_profile(profile, path):
    profile["last_seen"] = datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


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
        if not isinstance(profile.get("visited_structures"), list):
            profile["visited_structures"] = []
        next_structure_id = profile.get("next_structure_id")
        profile["next_structure_id"] = next_structure_id if isinstance(next_structure_id, str) and next_structure_id else None
        active_structure_id = profile.get("active_structure_id")
        profile["active_structure_id"] = active_structure_id if isinstance(active_structure_id, str) and active_structure_id else None
        if "created_at" not in profile or not profile["created_at"]:
            profile["created_at"] = defaults["created_at"]
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
        tr("profile.bank_inventory", value=format_inventory_counts(profile.get("bank_inventory", []))),
    ]
