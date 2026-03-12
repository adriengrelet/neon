#!/usr/bin/env python3
from termfx import color as color_text, color_choice_line

SHOP_ITEMS = {
    "1": {
        "id": "synaptique",
        "kind": "upgrade",
        "cost": 100,
        "line_key": "shop.item.1",
        "buy_key": "shop.buy.1",
        "flag": "synaptique_bought",
    },
    "2": {
        "id": "surcharge",
        "kind": "upgrade",
        "cost": 100,
        "line_key": "shop.item.2",
        "buy_key": "shop.buy.2",
        "flag": "surcharge_bought",
    },
    "3": {
        "id": "interface",
        "kind": "upgrade",
        "cost": 150,
        "line_key": "shop.item.3",
        "buy_key": "shop.buy.3",
        "flag": "interface_bought",
    },
    "4": {
        "id": "combat_chip",
        "kind": "upgrade",
        "cost": 150,
        "line_key": "shop.item.4",
        "buy_key": "shop.buy.4",
        "flag": "combat_chip_bought",
    },
    "5": {
        "id": "force",
        "kind": "upgrade",
        "cost": 100,
        "line_key": "shop.item.5",
        "buy_key": "shop.buy.5",
        "flag": "force_bought",
    },
    "6": {
        "id": "vitesse",
        "kind": "upgrade",
        "cost": 100,
        "line_key": "shop.item.6",
        "buy_key": "shop.buy.6",
        "flag": "vitesse_bought",
    },
    "7": {
        "id": "energy_dissipator",
        "kind": "upgrade",
        "cost": 300,
        "line_key": "shop.item.7",
        "buy_key": "shop.buy.7",
        "flag": "energy_dissipator_bought",
    },
    "8": {
        "id": "medkit",
        "kind": "consumable",
        "cost": 300,
        "line_key": "shop.item.8",
        "buy_key": "shop.buy.8",
        "inventory_id": "medkit",
    },
    "9": {
        "id": "energy_cell",
        "kind": "consumable",
        "cost": 300,
        "line_key": "shop.item.9",
        "buy_key": "shop.buy.9",
        "inventory_id": "energy_cell",
    },
    "10": {
        "id": "energy_drink",
        "kind": "consumable",
        "cost": 75,
        "line_key": "shop.item.10",
        "buy_key": "shop.buy.10",
        "inventory_id": "energy_drink",
    },
    "11": {
        "id": "hemo_patch",
        "kind": "consumable",
        "cost": 50,
        "line_key": "shop.item.11",
        "buy_key": "shop.buy.11",
        "inventory_id": "hemo_patch",
    },
    "12": {
        "id": "neuro_booster",
        "kind": "consumable",
        "cost": 90,
        "line_key": "shop.item.12",
        "buy_key": "shop.buy.12",
        "inventory_id": "neuro_booster",
    },
    "13": {
        "id": "regen_capsule",
        "kind": "consumable",
        "cost": 120,
        "line_key": "shop.item.13",
        "buy_key": "shop.buy.13",
        "inventory_id": "regen_capsule",
    },
    "14": {
        "id": "laser_pistol",
        "kind": "consumable",
        "cost": 1000,
        "line_key": "shop.item.14",
        "buy_key": "shop.buy.14",
        "inventory_id": "laser_pistol",
        "unique": True,
    },
}


