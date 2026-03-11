#!/usr/bin/env python3
import random


def current_room(world, player):
    return world[player['y']][player['x']]


def draw_map(world, player, width, height, tr, show_legend=True):
    print("\n" + tr("map.title"))
    for y in range(height):
        line = ""
        for x in range(width):
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


def describe(world, player, tr):
    room = current_room(world, player)
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


def move(world, player, width, height, dx, dy, tr, on_enemy_turn):
    room = current_room(world, player)
    if room.locked:
        print(tr("move.locked_exit"))
        return
    nx = player['x'] + dx
    ny = player['y'] + dy
    if 0 <= nx < width and 0 <= ny < height:
        player['x'] = nx
        player['y'] = ny
        on_enemy_turn()
        describe(world, player, tr)
    else:
        print(tr("move.wall"))


def scan(world, player, tr, tr_value, world_rules, effective_energy_cost, on_enemy_turn):
    room = current_room(world, player)
    print(tr("scan.title"))
    scan_cost = effective_energy_cost(random.randint(1, 10))
    player['energy'] = max(0, player['energy'] - scan_cost)
    print(tr("scan.cost", cost=scan_cost))
    found = False
    if random.random() < world_rules.get('scan_item_discovery_chance', 0.35) and not room.item:
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
    on_enemy_turn()


def echo_scan(world, player, width, height, tr, effective_energy_cost):
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
            if 0 <= nx < width and 0 <= ny < height:
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
