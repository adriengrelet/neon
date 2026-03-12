import random
import string
import time


def run_attack(*, player, combat_time, reflex_time, tr, get_current_room, normalize_primary_stats):
    normalize_primary_stats()
    room = get_current_room()
    if not room.enemy:
        print(tr("attack.no_target"))
        return

    stance = random.choice(["aggressive", "defensive", "unstable"])
    if stance == "aggressive":
        print(tr("attack.stance.aggressive"))
    elif stance == "defensive":
        print(tr("attack.stance.defensive"))
    else:
        print(tr("attack.stance.unstable"))

    effective_time = combat_time * player["combat_time_bonus"]
    print("\n" + tr("attack.prompt", time=effective_time))
    start = time.time()
    choice = input(tr("attack.choice_prompt")).strip().upper()
    elapsed = time.time() - start
    if elapsed > effective_time:
        print(tr("attack.timeout"))
        choice = random.choice(["A", "B", "C"])

    outcome = "neutral"
    if (choice == "A" and stance == "unstable") or (choice == "B" and stance == "aggressive") or (choice == "C" and stance == "defensive"):
        outcome = "good"
    elif (choice == "A" and stance == "defensive") or (choice == "B" and stance == "unstable") or (choice == "C" and stance == "aggressive"):
        outcome = "bad"

    if random.random() < 0.30:
        reflex_char = random.choice(string.ascii_letters + string.digits)
        print(tr("attack.reflex_prompt", char=reflex_char))
        start = time.time()
        reflex = input(tr("ui.reflex_input_prompt")).strip()
        reaction_time = time.time() - start
        reaction_ms = int(reaction_time * 1000)
        if reflex == reflex_char and reaction_time < reflex_time:
            print(tr("attack.reflex.success", ms=reaction_ms))
            taken = max(0, int(reaction_time * 5))
        else:
            print(tr("attack.reflex.failure", ms=reaction_ms))
            taken = random.randint(10, 20)
    else:
        if outcome == "good":
            taken = random.randint(0, 5)
        elif outcome == "bad":
            taken = random.randint(10, 20)
        else:
            taken = random.randint(5, 10)

    if player["surcharge_bought"] and choice == "C":
        taken = max(0, taken - 3)
        print(tr("attack.bonus.surcharge"))
    if player["force_bought"] and choice == "A":
        taken = max(0, taken - 3)
        print(tr("attack.bonus.force"))
    if player["vitesse_bought"] and choice == "B":
        taken = max(0, taken - 3)
        print(tr("attack.bonus.vitesse"))

    if room.enemy == "CORE Sentinel":
        damage_to_core = random.randint(15, 35)
        if "laser_pistol" in player.get("inventory", []):
            damage_to_core += 10
            print(tr("attack.bonus.laser_pistol"))
        room.enemy_hp -= damage_to_core
        print(tr("attack.core.hit", damage=damage_to_core))
        if room.enemy_hp > 0:
            print(tr("attack.core.hp", hp=room.enemy_hp))
            core_damage = random.randint(10, 20)
            player["hp"] -= core_damage
            print(tr("attack.core.counter", damage=core_damage))
        else:
            print(tr("attack.core.neutralized"))
            room.enemy = None
            if not player["core_hacked"]:
                print(tr("attack.core.remaining_hack"))
    else:
        print(tr("attack.neutralize", enemy=room.enemy))
        room.enemy = None
        player["hp"] -= taken
        print(tr("attack.taken", damage=taken))

    normalize_primary_stats()


def run_enemy_attack(*, player, tr, get_current_room, normalize_primary_stats):
    normalize_primary_stats()
    room = get_current_room()
    if not room.enemy:
        return

    damage = random.randint(10, 20)
    player["hp"] -= damage
    if room.enemy == "CORE Sentinel":
        print(tr("enemy_attack.core", damage=damage))
    else:
        print(tr("enemy_attack.normal", enemy=room.enemy, damage=damage))

    normalize_primary_stats()


def run_enemy_turn(*, player, alarm_threshold, reinforcement_chance, tr, tr_value, get_current_room):
    room = get_current_room()
    if player["alarm"] >= alarm_threshold and random.random() < reinforcement_chance and not room.enemy:
        room.enemy = random.choice(tr_value("content.enemies"))
        print(tr("enemy_turn.reinforcement"))