def _build_sell_value_map():
    sell_values = {}
    for item in SHOP_ITEMS.values():
        if item.get("kind") != "consumable":
            continue
        inventory_id = item.get("inventory_id")
        cost = int(item.get("cost", 0))
        if inventory_id and cost > 0:
            sell_values[inventory_id] = max(1, cost // 2)
    return sell_values


SELL_VALUES = _build_sell_value_map()


def _apply_upgrade_effect(player, item_id):
    if item_id == "synaptique":
        player["hack_time_bonus"] += 10
    elif item_id == "interface":
        player["matrix_reduction"] += 1
    elif item_id == "combat_chip":
        player["combat_time_bonus"] = 2


def _apply_upgrade_purchase(player, item):
    flag = item["flag"]
    if player.get(flag):
        return False
    player[flag] = True
    _apply_upgrade_effect(player, item["id"])
    return True


def apply_upgrade_ids_to_player(player, upgrade_ids):
    if not isinstance(upgrade_ids, list):
        return

    for item in SHOP_ITEMS.values():
        if item["kind"] != "upgrade":
            continue
        if item["id"] in upgrade_ids:
            _apply_upgrade_purchase(player, item)


def _sorted_shop_keys():
    return sorted(SHOP_ITEMS.keys(), key=int)


def _run_shared_shop(
    *,
    tr,
    title_key,
    credits_key,
    quit_key,
    prompt_key,
    invalid_key,
    insufficient_key,
    get_credits,
    set_credits,
    is_upgrade_owned,
    on_upgrade_purchase,
    on_consumable_purchase,
    render_extra_header=None,
):
    while True:
        credits = int(get_credits())
        print("\n" + color_text(tr(title_key), "blue"))
        print(color_text(tr(credits_key, credits=credits), "blue"))
        if render_extra_header is not None:
            render_extra_header()

        for key in _sorted_shop_keys():
            item = SHOP_ITEMS[key]
            if item["kind"] == "upgrade" and is_upgrade_owned(item):
                continue
            print(color_choice_line(tr(item["line_key"])))
        print(color_choice_line(tr(quit_key)))

        choice = input(color_text(tr(prompt_key), "blue")).strip()
        if choice == "0":
            break

        item = SHOP_ITEMS.get(choice)
        if item is None:
            print(color_text(tr(invalid_key), "blue"))
            continue

        if item["kind"] == "upgrade" and is_upgrade_owned(item):
            print(color_text(tr(invalid_key), "blue"))
            continue

        if credits < item["cost"]:
            print(color_text(tr(insufficient_key), "blue"))
            continue

        set_credits(credits - item["cost"])
        if item["kind"] == "upgrade":
            bought = on_upgrade_purchase(item)
        else:
            bought = on_consumable_purchase(item)

        if not bought:
            set_credits(credits)
            print(color_text(tr(invalid_key), "blue"))
            continue

        print(color_text(tr(item["buy_key"]), "blue"))


def _count_items(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def _remove_item_occurrences(items, target_item, count):
    removed = 0
    while removed < count:
        try:
            items.remove(target_item)
        except ValueError:
            break
        removed += 1
    return removed


def run_pre_run_inventory_manager(profile, path, tr, save_profile, format_inventory_counts):
    if not profile:
        return

    while True:
        bank_inventory = profile.get("bank_inventory", [])
        if not isinstance(bank_inventory, list):
            bank_inventory = []
            profile["bank_inventory"] = bank_inventory

        counts = _count_items(bank_inventory)
        ordered_items = sorted(counts.keys())

        print("\n" + color_text(tr("prerun.inventory.title"), "blue"))
        print(color_text(tr("prerun.inventory.credits", credits=int(profile.get("bank_credits", 0))), "blue"))
        print(color_text(tr("prerun.inventory.items", value=format_inventory_counts(bank_inventory)), "blue"))

        if ordered_items:
            for idx, item_id in enumerate(ordered_items, start=1):
                sell_value = SELL_VALUES.get(item_id, 0)
                sell_value_text = str(sell_value) if sell_value > 0 else "N/A"
                print(
                    color_choice_line(
                        tr(
                            "prerun.inventory.entry",
                            idx=idx,
                            item=item_id,
                            count=counts[item_id],
                            sell=sell_value_text,
                        )
                    )
                )
        else:
            print(color_text(tr("prerun.inventory.empty"), "blue"))

        print(color_choice_line(tr("prerun.inventory.sell")))
        print(color_choice_line(tr("prerun.inventory.discard")))
        print(color_choice_line(tr("prerun.inventory.back")))

        choice = input(color_text(tr("prerun.inventory.prompt"), "blue")).strip().lower()
        if choice == "0":
            return
        action = None
        if choice in {"s", "sell"}:
            action = "sell"
        elif choice in {"d", "drop"}:
            action = "drop"

        if action is None:
            print(color_text(tr("prerun.inventory.invalid"), "blue"))
            continue
        if not ordered_items:
            print(color_text(tr("prerun.inventory.empty"), "blue"))
            continue

        selected_raw = input(
            color_text(tr("prerun.inventory.select_prompt", max=len(ordered_items)), "blue")
        ).strip()
        if not selected_raw.isdigit():
            print(color_text(tr("prerun.inventory.invalid"), "blue"))
            continue

        selected_index = int(selected_raw)
        if selected_index < 1 or selected_index > len(ordered_items):
            print(color_text(tr("prerun.inventory.invalid"), "blue"))
            continue

        selected_item = ordered_items[selected_index - 1]
        max_qty = counts[selected_item]
        qty_raw = input(color_text(tr("prerun.inventory.qty_prompt", max=max_qty), "blue")).strip()

        if qty_raw == "":
            quantity = 1
        elif qty_raw.isdigit():
            quantity = max(1, min(int(qty_raw), max_qty))
        else:
            print(color_text(tr("prerun.inventory.invalid"), "blue"))
            continue

        if action == "sell":
            sell_value = SELL_VALUES.get(selected_item, 0)
            if sell_value <= 0:
                print(color_text(tr("prerun.inventory.unsellable", item=selected_item), "blue"))
                continue

            removed_count = _remove_item_occurrences(bank_inventory, selected_item, quantity)
            if removed_count <= 0:
                print(color_text(tr("prerun.inventory.invalid"), "blue"))
                continue

            earned = sell_value * removed_count
            profile["bank_credits"] = int(profile.get("bank_credits", 0)) + earned
            save_profile(profile, path)
            print(color_text(tr("prerun.inventory.sold", item=selected_item, count=removed_count, credits=earned), "blue"))
            continue

        removed_count = _remove_item_occurrences(bank_inventory, selected_item, quantity)
        if removed_count <= 0:
            print(color_text(tr("prerun.inventory.invalid"), "blue"))
            continue

        save_profile(profile, path)
        print(color_text(tr("prerun.inventory.discarded", item=selected_item, count=removed_count), "blue"))


def run_pre_run_shop(profile, path, tr, save_profile, format_inventory_counts, ask_confirmation=True):
    if not profile:
        return []

    if ask_confirmation:
        bank_credits = int(profile.get("bank_credits", 0))
        visit = input(color_text(tr("prerun.shop.offer_prompt", credits=bank_credits), "blue")).strip().lower()
        if visit != "y":
            return []

    pending_run_upgrades = []

    def get_credits():
        return int(profile.get("bank_credits", 0))

    def set_credits(value):
        profile["bank_credits"] = int(value)

    def is_upgrade_owned(item):
        return item["id"] in pending_run_upgrades

    def on_upgrade_purchase(item):
        if item["id"] in pending_run_upgrades:
            return False
        pending_run_upgrades.append(item["id"])
        save_profile(profile, path)
        return True

    def on_consumable_purchase(item):
        bank_inventory = profile.get("bank_inventory", [])
        if not isinstance(bank_inventory, list):
            bank_inventory = []
        if item.get("unique") and item["inventory_id"] in bank_inventory:
            return False
        bank_inventory.append(item["inventory_id"])
        profile["bank_inventory"] = bank_inventory
        save_profile(profile, path)
        return True

    def render_extra_header():
        print(tr("prerun.shop.bank_inventory", value=format_inventory_counts(profile.get("bank_inventory", []))))

    _run_shared_shop(
        tr=tr,
        title_key="prerun.shop.title",
        credits_key="prerun.shop.credits",
        quit_key="prerun.shop.quit",
        prompt_key="prerun.shop.choice_prompt",
        invalid_key="prerun.shop.invalid",
        insufficient_key="prerun.shop.insufficient",
        get_credits=get_credits,
        set_credits=set_credits,
        is_upgrade_owned=is_upgrade_owned,
        on_upgrade_purchase=on_upgrade_purchase,
        on_consumable_purchase=on_consumable_purchase,
        render_extra_header=render_extra_header,
    )
    return list(pending_run_upgrades)


def run_in_game_shop(
    player,
    tr,
    normalize_credits,
    sync_inventory_callback=None,
):
    normalize_credits()

    def get_credits():
        return int(player.get("credits", 0))

    def set_credits(value):
        player["credits"] = int(value)

    def is_upgrade_owned(item):
        return bool(player.get(item["flag"]))

    def on_upgrade_purchase(item):
        return _apply_upgrade_purchase(player, item)

    def on_consumable_purchase(item):
        if item.get("unique") and item["inventory_id"] in player["inventory"]:
            return False
        player["inventory"].append(item["inventory_id"])
        if sync_inventory_callback is not None:
            sync_inventory_callback()
        return True

    _run_shared_shop(
        tr=tr,
        title_key="shop.title",
        credits_key="shop.credits",
        quit_key="shop.item.0",
        prompt_key="shop.prompt",
        invalid_key="shop.invalid",
        insufficient_key="shop.insufficient",
        get_credits=get_credits,
        set_credits=set_credits,
        is_upgrade_owned=is_upgrade_owned,
        on_upgrade_purchase=on_upgrade_purchase,
        on_consumable_purchase=on_consumable_purchase,
    )
