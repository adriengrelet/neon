#!/usr/bin/env python3

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
        "cost": 100,
        "line_key": "shop.item.8",
        "buy_key": "shop.buy.8",
        "inventory_id": "medkit",
    },
    "9": {
        "id": "energy_cell",
        "kind": "consumable",
        "cost": 100,
        "line_key": "shop.item.9",
        "buy_key": "shop.buy.9",
        "inventory_id": "energy_cell",
    },
}


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
        print("\n" + tr(title_key))
        print(tr(credits_key, credits=credits))
        if render_extra_header is not None:
            render_extra_header()

        for key in _sorted_shop_keys():
            item = SHOP_ITEMS[key]
            if item["kind"] == "upgrade" and is_upgrade_owned(item):
                continue
            print(tr(item["line_key"]))
        print(tr(quit_key))

        choice = input(tr(prompt_key)).strip()
        if choice == "0":
            break

        item = SHOP_ITEMS.get(choice)
        if item is None:
            print(tr(invalid_key))
            continue

        if item["kind"] == "upgrade" and is_upgrade_owned(item):
            print(tr(invalid_key))
            continue

        if credits < item["cost"]:
            print(tr(insufficient_key))
            continue

        set_credits(credits - item["cost"])
        if item["kind"] == "upgrade":
            bought = on_upgrade_purchase(item)
        else:
            bought = on_consumable_purchase(item)

        if not bought:
            set_credits(credits)
            print(tr(invalid_key))
            continue

        print(tr(item["buy_key"]))


def run_pre_run_shop(profile, path, tr, save_profile, format_inventory_counts):
    if not profile:
        return []

    bank_credits = int(profile.get("bank_credits", 0))
    visit = input(tr("prerun.shop.offer_prompt", credits=bank_credits)).strip().lower()
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
    profile=None,
    profile_path=None,
    save_profile=None,
):
    normalize_credits()

    use_bank_wallet = bool(profile) and bool(profile_path) and (save_profile is not None)

    def get_credits():
        if use_bank_wallet:
            return int(profile.get("bank_credits", 0))
        return int(player.get("credits", 0))

    def set_credits(value):
        if use_bank_wallet:
            profile["bank_credits"] = int(value)
            save_profile(profile, profile_path)
            return
        player["credits"] = int(value)

    def is_upgrade_owned(item):
        return bool(player.get(item["flag"]))

    def on_upgrade_purchase(item):
        return _apply_upgrade_purchase(player, item)

    def on_consumable_purchase(item):
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
