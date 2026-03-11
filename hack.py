#!/usr/bin/env python3
import random
import time


def reveal_unknown_fragment_markers(world, width, height, player, get_echo_marker):
    marked = 0
    for y in range(height):
        for x in range(width):
            room = world[y][x]
            if room.visited or not room.rom_fragment:
                continue
            if room.rom_fragment["id"] in player["rom_fragments"]:
                continue
            marker = get_echo_marker(room)
            if marker:
                room.echo_marker = marker
                marked += 1
    return marked


def hack_grid_size(player):
    h = player["hack"]
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
    return max(3, size - player["matrix_reduction"])


def mini_hack_success(player, hex_values, tr, hack_time, core_bonus=False):
    size = hack_grid_size(player) + (1 if core_bonus else 0)
    rows = [chr(ord("A") + i) for i in range(size)]
    cols = [str(i + 1) for i in range(size)]
    grid = [[random.choice(hex_values) for _ in range(size)] for _ in range(size)]
    a = (random.randint(0, size - 1), random.randint(0, size - 1))

    while True:
        b = (random.randint(0, size - 1), a[1])
        if b != a:
            break

    while True:
        c = (b[0], random.randint(0, size - 1))
        if c != b:
            break

    forced = random.sample(hex_values, 3)
    grid[a[0]][a[1]] = forced[0]
    grid[b[0]][b[1]] = forced[1]
    grid[c[0]][c[1]] = forced[2]
    target = [grid[a[0]][a[1]], grid[b[0]][b[1]], grid[c[0]][c[1]]]

    print("\n" + tr("hack.matrix.title"))
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

    for step in range(3):
        choice = input(tr("hack.matrix.step_prompt", step=step + 1)).strip().upper()
        if time.time() - start > hack_time + player["hack_time_bonus"]:
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


def get_core_hint(player, core_x, core_y, tr):
    dx = core_x - player["x"]
    dy = core_y - player["y"]
    if abs(dx) > abs(dy):
        if dx > 0:
            return tr("core_hint.east")
        return tr("core_hint.west")
    if dy > 0:
        return tr("core_hint.south")
    return tr("core_hint.north")


def run_hack(
    player,
    world,
    width,
    height,
    core_x,
    core_y,
    hex_values,
    hack_time,
    difficulty_multiplier,
    tr,
    tr_value,
    get_current_room,
    get_echo_marker,
    draw_map,
    effective_energy_cost,
    normalize_primary_stats,
    normalize_credits,
    round_int,
):
    room = get_current_room()
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
    player["energy"] = max(0, player["energy"] - cost)

    result = mini_hack_success(player, hex_values, tr, hack_time, core_bonus=room.core)
    if not result[0]:
        print(tr("hack.cost", cost=cost))
        old_alarm = player["alarm"]
        player["alarm"] += max(1, int(player.get("alarm_step", 1)))
        if player["alarm"] > old_alarm:
            print(tr("hack.alarm_triggered", alarm=player["alarm"]))
        if player["alarm"] == 3:
            room = get_current_room()
            if not room.enemy:
                room.enemy = random.choice(tr_value("content.enemies"))
                print(tr("hack.alarm_enemy"))
        player["hack"] = max(10, player["hack"] - 10)
        player["hacks_failed"] += 1
        normalize_primary_stats()
        print(tr("hack.reduced", hack=player["hack"]))
        return

    print(tr("hack.cost", cost=cost))
    player["hacks_success"] += 1
    player["total_hack_time"] += result[1]
    is_standard_hack = room.terminal and not room.core
    base_credits = random.randint(50, 100)
    speed_bonus = max(0, 125 - (result[1] / 1000) * 5)
    credit_gain = round_int(base_credits + int(speed_bonus) / difficulty_multiplier)

    if is_standard_hack:
        print(tr("hack.standard_success"))
        print(tr("hack.loot.a"))
        print(tr("hack.loot.b"))
        print(tr("hack.loot.c"))
        print(tr("hack.loot.d"))
        loot_choice = input(tr("hack.loot.prompt")).strip().upper()

        if loot_choice == "B":
            player["hp"] += 25
            print(tr("hack.loot.heal"))
        elif loot_choice == "C":
            player["hack"] += 5
            print(tr("hack.loot.upgrade"))
        elif loot_choice == "D":
            player["energy"] += 10
            print(tr("hack.loot.cyber_heal"))
        else:
            player["credits"] += credit_gain
            print(tr("hack.loot.credits", credits=credit_gain))

        if random.random() < 0.25:
            revealed = reveal_unknown_fragment_markers(world, width, height, player, get_echo_marker)
            if revealed > 0:
                print(tr("hack.fragment_ping", count=revealed))
                draw_map(show_legend=True)
            else:
                print(tr("hack.fragment_ping_none"))
    else:
        player["credits"] += credit_gain
        print(tr("hack.success.credits", credits=credit_gain))

    player["alarm"] = max(0, player["alarm"] - 1)
    print(tr("hack.alarm_reduced"))
    if room.locked:
        room.locked = False
        print(tr("hack.unlock_room"))
    if room.terminal:
        room.terminal = False
        if room.core:
            player["core_hacked"] = True
            print(tr("hack.core_pirated"))
        else:
            print(get_core_hint(player, core_x, core_y, tr))

    normalize_primary_stats()
    normalize_credits()
    print(tr("hack.done_ms", ms=result[1]))
