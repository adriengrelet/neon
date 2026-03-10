#!/usr/bin/env python3
import random
import os
import sys
import time
import string
from datetime import datetime

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

INTRO = """
==============================
        NEON NODE v6
==============================

Infiltre la mégastructure.
Atteins le CORE central, pirate-le, et ressors vivant.

Pour les hacks :
- Plus ton hack est élevé, plus la matrice est petite.
- Étape 1 : libre de trouver la bonne valeur hexa dans la matrice (qui doit correspondre à la première valeur du code demandé).
- Étape 2 : doit être dans la même colonne que l'étape 1.
- Étape 3 : doit être dans la même ligne que l'étape 2.

Le temps est limité pour réussir le hack, et échouer augmente ton alarme et réduit ton hack.

Des crédits sont gagnés en piratant des terminaux, et peuvent être utilisés pour acheter des améliorations dans le shop.
Plus tu hackes vite, plus tu gagnes de crédits !

Commandes :
 north / n : se déplacer vers le nord
 south / s : se déplacer vers le sud
 east / e : se déplacer vers l'est
 west / w  : se déplacer vers l'ouest
 scan / sc : scanner la salle pour trouver des objets cachés ou des indices
 echo / ec : sonder les salles autour de toi et révéler des marqueurs tactiques sur la carte
 hack / h : tenter de pirater un terminal ou de désactiver un verrouillage
 attack : engager le combat contre un ennemi présent
 take / t : ramasser un objet visible dans la salle ou découvert en scan
 use <objet> / u <objet> : utiliser un objet de l'inventaire (ex: use medkit)
 map / m : afficher la carte du niveau (P = position, C = core, . = salle visitée, # = salle non visitée)
 inventory / inv : afficher l'inventaire
 status / stat : afficher le statut et les améliorations
 fragments / fra : afficher les fragments ROM collectés et le dossier narratif
 shop / sh : accéder au magasin pour acheter des améliorations avec les crédits
 help / he : afficher les commandes
 quit / q : quitter le jeu
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

# Translation scaffold: start with startup/UI strings and extend progressively.
TRANSLATIONS = {
    "fr": {
        "language.title": "=== CHOIX DE LANGUE ===",
        "language.subtitle": "Codes disponibles :",
        "language.option": "- {code} : {name}",
        "language.prompt": "Langue (fr/en/it/es) > ",
        "language.selected": "Langue active : {code} ({name})",
        "language.invalid": "Code invalide. Utilise fr, en, it, es.",
        "statusline.compact": "HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3",
        "leaderboard.title": "=== LEADERBOARD ===",
        "leaderboard.entry": "#{idx} {line}",
        "leaderboard.none": "Aucun score enregistré.",
        "intro.press_enter": "Appuie sur Entree pour commencer...",
        "startup.launching": "Lancement du jeu...",
        "startup.player_name_prompt": "Nom du joueur : ",
        "startup.player_name_echo": "Joueur: {name}",
        "startup.difficulty_title": "=== SELECTION DIFFICULTE ===",
        "startup.difficulty_1": "1. Balade cyber   - Hack : 60s  Combat : 10s  Reflexe : 6s  Multiplicateur de points : 1x",
        "startup.difficulty_2": "2. Epreuve cyber  - Hack : 45s  Combat : 6s   Reflexe : 4s  Multiplicateur de points : 2x",
        "startup.difficulty_3": "3. Transpiration cyber - Hack : 30s  Combat : 4s   Reflexe : 2s  Multiplicateur de points : 3x",
        "startup.difficulty_4": "4. Violence cyber - Hack : 20s  Combat : 3s   Reflexe : 3s  Multiplicateur de points : 4x",
        "startup.difficulty_prompt": "Choisir le niveau (1-4) : ",
        "startup.difficulty_invalid": "Niveau invalide, difficulte 3 selectionnee par defaut.",
        "map.title": "=== MAP ===",
        "map.legend": "Légende: P=Player | C=Core | .=Salle visitée | E=Ennemi | L=Loot | F=Fragment | M=Multi | #=Inconnue",
        "describe.enemy_present": "⚠ Ennemi présent : {enemy}",
        "describe.core_hp": "HP du CORE Sentinel : {hp}",
        "describe.locked": "🔒 Salle verrouillée.",
        "describe.terminal": "💻 Terminal détecté.",
        "describe.item_visible": "📦 Objet visible : {item}",
        "describe.fragment_visible": "🧩 Fragment ROM detecte : {fragment_id}",
        "describe.core_detected": "===== ☢ CORE CENTRAL détecté ! =====",
        "move.locked_exit": "🔒 Impossible de sortir : verrouillage actif.",
        "move.wall": "Mur structurel.",
        "scan.title": "=== SCAN PROFOND ===",
        "scan.cost": "Coût énergétique du scan : {cost}",
        "scan.object_found": "Objet caché détecté : {item}",
        "scan.lock_pulse": "Le verrouillage pulse à fréquence variable.",
        "scan.ports_open": "Ports d'intrusion encore ouverts.",
        "scan.rom_signature": "Signature ROM fragmentaire detectee dans la salle.",
        "scan.nothing": "Rien de nouveau détecté.",
        "echo.title": "=== ECHO ETENDU ===",
        "echo.cost": "Coût énergétique de l'echo : {cost}",
        "echo.detected": "Signatures détectées autour de toi : {count}",
        "echo.none": "Aucune signature tactique détectée autour de toi.",
        "story.title": "=== DOSSIER ROM DECHIFFRE ===",
        "story.id": "ID: {id}",
        "story.name": "Titre: {title}",
        "story.hacker": "Hacker: {hacker}",
        "story.context": "Contexte: {context}",
        "story.logs": "--- LOGS ---",
        "story.epilogue": "--- EPILOGUE ---",
        "fragments.title": "=== FRAGMENTS ROM ===",
        "fragments.count": "Collecte: {found}/{total}",
        "fragments.line": "[{mark}] {id} - {label}",
        "fragments.unlocked": "Acces au dossier narratif complet debloque.",
        "fragments.read_prompt": "Lire l'histoire maintenant ? (y/n) ",
        "fragments.incomplete": "Recupere les 3 fragments pour dechiffrer l'histoire complete.",
        "hack.matrix.title": "=== MATRICE D'INTRUSION ===",
        "hack.matrix.sequence": "Séquence cible : {sequence}",
        "hack.matrix.rules": "Étape 1 libre | Étape 2 même colonne | Étape 3 même ligne",
        "hack.matrix.step_prompt": "Étape {step} > ",
        "hack.matrix.timeout": "Temps dépassé",
        "hack.matrix.incorrect": "Code incorrect",
        "hack.matrix.same_column": "Même colonne requise",
        "hack.matrix.same_row": "Même ligne requise",
        "core_hint.east": "INDICE : Le core est à l'est.",
        "core_hint.west": "INDICE : Le core est à l'ouest.",
        "core_hint.south": "INDICE : Le core est au sud.",
        "core_hint.north": "INDICE : Le core est au nord.",
        "hack.blocked_core": "Le CORE est protégé. Neutralise d'abord l'ennemi présent.",
        "hack.nothing": "Rien à pirater ici.",
        "hack.title": "=== HACK ===",
        "hack.cost": "Coût énergétique : {cost}",
        "hack.alarm_triggered": "⚠ Attention Alarme niveau {alarm} enclenchée !",
        "hack.alarm_enemy": "🚨 Ennemi d'alarme déployé dans cette salle !",
        "hack.reduced": "Hack réduit à {hack}",
        "hack.standard_success": "💻 Hack standard réussi. Choix du loot :",
        "hack.fragment_ping": "🛰️ Intel terminal : signatures ROM repérées sur la carte ({count}).",
        "hack.fragment_ping_none": "Intel terminal : aucune signature ROM inconnue à révéler.",
        "hack.loot.a": "A. Crédits",
        "hack.loot.b": "B. Soin neurocyber (+25 HP)",
        "hack.loot.c": "C. Upgrade hack (+5 HK)",
        "hack.loot.prompt": "Loot > ",
        "hack.loot.heal": "🧠 Soin appliqué : +25 HP",
        "hack.loot.upgrade": "⚙ Upgrade hack appliqué : +5 HK",
        "hack.loot.credits": "💰 Loot crédits obtenu : +{credits}",
        "hack.success.credits": "💻 Hack réussi ! +{credits} crédits",
        "hack.alarm_reduced": "Alarme réduite de 1.",
        "hack.unlock_room": "🔓 Salle déverrouillée.",
        "hack.core_pirated": "☢ CORE piraté. Extraction possible.",
        "hack.done_ms": "Hack réalisé en {ms} ms",
        "attack.no_target": "Aucune cible.",
        "attack.stance.aggressive": "L'ennemi charge avec agressivité, prêt à frapper fort.",
        "attack.stance.defensive": "L'ennemi se retranche derrière des défenses solides.",
        "attack.stance.unstable": "L'ennemi bouge de manière erratique et imprévisible.",
        "attack.prompt": "Combat : A frontal | B feinte | C surcharge (choix en {time}s)",
        "attack.choice_prompt": "Choix > ",
        "attack.timeout": "Temps de réaction trop long : action de combat automatisée aléatoire.",
        "attack.reflex_prompt": "⚡ Réflexe : tape {char} vite",
        "attack.reflex.success": "Réussi en {ms} ms ! Bonus : dégâts réduits.",
        "attack.reflex.failure": "Échec en {ms} ms ! Malus : dégâts augmentés.",
        "attack.bonus.surcharge": "Augmentation surcharge activée : dégâts réduits !",
        "attack.bonus.force": "Augmentation force activée : dégâts réduits !",
        "attack.bonus.vitesse": "Augmentation vitesse activée : dégâts réduits !",
        "attack.core.hit": "Tu attaques le CORE Sentinel ! Dégâts : {damage}",
        "attack.core.hp": "HP du CORE Sentinel : {hp}",
        "attack.core.counter": "Le CORE Sentinel contre-attaque ! Tu encaisses {damage} dégâts.",
        "attack.core.neutralized": "CORE Sentinel neutralisé !",
        "attack.core.remaining_hack": "Le Sentinel est tombé, mais il reste à hacker le CORE.",
        "attack.neutralize": "Tu neutralises {enemy}",
        "attack.taken": "Tu encaisses {damage} dégâts",
        "enemy_attack.core": "⚠️ Le CORE Sentinel t'attaque ! Tu encaisses {damage} dégâts.",
        "enemy_attack.normal": "⚠️ {enemy} t'attaque ! Tu encaisses {damage} dégâts.",
        "take.fragment": "Fragment ROM recupere : {fragment_id} ({count}/3)",
        "take.item": "Pris : {item}",
        "take.none": "Rien à prendre.",
        "use.absent": "Objet absent.",
        "use.used": "{item} utilisé.",
        "inventory.title": "Inventaire :",
        "inventory.empty": "Vide",
        "inventory.medkit": "- medkit : restaure 25 HP",
        "inventory.energy_cell": "- energy_cell : restaure 25 énergie",
        "inventory.exploit_chip": "- exploit_chip : +10 hack",
        "status.title": "=== MATERIEL AUGMENTE ===",
        "status.synaptique": "- Augmentation synaptique : +10s au temps de hack",
        "status.surcharge": "- Augmentation surcharge : améliore surcharge en combat",
        "status.interface": "- Interface neuronale hacker augmentée : matrice réduite de 1",
        "status.combat_chip": "- Chip de combat : double le temps d'action en combat",
        "status.force": "- Augmentation force : améliore attaque frontale en combat",
        "status.vitesse": "- Augmentation vitesse : améliore feinte en combat",
        "status.dissipateur": "- Dissipateur énergétique : divise par 2 les coûts en énergie des actions",
        "status.none": "Aucun",
        "status.characteristics": "=== CARACTERISTIQUES ===",
        "status.line": "HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}",
        "status.fragments": "Fragments ROM: {count}/3",
        "help.commands": "Commandes : n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <objet> | inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q",
        "shop.title": "=== MAGASIN ===",
        "shop.credits": "Crédits disponibles : {credits}",
        "shop.items": "Items disponibles :",
        "shop.item.1": "1. Augmentation synaptique - 100 crédits : +10s au temps de hack",
        "shop.item.2": "2. Augmentation surcharge - 100 crédits : améliore surcharge en combat",
        "shop.item.3": "3. Interface neuronale hacker augmentée - 150 crédits : matrice réduite de 1",
        "shop.item.4": "4. Chip de combat - 150 crédits : double le temps pour agir en combat",
        "shop.item.5": "5. Augmentation force - 100 crédits : améliore attaque frontale en combat",
        "shop.item.6": "6. Augmentation vitesse - 100 crédits : améliore feinte en combat",
        "shop.item.7": "7. Dissipateur énergétique - 300 crédits : divise par 2 les coûts en EN des actions",
        "shop.item.0": "0. Quitter",
        "shop.prompt": "Choix > ",
        "shop.buy.1": "Augmentation synaptique achetée ! +10s au temps de hack.",
        "shop.buy.2": "Augmentation surcharge achetée ! Surcharge améliorée en combat.",
        "shop.buy.3": "Interface neuronale achetée ! Matrice réduite de 1.",
        "shop.buy.4": "Chip de combat acheté ! Temps de combat doublé.",
        "shop.buy.5": "Augmentation force achetée ! Attaque frontale améliorée.",
        "shop.buy.6": "Augmentation vitesse achetée ! Feinte améliorée.",
        "shop.buy.7": "Dissipateur énergétique acheté ! Les coûts EN des actions sont divisés par 2.",
        "shop.invalid": "Choix invalide ou insuffisant de crédits.",
        "enemy_turn.reinforcement": "⚠ Renfort système détecté",
        "score.title": "=== SCORE FINAL ===",
        "score.base": "Score de base: {score}",
        "score.rom_bonus": "Bonus fragments ROM: {bonus}",
        "score.time_bonus": "Bonus temps total: {bonus}",
        "score.hack_bonus": "Bonus temps hack: {bonus}",
        "score.rank": "Votre score vous classe #{rank}.",
        "core.pirated": "=== CORE PIRATÉ ===",
        "main.spawn": "spawn position {x},{y}",
        "main.core": "core position {x},{y}",
        "main.story_channel": "Canal ROM detecte: dossier {story_id} fragmente en 3 caches.",
        "main.death": "Tu tombes dans le réseau.",
        "main.alarm_game_over": "🚨 Alarme maximale atteinte ! Game over.",
        "ui.choice_prompt": "Choix > ",
        "ui.reflex_input_prompt": "> ",
        "ui.command_prompt": "\n> ",
        "ui.quit_confirm": "Voulez-vous quitter la partie en cours ? (y/n) ",
        "ui.replay_prompt": "Rejouer ? (y/n) ",
        "ui.unknown_command": "Commande inconnue.",
        "error.unhandled": "Une erreur est survenue : {error}",
    },
    "en": {
        "language.title": "=== LANGUAGE SELECTION ===",
        "language.subtitle": "Available codes:",
        "language.option": "- {code} : {name}",
        "language.prompt": "Language (fr/en/it/es) > ",
        "language.selected": "Active language: {code} ({name})",
        "language.invalid": "Invalid code. Use fr, en, it, es.",
        "statusline.compact": "HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3",
        "leaderboard.title": "=== LEADERBOARD ===",
        "leaderboard.entry": "#{idx} {line}",
        "leaderboard.none": "No score recorded.",
        "intro.press_enter": "Press Enter to start...",
        "startup.launching": "Launching game...",
        "startup.player_name_prompt": "Player name: ",
        "startup.player_name_echo": "Player: {name}",
        "startup.difficulty_title": "=== DIFFICULTY SELECTION ===",
        "startup.difficulty_1": "1. Cyber walk   - Hack: 60s  Combat: 10s  Reflex: 6s  Score multiplier: 1x",
        "startup.difficulty_2": "2. Cyber trial  - Hack: 45s  Combat: 6s   Reflex: 4s  Score multiplier: 2x",
        "startup.difficulty_3": "3. Cyber sweat  - Hack: 30s  Combat: 4s   Reflex: 2s  Score multiplier: 3x",
        "startup.difficulty_4": "4. Cyber violence - Hack: 20s  Combat: 3s   Reflex: 3s  Score multiplier: 4x",
        "startup.difficulty_prompt": "Choose level (1-4): ",
        "startup.difficulty_invalid": "Invalid level, difficulty 3 selected by default.",
        "map.title": "=== MAP ===",
        "map.legend": "Legend: P=Player | C=Core | .=Visited room | E=Enemy | L=Loot | F=Fragment | M=Multi | #=Unknown",
        "describe.enemy_present": "⚠ Enemy present: {enemy}",
        "describe.core_hp": "CORE Sentinel HP: {hp}",
        "describe.locked": "🔒 Room locked.",
        "describe.terminal": "💻 Terminal detected.",
        "describe.item_visible": "📦 Visible item: {item}",
        "describe.fragment_visible": "🧩 ROM fragment detected: {fragment_id}",
        "describe.core_detected": "===== ☢ CENTRAL CORE detected! =====",
        "move.locked_exit": "🔒 Cannot leave: lockdown active.",
        "move.wall": "Structural wall.",
        "scan.title": "=== DEEP SCAN ===",
        "scan.cost": "Scan energy cost: {cost}",
        "scan.object_found": "Hidden item detected: {item}",
        "scan.lock_pulse": "Lock pulses at variable frequency.",
        "scan.ports_open": "Intrusion ports are still open.",
        "scan.rom_signature": "Fragmented ROM signature detected in this room.",
        "scan.nothing": "Nothing new detected.",
        "echo.title": "=== EXTENDED ECHO ===",
        "echo.cost": "Echo energy cost: {cost}",
        "echo.detected": "Tactical signatures detected around you: {count}",
        "echo.none": "No tactical signature detected around you.",
        "story.title": "=== DECRYPTED ROM FILE ===",
        "story.id": "ID: {id}",
        "story.name": "Title: {title}",
        "story.hacker": "Hacker: {hacker}",
        "story.context": "Context: {context}",
        "story.logs": "--- LOGS ---",
        "story.epilogue": "--- EPILOGUE ---",
        "fragments.title": "=== ROM FRAGMENTS ===",
        "fragments.count": "Collection: {found}/{total}",
        "fragments.line": "[{mark}] {id} - {label}",
        "fragments.unlocked": "Access to the complete narrative file unlocked.",
        "fragments.read_prompt": "Read the story now? (y/n) ",
        "fragments.incomplete": "Collect all 3 fragments to decrypt the full story.",
        "hack.matrix.title": "=== INTRUSION MATRIX ===",
        "hack.matrix.sequence": "Target sequence: {sequence}",
        "hack.matrix.rules": "Step 1 free | Step 2 same column | Step 3 same row",
        "hack.matrix.step_prompt": "Step {step} > ",
        "hack.matrix.timeout": "Time exceeded",
        "hack.matrix.incorrect": "Incorrect code",
        "hack.matrix.same_column": "Same column required",
        "hack.matrix.same_row": "Same row required",
        "core_hint.east": "HINT: The core is to the east.",
        "core_hint.west": "HINT: The core is to the west.",
        "core_hint.south": "HINT: The core is to the south.",
        "core_hint.north": "HINT: The core is to the north.",
        "hack.blocked_core": "The CORE is protected. Neutralize the enemy first.",
        "hack.nothing": "Nothing to hack here.",
        "hack.title": "=== HACK ===",
        "hack.cost": "Energy cost: {cost}",
        "hack.alarm_triggered": "⚠ Warning: Alarm level {alarm} triggered!",
        "hack.alarm_enemy": "🚨 Alarm enemy deployed in this room!",
        "hack.reduced": "Hack reduced to {hack}",
        "hack.standard_success": "💻 Standard hack succeeded. Choose loot:",
        "hack.fragment_ping": "🛰️ Terminal intel: ROM signatures mapped ({count}).",
        "hack.fragment_ping_none": "Terminal intel: no unknown ROM signatures to reveal.",
        "hack.loot.a": "A. Credits",
        "hack.loot.b": "B. Neuro heal (+25 HP)",
        "hack.loot.c": "C. Hack upgrade (+5 HK)",
        "hack.loot.prompt": "Loot > ",
        "hack.loot.heal": "🧠 Heal applied: +25 HP",
        "hack.loot.upgrade": "⚙ Hack upgrade applied: +5 HK",
        "hack.loot.credits": "💰 Credit loot obtained: +{credits}",
        "hack.success.credits": "💻 Hack succeeded! +{credits} credits",
        "hack.alarm_reduced": "Alarm reduced by 1.",
        "hack.unlock_room": "🔓 Room unlocked.",
        "hack.core_pirated": "☢ CORE hacked. Extraction possible.",
        "hack.done_ms": "Hack completed in {ms} ms",
        "attack.no_target": "No target.",
        "attack.stance.aggressive": "The enemy charges aggressively, ready to hit hard.",
        "attack.stance.defensive": "The enemy turtles behind solid defenses.",
        "attack.stance.unstable": "The enemy moves erratically and unpredictably.",
        "attack.prompt": "Combat: A frontal | B feint | C overload (choose within {time}s)",
        "attack.choice_prompt": "Choice > ",
        "attack.timeout": "Reaction too slow: random combat action selected.",
        "attack.reflex_prompt": "⚡ Reflex: type {char} quickly",
        "attack.reflex.success": "Success in {ms} ms! Bonus: reduced damage.",
        "attack.reflex.failure": "Failed in {ms} ms! Penalty: increased damage.",
        "attack.bonus.surcharge": "Overload augment activated: reduced damage!",
        "attack.bonus.force": "Strength augment activated: reduced damage!",
        "attack.bonus.vitesse": "Speed augment activated: reduced damage!",
        "attack.core.hit": "You strike the CORE Sentinel! Damage: {damage}",
        "attack.core.hp": "CORE Sentinel HP: {hp}",
        "attack.core.counter": "CORE Sentinel counterattacks! You take {damage} damage.",
        "attack.core.neutralized": "CORE Sentinel neutralized!",
        "attack.core.remaining_hack": "Sentinel is down, but you still need to hack the CORE.",
        "attack.neutralize": "You neutralize {enemy}",
        "attack.taken": "You take {damage} damage",
        "enemy_attack.core": "⚠️ CORE Sentinel attacks you! You take {damage} damage.",
        "enemy_attack.normal": "⚠️ {enemy} attacks you! You take {damage} damage.",
        "take.fragment": "ROM fragment recovered: {fragment_id} ({count}/3)",
        "take.item": "Taken: {item}",
        "take.none": "Nothing to take.",
        "use.absent": "Item not found.",
        "use.used": "{item} used.",
        "inventory.title": "Inventory:",
        "inventory.empty": "Empty",
        "inventory.medkit": "- medkit: restores 25 HP",
        "inventory.energy_cell": "- energy_cell: restores 25 energy",
        "inventory.exploit_chip": "- exploit_chip: +10 hack",
        "status.title": "=== AUGMENTED GEAR ===",
        "status.synaptique": "- Synaptic augment: +10s hack time",
        "status.surcharge": "- Overload augment: improves overload in combat",
        "status.interface": "- Enhanced hacker neural interface: matrix reduced by 1",
        "status.combat_chip": "- Combat chip: doubles action time in combat",
        "status.force": "- Strength augment: improves frontal attack",
        "status.vitesse": "- Speed augment: improves feint",
        "status.dissipateur": "- Energy dissipator: halves action energy costs",
        "status.none": "None",
        "status.characteristics": "=== CHARACTERISTICS ===",
        "status.line": "HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}",
        "status.fragments": "ROM fragments: {count}/3",
        "help.commands": "Commands: n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <item> | inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q",
        "shop.title": "=== SHOP ===",
        "shop.credits": "Available credits: {credits}",
        "shop.items": "Available items:",
        "shop.item.1": "1. Synaptic augment - 100 credits: +10s hack time",
        "shop.item.2": "2. Overload augment - 100 credits: improves overload in combat",
        "shop.item.3": "3. Enhanced neural hacker interface - 150 credits: matrix reduced by 1",
        "shop.item.4": "4. Combat chip - 150 credits: doubles action time in combat",
        "shop.item.5": "5. Strength augment - 100 credits: improves frontal attack",
        "shop.item.6": "6. Speed augment - 100 credits: improves feint",
        "shop.item.7": "7. Energy dissipator - 300 credits: halves EN costs for actions",
        "shop.item.0": "0. Exit",
        "shop.prompt": "Choice > ",
        "shop.buy.1": "Synaptic augment purchased! +10s hack time.",
        "shop.buy.2": "Overload augment purchased! Overload improved in combat.",
        "shop.buy.3": "Neural interface purchased! Matrix reduced by 1.",
        "shop.buy.4": "Combat chip purchased! Combat time doubled.",
        "shop.buy.5": "Strength augment purchased! Frontal attack improved.",
        "shop.buy.6": "Speed augment purchased! Feint improved.",
        "shop.buy.7": "Energy dissipator purchased! Action EN costs are now halved.",
        "shop.invalid": "Invalid choice or insufficient credits.",
        "enemy_turn.reinforcement": "⚠ System reinforcement detected",
        "score.title": "=== FINAL SCORE ===",
        "score.base": "Base score: {score}",
        "score.rom_bonus": "ROM fragment bonus: {bonus}",
        "score.time_bonus": "Total time bonus: {bonus}",
        "score.hack_bonus": "Hack time bonus: {bonus}",
        "score.rank": "Your score ranks you #{rank}.",
        "core.pirated": "=== CORE HACKED ===",
        "main.spawn": "spawn position {x},{y}",
        "main.core": "core position {x},{y}",
        "main.story_channel": "ROM channel detected: file {story_id} split into 3 caches.",
        "main.death": "You collapse into the network.",
        "main.alarm_game_over": "🚨 Maximum alarm reached! Game over.",
        "ui.choice_prompt": "Choice > ",
        "ui.reflex_input_prompt": "> ",
        "ui.command_prompt": "\n> ",
        "ui.quit_confirm": "Do you want to quit the current run? (y/n) ",
        "ui.replay_prompt": "Play again? (y/n) ",
        "ui.unknown_command": "Unknown command.",
        "error.unhandled": "An error occurred: {error}",
    },
    "it": {
        "language.title": "=== SCELTA LINGUA ===",
        "language.subtitle": "Codici disponibili:",
        "language.option": "- {code} : {name}",
        "language.prompt": "Lingua (fr/en/it/es) > ",
        "language.selected": "Lingua attiva: {code} ({name})",
        "language.invalid": "Codice non valido. Usa fr, en, it, es.",
        "statusline.compact": "HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3",
        "leaderboard.title": "=== CLASSIFICA ===",
        "leaderboard.entry": "#{idx} {line}",
        "leaderboard.none": "Nessun punteggio registrato.",
        "intro.press_enter": "Premi Invio per iniziare...",
        "startup.launching": "Avvio del gioco...",
        "startup.player_name_prompt": "Nome giocatore: ",
        "startup.player_name_echo": "Giocatore: {name}",
        "startup.difficulty_title": "=== SELEZIONE DIFFICOLTA ===",
        "startup.difficulty_1": "1. Passeggiata cyber - Hack: 60s  Combattimento: 10s  Riflesso: 6s  Moltiplicatore punti: 1x",
        "startup.difficulty_2": "2. Prova cyber - Hack: 45s  Combattimento: 6s   Riflesso: 4s  Moltiplicatore punti: 2x",
        "startup.difficulty_3": "3. Sudore cyber - Hack: 30s  Combattimento: 4s   Riflesso: 2s  Moltiplicatore punti: 3x",
        "startup.difficulty_4": "4. Violenza cyber - Hack: 20s  Combattimento: 3s   Riflesso: 3s  Moltiplicatore punti: 4x",
        "startup.difficulty_prompt": "Scegli livello (1-4): ",
        "startup.difficulty_invalid": "Livello non valido, selezionata la difficolta 3 di default.",
        "map.title": "=== MAPPA ===",
        "map.legend": "Legenda: P=Giocatore | C=Core | .=Stanza visitata | E=Nemico | L=Loot | F=Frammento | M=Multi | #=Sconosciuta",
        "describe.enemy_present": "⚠ Nemico presente: {enemy}",
        "describe.core_hp": "HP CORE Sentinel: {hp}",
        "describe.locked": "🔒 Stanza bloccata.",
        "describe.terminal": "💻 Terminale rilevato.",
        "describe.item_visible": "📦 Oggetto visibile: {item}",
        "describe.fragment_visible": "🧩 Frammento ROM rilevato: {fragment_id}",
        "describe.core_detected": "===== ☢ CORE CENTRALE rilevato! =====",
        "move.locked_exit": "🔒 Impossibile uscire: blocco attivo.",
        "move.wall": "Muro strutturale.",
        "scan.title": "=== SCANSIONE PROFONDA ===",
        "scan.cost": "Costo energetico scansione: {cost}",
        "scan.object_found": "Oggetto nascosto rilevato: {item}",
        "scan.lock_pulse": "Il blocco pulsa a frequenza variabile.",
        "scan.ports_open": "Porte di intrusione ancora aperte.",
        "scan.rom_signature": "Firma ROM frammentaria rilevata in questa stanza.",
        "scan.nothing": "Nessuna novita rilevata.",
        "echo.title": "=== ECHO ESTESO ===",
        "echo.cost": "Costo energetico echo: {cost}",
        "echo.detected": "Firme tattiche rilevate attorno a te: {count}",
        "echo.none": "Nessuna firma tattica rilevata attorno a te.",
        "story.title": "=== FILE ROM DECIFRATO ===",
        "story.id": "ID: {id}",
        "story.name": "Titolo: {title}",
        "story.hacker": "Hacker: {hacker}",
        "story.context": "Contesto: {context}",
        "story.logs": "--- LOG ---",
        "story.epilogue": "--- EPILOGO ---",
        "fragments.title": "=== FRAMMENTI ROM ===",
        "fragments.count": "Raccolta: {found}/{total}",
        "fragments.line": "[{mark}] {id} - {label}",
        "fragments.unlocked": "Accesso al dossier narrativo completo sbloccato.",
        "fragments.read_prompt": "Leggere ora la storia? (y/n) ",
        "fragments.incomplete": "Recupera tutti e 3 i frammenti per decifrare la storia completa.",
        "hack.matrix.title": "=== MATRICE DI INTRUSIONE ===",
        "hack.matrix.sequence": "Sequenza obiettivo: {sequence}",
        "hack.matrix.rules": "Passo 1 libero | Passo 2 stessa colonna | Passo 3 stessa riga",
        "hack.matrix.step_prompt": "Passo {step} > ",
        "hack.matrix.timeout": "Tempo scaduto",
        "hack.matrix.incorrect": "Codice errato",
        "hack.matrix.same_column": "Richiesta stessa colonna",
        "hack.matrix.same_row": "Richiesta stessa riga",
        "core_hint.east": "INDIZIO: Il core e a est.",
        "core_hint.west": "INDIZIO: Il core e a ovest.",
        "core_hint.south": "INDIZIO: Il core e a sud.",
        "core_hint.north": "INDIZIO: Il core e a nord.",
        "hack.blocked_core": "Il CORE e protetto. Neutralizza prima il nemico presente.",
        "hack.nothing": "Niente da hackerare qui.",
        "hack.title": "=== HACK ===",
        "hack.cost": "Costo energetico: {cost}",
        "hack.alarm_triggered": "⚠ Attenzione: allarme livello {alarm} attivato!",
        "hack.alarm_enemy": "🚨 Nemico d'allarme dispiegato in questa stanza!",
        "hack.reduced": "Hack ridotto a {hack}",
        "hack.standard_success": "💻 Hack standard riuscito. Scegli il loot:",
        "hack.fragment_ping": "🛰️ Intel terminale: firme ROM mappate ({count}).",
        "hack.fragment_ping_none": "Intel terminale: nessuna firma ROM sconosciuta da rivelare.",
        "hack.loot.a": "A. Crediti",
        "hack.loot.b": "B. Cura neurocyber (+25 HP)",
        "hack.loot.c": "C. Upgrade hack (+5 HK)",
        "hack.loot.prompt": "Loot > ",
        "hack.loot.heal": "🧠 Cura applicata: +25 HP",
        "hack.loot.upgrade": "⚙ Upgrade hack applicato: +5 HK",
        "hack.loot.credits": "💰 Loot crediti ottenuto: +{credits}",
        "hack.success.credits": "💻 Hack riuscito! +{credits} crediti",
        "hack.alarm_reduced": "Allarme ridotto di 1.",
        "hack.unlock_room": "🔓 Stanza sbloccata.",
        "hack.core_pirated": "☢ CORE hackerato. Estrazione possibile.",
        "hack.done_ms": "Hack completato in {ms} ms",
        "attack.no_target": "Nessun bersaglio.",
        "attack.stance.aggressive": "Il nemico carica con aggressivita, pronto a colpire forte.",
        "attack.stance.defensive": "Il nemico si barrica dietro difese solide.",
        "attack.stance.unstable": "Il nemico si muove in modo erratico e imprevedibile.",
        "attack.prompt": "Combattimento: A frontale | B finta | C sovraccarico (scegli entro {time}s)",
        "attack.choice_prompt": "Scelta > ",
        "attack.timeout": "Tempo di reazione troppo lungo: azione casuale selezionata.",
        "attack.reflex_prompt": "⚡ Riflesso: digita {char} in fretta",
        "attack.reflex.success": "Riuscito in {ms} ms! Bonus: danni ridotti.",
        "attack.reflex.failure": "Fallito in {ms} ms! Malus: danni aumentati.",
        "attack.bonus.surcharge": "Sovraccarico attivato: danni ridotti!",
        "attack.bonus.force": "Potenziamento forza attivato: danni ridotti!",
        "attack.bonus.vitesse": "Potenziamento velocita attivato: danni ridotti!",
        "attack.core.hit": "Attacchi il CORE Sentinel! Danni: {damage}",
        "attack.core.hp": "HP CORE Sentinel: {hp}",
        "attack.core.counter": "Il CORE Sentinel contrattacca! Subisci {damage} danni.",
        "attack.core.neutralized": "CORE Sentinel neutralizzato!",
        "attack.core.remaining_hack": "Sentinel abbattuto, ma devi ancora hackerare il CORE.",
        "attack.neutralize": "Neutralizzi {enemy}",
        "attack.taken": "Subisci {damage} danni",
        "enemy_attack.core": "⚠️ Il CORE Sentinel ti attacca! Subisci {damage} danni.",
        "enemy_attack.normal": "⚠️ {enemy} ti attacca! Subisci {damage} danni.",
        "take.fragment": "Frammento ROM recuperato: {fragment_id} ({count}/3)",
        "take.item": "Preso: {item}",
        "take.none": "Niente da prendere.",
        "use.absent": "Oggetto assente.",
        "use.used": "{item} usato.",
        "inventory.title": "Inventario:",
        "inventory.empty": "Vuoto",
        "inventory.medkit": "- medkit: ripristina 25 HP",
        "inventory.energy_cell": "- energy_cell: ripristina 25 energia",
        "inventory.exploit_chip": "- exploit_chip: +10 hack",
        "status.title": "=== EQUIPAGGIAMENTO AUMENTATO ===",
        "status.synaptique": "- Potenziamento sinaptico: +10s al tempo di hack",
        "status.surcharge": "- Potenziamento sovraccarico: migliora il sovraccarico in combattimento",
        "status.interface": "- Interfaccia neurale hacker avanzata: matrice ridotta di 1",
        "status.combat_chip": "- Chip da combattimento: raddoppia il tempo d'azione in combattimento",
        "status.force": "- Potenziamento forza: migliora l'attacco frontale",
        "status.vitesse": "- Potenziamento velocita: migliora la finta",
        "status.dissipateur": "- Dissipatore energetico: dimezza i costi energetici delle azioni",
        "status.none": "Nessuno",
        "status.characteristics": "=== CARATTERISTICHE ===",
        "status.line": "HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}",
        "status.fragments": "Frammenti ROM: {count}/3",
        "help.commands": "Comandi: n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <oggetto> | inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q",
        "shop.title": "=== NEGOZIO ===",
        "shop.credits": "Crediti disponibili: {credits}",
        "shop.items": "Oggetti disponibili:",
        "shop.item.1": "1. Potenziamento sinaptico - 100 crediti: +10s al tempo di hack",
        "shop.item.2": "2. Potenziamento sovraccarico - 100 crediti: migliora il sovraccarico in combattimento",
        "shop.item.3": "3. Interfaccia neurale hacker avanzata - 150 crediti: matrice ridotta di 1",
        "shop.item.4": "4. Chip da combattimento - 150 crediti: raddoppia il tempo per agire in combattimento",
        "shop.item.5": "5. Potenziamento forza - 100 crediti: migliora attacco frontale",
        "shop.item.6": "6. Potenziamento velocita - 100 crediti: migliora finta",
        "shop.item.7": "7. Dissipatore energetico - 300 crediti: dimezza i costi EN delle azioni",
        "shop.item.0": "0. Esci",
        "shop.prompt": "Scelta > ",
        "shop.buy.1": "Potenziamento sinaptico acquistato! +10s al tempo di hack.",
        "shop.buy.2": "Potenziamento sovraccarico acquistato! Sovraccarico migliorato in combattimento.",
        "shop.buy.3": "Interfaccia neurale acquistata! Matrice ridotta di 1.",
        "shop.buy.4": "Chip da combattimento acquistato! Tempo di combattimento raddoppiato.",
        "shop.buy.5": "Potenziamento forza acquistato! Attacco frontale migliorato.",
        "shop.buy.6": "Potenziamento velocita acquistato! Finta migliorata.",
        "shop.buy.7": "Dissipatore energetico acquistato! I costi EN delle azioni sono dimezzati.",
        "shop.invalid": "Scelta non valida o crediti insufficienti.",
        "enemy_turn.reinforcement": "⚠ Rinforzo di sistema rilevato",
        "score.title": "=== PUNTEGGIO FINALE ===",
        "score.base": "Punteggio base: {score}",
        "score.rom_bonus": "Bonus frammenti ROM: {bonus}",
        "score.time_bonus": "Bonus tempo totale: {bonus}",
        "score.hack_bonus": "Bonus tempo hack: {bonus}",
        "score.rank": "Il tuo punteggio ti classifica #{rank}.",
        "core.pirated": "=== CORE HACKERATO ===",
        "main.spawn": "posizione spawn {x},{y}",
        "main.core": "posizione core {x},{y}",
        "main.story_channel": "Canale ROM rilevato: dossier {story_id} frammentato in 3 cache.",
        "main.death": "Cadi nella rete.",
        "main.alarm_game_over": "🚨 Allarme massimo raggiunto! Game over.",
        "ui.choice_prompt": "Scelta > ",
        "ui.reflex_input_prompt": "> ",
        "ui.command_prompt": "\n> ",
        "ui.quit_confirm": "Vuoi uscire dalla partita in corso? (y/n) ",
        "ui.replay_prompt": "Rigiocare? (y/n) ",
        "ui.unknown_command": "Comando sconosciuto.",
        "error.unhandled": "Si e verificato un errore: {error}",
    },
    "es": {
        "language.title": "=== SELECCION DE IDIOMA ===",
        "language.subtitle": "Codigos disponibles:",
        "language.option": "- {code} : {name}",
        "language.prompt": "Idioma (fr/en/it/es) > ",
        "language.selected": "Idioma activo: {code} ({name})",
        "language.invalid": "Codigo invalido. Usa fr, en, it, es.",
        "statusline.compact": "HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3",
        "leaderboard.title": "=== CLASIFICACION ===",
        "leaderboard.entry": "#{idx} {line}",
        "leaderboard.none": "No hay puntuaciones registradas.",
        "intro.press_enter": "Pulsa Enter para empezar...",
        "startup.launching": "Iniciando juego...",
        "startup.player_name_prompt": "Nombre del jugador: ",
        "startup.player_name_echo": "Jugador: {name}",
        "startup.difficulty_title": "=== SELECCION DE DIFICULTAD ===",
        "startup.difficulty_1": "1. Paseo cyber - Hack: 60s  Combate: 10s  Reflejo: 6s  Multiplicador de puntos: 1x",
        "startup.difficulty_2": "2. Prueba cyber - Hack: 45s  Combate: 6s   Reflejo: 4s  Multiplicador de puntos: 2x",
        "startup.difficulty_3": "3. Sudor cyber - Hack: 30s  Combate: 4s   Reflejo: 2s  Multiplicador de puntos: 3x",
        "startup.difficulty_4": "4. Violencia cyber - Hack: 20s  Combate: 3s   Reflejo: 3s  Multiplicador de puntos: 4x",
        "startup.difficulty_prompt": "Elige nivel (1-4): ",
        "startup.difficulty_invalid": "Nivel invalido, se selecciona dificultad 3 por defecto.",
        "map.title": "=== MAPA ===",
        "map.legend": "Leyenda: P=Jugador | C=Core | .=Sala visitada | E=Enemigo | L=Loot | F=Fragmento | M=Multi | #=Desconocida",
        "describe.enemy_present": "⚠ Enemigo presente: {enemy}",
        "describe.core_hp": "HP del CORE Sentinel: {hp}",
        "describe.locked": "🔒 Sala bloqueada.",
        "describe.terminal": "💻 Terminal detectado.",
        "describe.item_visible": "📦 Objeto visible: {item}",
        "describe.fragment_visible": "🧩 Fragmento ROM detectado: {fragment_id}",
        "describe.core_detected": "===== ☢ CORE CENTRAL detectado! =====",
        "move.locked_exit": "🔒 No puedes salir: bloqueo activo.",
        "move.wall": "Muro estructural.",
        "scan.title": "=== ESCANEO PROFUNDO ===",
        "scan.cost": "Costo de energia del escaneo: {cost}",
        "scan.object_found": "Objeto oculto detectado: {item}",
        "scan.lock_pulse": "El bloqueo pulsa con frecuencia variable.",
        "scan.ports_open": "Puertos de intrusion aun abiertos.",
        "scan.rom_signature": "Firma ROM fragmentaria detectada en la sala.",
        "scan.nothing": "No se detecta nada nuevo.",
        "echo.title": "=== ECHO EXTENDIDO ===",
        "echo.cost": "Costo de energia del echo: {cost}",
        "echo.detected": "Firmas tacticas detectadas a tu alrededor: {count}",
        "echo.none": "No se detecta ninguna firma tactica a tu alrededor.",
        "story.title": "=== ARCHIVO ROM DESCIFRADO ===",
        "story.id": "ID: {id}",
        "story.name": "Titulo: {title}",
        "story.hacker": "Hacker: {hacker}",
        "story.context": "Contexto: {context}",
        "story.logs": "--- LOGS ---",
        "story.epilogue": "--- EPILOGO ---",
        "fragments.title": "=== FRAGMENTOS ROM ===",
        "fragments.count": "Recolectado: {found}/{total}",
        "fragments.line": "[{mark}] {id} - {label}",
        "fragments.unlocked": "Acceso al dossier narrativo completo desbloqueado.",
        "fragments.read_prompt": "Leer la historia ahora? (y/n) ",
        "fragments.incomplete": "Recoge los 3 fragmentos para descifrar la historia completa.",
        "hack.matrix.title": "=== MATRIZ DE INTRUSION ===",
        "hack.matrix.sequence": "Secuencia objetivo: {sequence}",
        "hack.matrix.rules": "Paso 1 libre | Paso 2 misma columna | Paso 3 misma fila",
        "hack.matrix.step_prompt": "Paso {step} > ",
        "hack.matrix.timeout": "Tiempo agotado",
        "hack.matrix.incorrect": "Codigo incorrecto",
        "hack.matrix.same_column": "Se requiere misma columna",
        "hack.matrix.same_row": "Se requiere misma fila",
        "core_hint.east": "PISTA: El core esta al este.",
        "core_hint.west": "PISTA: El core esta al oeste.",
        "core_hint.south": "PISTA: El core esta al sur.",
        "core_hint.north": "PISTA: El core esta al norte.",
        "hack.blocked_core": "El CORE esta protegido. Neutraliza primero al enemigo presente.",
        "hack.nothing": "No hay nada que hackear aqui.",
        "hack.title": "=== HACK ===",
        "hack.cost": "Costo de energia: {cost}",
        "hack.alarm_triggered": "⚠ Atencion: alarma nivel {alarm} activada!",
        "hack.alarm_enemy": "🚨 Enemigo de alarma desplegado en esta sala!",
        "hack.reduced": "Hack reducido a {hack}",
        "hack.standard_success": "💻 Hack estandar completado. Elige loot:",
        "hack.fragment_ping": "🛰️ Intel de terminal: firmas ROM mapeadas ({count}).",
        "hack.fragment_ping_none": "Intel de terminal: no hay firmas ROM desconocidas por revelar.",
        "hack.loot.a": "A. Creditos",
        "hack.loot.b": "B. Curacion neurocyber (+25 HP)",
        "hack.loot.c": "C. Mejora de hack (+5 HK)",
        "hack.loot.prompt": "Loot > ",
        "hack.loot.heal": "🧠 Curacion aplicada: +25 HP",
        "hack.loot.upgrade": "⚙ Mejora de hack aplicada: +5 HK",
        "hack.loot.credits": "💰 Loot de creditos obtenido: +{credits}",
        "hack.success.credits": "💻 Hack completado! +{credits} creditos",
        "hack.alarm_reduced": "Alarma reducida en 1.",
        "hack.unlock_room": "🔓 Sala desbloqueada.",
        "hack.core_pirated": "☢ CORE hackeado. Extraccion posible.",
        "hack.done_ms": "Hack realizado en {ms} ms",
        "attack.no_target": "Sin objetivo.",
        "attack.stance.aggressive": "El enemigo carga con agresividad, listo para golpear fuerte.",
        "attack.stance.defensive": "El enemigo se atrinchera tras defensas solidas.",
        "attack.stance.unstable": "El enemigo se mueve de forma erratica e impredecible.",
        "attack.prompt": "Combate: A frontal | B finta | C sobrecarga (elige en {time}s)",
        "attack.choice_prompt": "Eleccion > ",
        "attack.timeout": "Tiempo de reaccion demasiado largo: accion aleatoria seleccionada.",
        "attack.reflex_prompt": "⚡ Reflejo: escribe {char} rapido",
        "attack.reflex.success": "Exito en {ms} ms! Bonus: dano reducido.",
        "attack.reflex.failure": "Fallo en {ms} ms! Penalizacion: dano aumentado.",
        "attack.bonus.surcharge": "Sobrecarga activada: dano reducido!",
        "attack.bonus.force": "Aumento de fuerza activado: dano reducido!",
        "attack.bonus.vitesse": "Aumento de velocidad activado: dano reducido!",
        "attack.core.hit": "Atacas al CORE Sentinel! Dano: {damage}",
        "attack.core.hp": "HP del CORE Sentinel: {hp}",
        "attack.core.counter": "El CORE Sentinel contraataca! Recibes {damage} de dano.",
        "attack.core.neutralized": "CORE Sentinel neutralizado!",
        "attack.core.remaining_hack": "El Sentinel cayo, pero aun debes hackear el CORE.",
        "attack.neutralize": "Neutralizas a {enemy}",
        "attack.taken": "Recibes {damage} de dano",
        "enemy_attack.core": "⚠️ El CORE Sentinel te ataca! Recibes {damage} de dano.",
        "enemy_attack.normal": "⚠️ {enemy} te ataca! Recibes {damage} de dano.",
        "take.fragment": "Fragmento ROM recuperado: {fragment_id} ({count}/3)",
        "take.item": "Recogido: {item}",
        "take.none": "Nada que recoger.",
        "use.absent": "Objeto ausente.",
        "use.used": "{item} usado.",
        "inventory.title": "Inventario:",
        "inventory.empty": "Vacio",
        "inventory.medkit": "- medkit: restaura 25 HP",
        "inventory.energy_cell": "- energy_cell: restaura 25 energia",
        "inventory.exploit_chip": "- exploit_chip: +10 hack",
        "status.title": "=== EQUIPO AUMENTADO ===",
        "status.synaptique": "- Aumento sinaptico: +10s al tiempo de hack",
        "status.surcharge": "- Aumento de sobrecarga: mejora sobrecarga en combate",
        "status.interface": "- Interfaz neuronal de hacker aumentada: matriz reducida en 1",
        "status.combat_chip": "- Chip de combate: duplica el tiempo de accion en combate",
        "status.force": "- Aumento de fuerza: mejora ataque frontal",
        "status.vitesse": "- Aumento de velocidad: mejora finta",
        "status.dissipateur": "- Disipador energetico: reduce a la mitad los costos de energia de las acciones",
        "status.none": "Ninguno",
        "status.characteristics": "=== CARACTERISTICAS ===",
        "status.line": "HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}",
        "status.fragments": "Fragmentos ROM: {count}/3",
        "help.commands": "Comandos: n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <objeto> | inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q",
        "shop.title": "=== TIENDA ===",
        "shop.credits": "Creditos disponibles: {credits}",
        "shop.items": "Objetos disponibles:",
        "shop.item.1": "1. Aumento sinaptico - 100 creditos: +10s al tiempo de hack",
        "shop.item.2": "2. Aumento de sobrecarga - 100 creditos: mejora sobrecarga en combate",
        "shop.item.3": "3. Interfaz neuronal de hacker aumentada - 150 creditos: matriz reducida en 1",
        "shop.item.4": "4. Chip de combate - 150 creditos: duplica el tiempo para actuar en combate",
        "shop.item.5": "5. Aumento de fuerza - 100 creditos: mejora ataque frontal",
        "shop.item.6": "6. Aumento de velocidad - 100 creditos: mejora finta",
        "shop.item.7": "7. Disipador energetico - 300 creditos: reduce a la mitad los costos EN de las acciones",
        "shop.item.0": "0. Salir",
        "shop.prompt": "Eleccion > ",
        "shop.buy.1": "Aumento sinaptico comprado! +10s al tiempo de hack.",
        "shop.buy.2": "Aumento de sobrecarga comprado! Sobrecarga mejorada en combate.",
        "shop.buy.3": "Interfaz neuronal comprada! Matriz reducida en 1.",
        "shop.buy.4": "Chip de combate comprado! Tiempo de combate duplicado.",
        "shop.buy.5": "Aumento de fuerza comprado! Ataque frontal mejorado.",
        "shop.buy.6": "Aumento de velocidad comprado! Finta mejorada.",
        "shop.buy.7": "Disipador energetico comprado! Los costos EN de las acciones ahora se reducen a la mitad.",
        "shop.invalid": "Eleccion invalida o creditos insuficientes.",
        "enemy_turn.reinforcement": "⚠ Refuerzo del sistema detectado",
        "score.title": "=== PUNTUACION FINAL ===",
        "score.base": "Puntuacion base: {score}",
        "score.rom_bonus": "Bonus de fragmentos ROM: {bonus}",
        "score.time_bonus": "Bonus de tiempo total: {bonus}",
        "score.hack_bonus": "Bonus de tiempo de hack: {bonus}",
        "score.rank": "Tu puntuacion te coloca en el puesto #{rank}.",
        "core.pirated": "=== CORE HACKEADO ===",
        "main.spawn": "posicion de spawn {x},{y}",
        "main.core": "posicion del core {x},{y}",
        "main.story_channel": "Canal ROM detectado: dossier {story_id} fragmentado en 3 caches.",
        "main.death": "Caes en la red.",
        "main.alarm_game_over": "🚨 Alarma maxima alcanzada! Game over.",
        "ui.choice_prompt": "Eleccion > ",
        "ui.reflex_input_prompt": "> ",
        "ui.command_prompt": "\n> ",
        "ui.quit_confirm": "Quieres salir de la partida actual? (y/n) ",
        "ui.replay_prompt": "Jugar otra vez? (y/n) ",
        "ui.unknown_command": "Comando desconocido.",
        "error.unhandled": "Ha ocurrido un error: {error}",
    },
}

TRANSLATIONS["fr"]["intro.full"] = INTRO
TRANSLATIONS["en"]["intro.full"] = """
==============================
    NEON NODE v6
==============================

Infiltrate the megastructure.
Reach the central CORE, hack it, and get out alive.

For hacks:
- The higher your hack, the smaller the matrix.
- Step 1: freely find the correct hex value in the matrix (must match the first requested code value).
- Step 2: must be in the same column as step 1.
- Step 3: must be in the same row as step 2.

Time is limited to complete the hack, and failure raises your alarm and lowers your hack.

Credits are earned by hacking terminals and can be used to buy upgrades in the shop.
The faster you hack, the more credits you earn!

Commands:
 north / n : move north
 south / s : move south
 east / e : move east
 west / w  : move west
 scan / sc : scan the room for hidden objects or clues
 echo / ec : probe nearby rooms and reveal tactical map markers
 hack / h : try to hack a terminal or disable a lock
 attack : engage combat against a present enemy
 take / t : pick up a visible item in the room or found by scan
 use <item> / u <item> : use an inventory item (e.g. use medkit)
 map / m : display the level map (P = position, C = core, . = visited room, # = unvisited room)
 inventory / inv : display inventory
 status / stat : display status and upgrades
 fragments / fra : display collected ROM fragments and the story file
 shop / sh : open the shop to buy upgrades with credits
 help / he : display commands
 quit / q : quit the game
"""
TRANSLATIONS["it"]["intro.full"] = """
==============================
    NEON NODE v6
==============================

Infiltrati nella megastruttura.
Raggiungi il CORE centrale, hackeralo ed esci vivo.

Per gli hack:
- Piu alto e il tuo hack, piu piccola e la matrice.
- Passo 1: trova liberamente il valore esadecimale corretto nella matrice (deve corrispondere al primo valore richiesto).
- Passo 2: deve essere nella stessa colonna del passo 1.
- Passo 3: deve essere nella stessa riga del passo 2.

Il tempo e limitato per completare l'hack; fallire aumenta l'allarme e riduce il tuo hack.

I crediti si ottengono hackerando terminali e possono essere usati per comprare potenziamenti nel negozio.
Piu velocemente hackeri, piu crediti guadagni!

Comandi:
 north / n : muoversi a nord
 south / s : muoversi a sud
 east / e : muoversi a est
 west / w  : muoversi a ovest
 scan / sc : scandire la sala per trovare oggetti nascosti o indizi
 echo / ec : sondare le sale vicine e rivelare marcatori tattici sulla mappa
 hack / h : tentare di hackerare un terminale o disattivare un blocco
 attack : ingaggiare combattimento con un nemico presente
 take / t : raccogliere un oggetto visibile nella sala o trovato con scan
 use <oggetto> / u <oggetto> : usare un oggetto dell'inventario (es: use medkit)
 map / m : mostrare la mappa del livello (P = posizione, C = core, . = sala visitata, # = sala non visitata)
 inventory / inv : mostrare inventario
 status / stat : mostrare stato e potenziamenti
 fragments / fra : mostrare frammenti ROM raccolti e dossier narrativo
 shop / sh : aprire il negozio per comprare potenziamenti con i crediti
 help / he : mostrare i comandi
 quit / q : uscire dal gioco
"""
TRANSLATIONS["es"]["intro.full"] = """
==============================
    NEON NODE v6
==============================

Infiltrate en la megaestructura.
Llega al CORE central, hackealo y sal con vida.

Para los hacks:
- Cuanto mas alto sea tu hack, mas pequena sera la matriz.
- Paso 1: encuentra libremente el valor hex correcto en la matriz (debe coincidir con el primer valor pedido).
- Paso 2: debe estar en la misma columna que el paso 1.
- Paso 3: debe estar en la misma fila que el paso 2.

El tiempo es limitado para completar el hack; fallar aumenta tu alarma y reduce tu hack.

Los creditos se ganan hackeando terminales y pueden usarse para comprar mejoras en la tienda.
Cuanto mas rapido hackees, mas creditos ganas.

Comandos:
 north / n : moverse al norte
 south / s : moverse al sur
 east / e : moverse al este
 west / w  : moverse al oeste
 scan / sc : escanear la sala para encontrar objetos ocultos o pistas
 echo / ec : sondear salas cercanas y revelar marcadores tacticos en el mapa
 hack / h : intentar hackear un terminal o desactivar un bloqueo
 attack : iniciar combate contra un enemigo presente
 take / t : recoger un objeto visible en la sala o encontrado con scan
 use <objeto> / u <objeto> : usar un objeto del inventario (ej: use medkit)
 map / m : mostrar el mapa del nivel (P = posicion, C = core, . = sala visitada, # = sala no visitada)
 inventory / inv : mostrar inventario
 status / stat : mostrar estado y mejoras
 fragments / fra : mostrar fragmentos ROM recogidos y el dossier narrativo
 shop / sh : abrir la tienda para comprar mejoras con creditos
 help / he : mostrar comandos
 quit / q : salir del juego
"""

# Zone d'histoires ROM: ajoute ici de nouveaux dossiers avec un id unique.
# Le jeu en choisit un au hasard en debut de partie.
ROM_STORY_ARCHIVE = [
    {
        "id": "ROM-AX13",
        "title": "AX13 // Derniere Derive",
        "hacker": "Mara Voss (elle)",
        "bio": "Ex-ingenieure reseau de Kheiron Dynamics, disparue apres avoir tente de faire fuiter du code interne.",
        "fragments": [
            {"id": "AX13-1", "label": "Bootlog Bunker"},
            {"id": "AX13-2", "label": "Journal de Progression"},
            {"id": "AX13-3", "label": "Signal de Fin"}
        ],
        "logs": [
            "[2091-04-12 22:13] Infiltration entree niveau C. Bruit des drones plus fort que prevu.",
            "[2091-04-12 22:17] Le sas sent toujours l'ozone. J'avais dessine ce protocole il y a six ans. Le voir reutilise ici donne envie de vomir.",
            "[2091-04-12 22:24] Une camera m'a suivie sans declencher d'alerte. Soit je suis deja referencee, soit quelqu'un ralentit le systeme.",
            "[2091-04-12 22:31] Verrouillage thermique neutralise. J'ai perdu 30% de mes outils.",
            "[2091-04-12 22:38] Lian disait toujours qu'on finit par habiter les structures qu'on deteste. Je crois qu'elle avait raison.",
            "[2091-04-12 22:49] J'ai vu le sentinel au loin. Ce n'est pas un bot standard. Il hesite avant de tourner son optique vers moi.",
            "[2091-04-12 23:02] Alarmes en cascade. Les couloirs se reconfigurent en boucle.",
            "[2091-04-12 23:05] Paradoxe: j'entre pour saboter ce systeme, mais chaque porte ouverte prouve que mon ancien code tient encore mieux que moi.",
            "[2091-04-12 23:09] Si quelqu'un lit ca: ne reste jamais immobile apres un hack reussi.",
            "[2091-04-12 23:11] Je saigne dans ma combinaison. Je laisse ce dossier dans trois caches ROM."
        ],
        "epilogue": "Fin de transmission. Le signal de Mara coupe net apres une surcharge de securite."
    },
    {
        "id": "ROM-KR22",
        "title": "KR22 // Dette Rouge",
        "hacker": "Kenji Rault (il)",
        "bio": "Courrier de donnees indep, infiltrait la megastructure pour effacer un contrat de dette.",
        "fragments": [
            {"id": "KR22-1", "label": "Mandat Nocturne"},
            {"id": "KR22-2", "label": "Map Corrompue"},
            {"id": "KR22-3", "label": "Dernier Pledge"}
        ],
        "logs": [
            "[2088-09-03 01:40] Entree silencieuse. J'ai paye un fixeur pour une cle monousage.",
            "[2088-09-03 01:46] Je cours mieux quand je suis en colere. Mauvaise nouvelle: je suis en colere depuis des annees.",
            "[2088-09-03 02:02] Mon scanner ment. Certaines salles existent puis disparaissent.",
            "[2088-09-03 02:09] Ma soeur croit que je transporte encore des colis anonymes. Je n'ai jamais ose lui dire que parfois les colis sont des preuves.",
            "[2088-09-03 02:19] J'ai recupere des credits, mais chaque terminal augmente la pression.",
            "[2088-09-03 02:25] Le CORE diffuse mon ancien dossier medical. Ils me connaissent.",
            "[2088-09-03 02:28] Paradoxe idiot: voler des credits pour effacer une dette, c'est encore obeir a la logique du compte.",
            "[2088-09-03 02:33] Je continue. Si je sors, ma soeur dort enfin sans dette.",
            "[2088-09-03 02:36] Impact. Drone dans mon angle mort. Je segmente le journal en 3 ROM."
        ],
        "epilogue": "Le contrat de dette n'a jamais ete retrouve dans les archives publiques."
    },
    {
        "id": "ROM-NQ05",
        "title": "NQ05 // Chambre Froide",
        "hacker": "Noor Qassem (iel)",
        "bio": "Cryptanalyste freelance specialise dans les memoires mortes et les IA patrimoniales.",
        "fragments": [
            {"id": "NQ05-1", "label": "Trace d'Approche"},
            {"id": "NQ05-2", "label": "Rupture d'Interface"},
            {"id": "NQ05-3", "label": "Voix du Noyau"}
        ],
        "logs": [
            "[2093-02-20 18:05] Les murs sont froids. Tout ici consomme la chaleur comme des preuves.",
            "[2093-02-20 18:11] Une porte a rejoue ma propre respiration avec trois secondes d'avance.",
            "[2093-02-20 18:27] Une salle m'a rendu mon propre reflet avec 4 secondes d'avance.",
            "[2093-02-20 18:36] Dans le squat serveur on disait qu'une archive sauvee vaut parfois une emeute.",
            "[2093-02-20 18:51] Les routines sentinelles miment des erreurs humaines. Mauvais signe.",
            "[2093-02-20 19:04] J'ai reussi un hack propre. L'alarme est quand meme montee.",
            "[2093-02-20 19:10] Paradoxe: je preserve des fragments de memoire alors que je ne sais meme plus si certains souvenirs sont a moi.",
            "[2093-02-20 19:18] Si je tombe, que quelqu'un sorte ces logs. Que ca serve a autre chose.",
            "[2093-02-20 19:21] Contact perdu. Je verrouille mon histoire en fragments ROM."
        ],
        "epilogue": "Le reste des donnees de Noor est marque comme irreconciliable."
    },
    {
        "id": "ROM-LV77",
        "title": "LV77 // Fork Sauvage",
        "hacker": "Leia Varek (elle)",
        "bio": "Developpeuse issue d'un collectif logiciel libre dissous apres perquisition.",
        "fragments": [
            {"id": "LV77-1", "label": "Depot Cache"},
            {"id": "LV77-2", "label": "Conflit de Branche"},
            {"id": "LV77-3", "label": "Commit Final"}
        ],
        "logs": [
            "[2090-06-03 00:11] Entree validee. Les scanners tournent sur une vieille base Unix maquillee.",
            "[2090-06-03 00:19] Ada disait qu'un fork est parfois une rupture amoureuse en syntaxe propre.",
            "[2090-06-03 00:28] J'entre pour voler un depot qui m'appartenait deja avant brevetage.",
            "[2090-06-03 00:42] Premier sentinel neutralise.",
            "[2090-06-03 00:57] Paradoxe: je hais les monopoles mais j'espere encore que mon code survive sous leur logo.",
            "[2090-06-03 01:03] Si quelqu'un lit ceci: publier reste parfois plus dangereux qu'effacer."
        ],
        "epilogue": "Le depot n'a jamais ete republie integralement."
    },
    {
        "id": "ROM-SM04",
        "title": "SM04 // Zone Muette",
        "hacker": "Sam Mirek (il)",
        "bio": "Ancien technicien radio pirate specialise dans les bulletins clandestins.",
        "fragments": [
            {"id": "SM04-1", "label": "Frequence 1"},
            {"id": "SM04-2", "label": "Frequence 2"},
            {"id": "SM04-3", "label": "Frequence 3"}
        ],
        "logs": [
            "[2087-11-19 03:10] Je reconnais les parasites electriques avant meme les drones.",
            "[2087-11-19 03:21] Une enceinte murale rejoue ma propre emission pirate de 2084.",
            "[2087-11-19 03:34] Mon frere disait que parler trop fort finit toujours par attirer des bottes.",
            "[2087-11-19 03:41] Paradoxe: je pirate des frequences pour liberer la parole, mais ici chaque mot me localise.",
            "[2087-11-19 03:52] Si je tombe, laissez au moins le bruit circuler."
        ],
        "epilogue": "Aucune source n'a confirme la sortie de Sam."
    },
    {
        "id": "ROM-IR31",
        "title": "IR31 // Cendre Administrative",
        "hacker": "Iris Ren (elle)",
        "bio": "Ex-employee administrative ayant sabote des expulsions automatisees.",
        "fragments": [
            {"id": "IR31-1", "label": "Dossier Faux"},
            {"id": "IR31-2", "label": "Procedure Inverse"},
            {"id": "IR31-3", "label": "Archive Cendre"}
        ],
        "logs": [
            "[2092-01-08 19:14] Je connais encore les menus internes mieux que les agents qui les appliquent.",
            "[2092-01-08 19:25] J'ai deja sauve cent trente-deux dossiers avec de simples fautes volontaires.",
            "[2092-01-08 19:39] Ici les terminaux classent les vies comme des tickets.",
            "[2092-01-08 19:48] Paradoxe: falsifier pour retablir un peu de justice reste quand meme falsifier.",
            "[2092-01-08 19:56] Je continue."
        ],
        "epilogue": "Les journaux internes mentionnent une anomalie humaine persistante."
    },
    {
        "id": "ROM-DX90",
        "title": "DX90 // Syntaxe Dissidente",
        "hacker": "Dax Oren (iel)",
        "bio": "Mainteneur d'une distribution clandestine chiffree.",
        "fragments": [
            {"id": "DX90-1", "label": "Bootstrap"},
            {"id": "DX90-2", "label": "Kernel Drift"},
            {"id": "DX90-3", "label": "Root Panic"}
        ],
        "logs": [
            "[2094-07-01 21:03] Cle injectee dans le reseau secondaire.",
            "[2094-07-01 21:17] Reunion collective hier: deux heures pour debattre d'un nom de paquet.",
            "[2094-07-01 21:31] Paradoxe: nous voulons abolir les hierarchies mais quelqu'un finit toujours par merger seul.",
            "[2094-07-01 21:44] Premier tir evite.",
            "[2094-07-01 21:52] Meme les revolutions ont besoin de quelqu'un qui pense a te rappeler de manger."
        ],
        "epilogue": "Une cle similaire a reapparu plus tard sur plusieurs reseaux libres."
    },
    {
        "id": "ROM-PT12",
        "title": "PT12 // Ligne Fantome",
        "hacker": "Pia Torres (elle)",
        "bio": "Ancienne conductrice de metro autonome devenue saboteuse technique.",
        "fragments": [
            {"id": "PT12-1", "label": "Rail Mort"},
            {"id": "PT12-2", "label": "Bypass"},
            {"id": "PT12-3", "label": "Derniere Ligne"}
        ],
        "logs": [
            "[2089-12-14 04:05] Le silence ici ressemble aux tunnels avant remise sous tension.",
            "[2089-12-14 04:18] J'ai appris a ralentir les systemes avant d'apprendre a les casser.",
            "[2089-12-14 04:29] Paradoxe: je hais les automatismes mais je fais confiance a mes reflexes plus qu'aux gens.",
            "[2089-12-14 04:37] Deux drones derriere moi."
        ],
        "epilogue": "Le dossier des transports privatise n'a jamais refait surface."
    },
    {
        "id": "ROM-HQ44",
        "title": "HQ44 // Archive de Bruit",
        "hacker": "Hugo Quent (il)",
        "bio": "Musicien noise devenu pirate de signaux.",
        "fragments": [
            {"id": "HQ44-1", "label": "Impulse"},
            {"id": "HQ44-2", "label": "Feedback"},
            {"id": "HQ44-3", "label": "Cut"}
        ],
        "logs": [
            "[2086-03-03 02:14] Chaque alarme ici a presque une tonalite exploitable.",
            "[2086-03-03 02:27] Je compte mes pas comme des mesures.",
            "[2086-03-03 02:39] Paradoxe: transformer la peur en rythme ne l'annule pas.",
            "[2086-03-03 02:45] Je crois entendre un souffle derriere les relais."
        ],
        "epilogue": "Un extrait audio attribue a Hugo circule encore dans certains reseaux pirates."
    },
    {
        "id": "ROM-ZE08",
        "title": "ZE08 // Commune Incomplete",
        "hacker": "Zea Elin (elle)",
        "bio": "Membre d'une micro-commune urbaine autogeree.",
        "fragments": [
            {"id": "ZE08-1", "label": "Cuisine Collective"},
            {"id": "ZE08-2", "label": "Compteur Noir"},
            {"id": "ZE08-3", "label": "Sortie Incomplete"}
        ],
        "logs": [
            "[2095-05-10 23:01] On a partage la soupe avant mon depart.",
            "[2095-05-10 23:14] Les relevés energetiques mentent exactement comme les prefets.",
            "[2095-05-10 23:28] Paradoxe: vivre sans chef demande parfois plus de discipline que l'inverse.",
            "[2095-05-10 23:37] Si je reviens, il faudra encore reparer le chargeur solaire du toit."
        ],
        "epilogue": "Le quartier de Zea a subi une coupure totale deux semaines plus tard."
    }
]

ROOM_DESCRIPTIONS = [
    "Couloir saturé de néons rouges.",
    "Salle serveur où bourdonnent des relais thermiques.",
    "Zone technique abandonnée couverte de câbles.",
    "Ancien checkpoint de sécurité.",
    "Passage étroit où clignote une enseigne cassée.",
    "Salle noyée dans un bruit électrique intermittent.",
    "Salle de contrôle avec écrans holographiques défaillants.",
    "Tunnel de ventilation rempli de conduits rouillés.",
    "Laboratoire abandonné avec équipements médicaux étranges.",
    "Hangar vide résonnant d'échos lointains.",
    "Bureau exécutif avec mobilier high-tech détruit.",
    "Zone de stockage avec caisses de données empilées.",
    "Salle de réunion avec table interactive brisée.",
    "Couloir d'accès aux ascenseurs bloqués.",
    "Zone de maintenance avec outils éparpillés."
]

ENEMIES = ["Drone", "Guard", "Sentry Bot", "Proxy Hunter"]
ITEMS = ["medkit", "energy_cell", "exploit_chip"]
HEX_VALUES = ['7A', '3F', '9C', 'BD', 'E1', '55', '2D', '8B', '4E', 'AA', '6C', 'F2', '1D', 'C7', 'B4', '0F', 'D9', 'A3', '5E', '91']

TRANSLATIONS["fr"]["content.room_descriptions"] = ROOM_DESCRIPTIONS
TRANSLATIONS["fr"]["content.enemies"] = ENEMIES
TRANSLATIONS["fr"]["content.items"] = ITEMS
TRANSLATIONS["fr"]["content.rom_story_archive"] = ROM_STORY_ARCHIVE
TRANSLATIONS["en"]["content.rom_story_archive"] = [
    {
        "id": "ROM-AX13",
        "title": "AX13 // Last Drift",
        "hacker": "Mara Voss (she)",
        "bio": "Former network engineer at Kheiron Dynamics, disappeared after trying to leak internal code.",
        "fragments": [
            {"id": "AX13-1", "label": "Bunker Bootlog"},
            {"id": "AX13-2", "label": "Progress Log"},
            {"id": "AX13-3", "label": "End Signal"}
        ],
        "logs": [
            "[2091-04-12 22:13] Infiltration at level C entrance. Drone noise louder than expected.",
            "[2091-04-12 22:17] The airlock still smells like ozone. I designed this protocol six years ago. Seeing it reused here makes me sick.",
            "[2091-04-12 22:24] A camera tracked me without triggering an alert. Either I am already flagged, or someone is slowing the system.",
            "[2091-04-12 22:31] Thermal lock neutralized. I lost 30% of my tools.",
            "[2091-04-12 22:38] Lian always said we end up living inside the structures we hate. I think she was right.",
            "[2091-04-12 22:49] I saw the Sentinel in the distance. It is not a standard bot. It hesitates before turning its optics toward me.",
            "[2091-04-12 23:02] Cascading alarms. Corridors keep reconfiguring in loops.",
            "[2091-04-12 23:05] Paradox: I came in to sabotage this system, yet every opened door proves my old code still holds better than I do.",
            "[2091-04-12 23:09] If anyone reads this: never stay still after a successful hack.",
            "[2091-04-12 23:11] I am bleeding into my suit. Leaving this file in three ROM caches."
        ],
        "epilogue": "End of transmission. Mara's signal cuts abruptly after a security overload."
    },
    {
        "id": "ROM-KR22",
        "title": "KR22 // Red Debt",
        "hacker": "Kenji Rault (he)",
        "bio": "Independent data courier, infiltrated the megastructure to erase a debt contract.",
        "fragments": [
            {"id": "KR22-1", "label": "Night Warrant"},
            {"id": "KR22-2", "label": "Corrupted Map"},
            {"id": "KR22-3", "label": "Last Pledge"}
        ],
        "logs": [
            "[2088-09-03 01:40] Silent entry. Paid a fixer for a single-use key.",
            "[2088-09-03 01:46] I run better when I am angry. Bad news: I have been angry for years.",
            "[2088-09-03 02:02] My scanner lies. Some rooms exist, then vanish.",
            "[2088-09-03 02:09] My sister thinks I still carry anonymous packages. I never told her those packages are sometimes evidence.",
            "[2088-09-03 02:19] I got credits, but every terminal raises the pressure.",
            "[2088-09-03 02:25] The CORE broadcasts my old medical record. They know me.",
            "[2088-09-03 02:28] Stupid paradox: stealing credits to erase debt still obeys the logic of accounting.",
            "[2088-09-03 02:33] I keep going. If I get out, my sister can finally sleep debt-free.",
            "[2088-09-03 02:36] Impact. Drone in my blind spot. Splitting this log into 3 ROM fragments."
        ],
        "epilogue": "The debt contract was never found in public archives."
    },
    {
        "id": "ROM-NQ05",
        "title": "NQ05 // Cold Chamber",
        "hacker": "Noor Qassem (they)",
        "bio": "Freelance cryptanalyst specialized in dead memory systems and heritage AIs.",
        "fragments": [
            {"id": "NQ05-1", "label": "Approach Trace"},
            {"id": "NQ05-2", "label": "Interface Rupture"},
            {"id": "NQ05-3", "label": "Core Voice"}
        ],
        "logs": [
            "[2093-02-20 18:05] The walls are cold. Everything here consumes heat like evidence.",
            "[2093-02-20 18:11] A door replayed my own breathing three seconds ahead.",
            "[2093-02-20 18:27] One room returned my reflection with a 4-second lead.",
            "[2093-02-20 18:36] In the server squat we used to say one saved archive can be worth a riot.",
            "[2093-02-20 18:51] Sentinel routines imitate human errors. Bad sign.",
            "[2093-02-20 19:04] I landed a clean hack. Alarm still climbed.",
            "[2093-02-20 19:10] Paradox: I preserve memory fragments while I am no longer sure some memories are mine.",
            "[2093-02-20 19:18] If I fall, someone get these logs out. Let it serve something else.",
            "[2093-02-20 19:21] Contact lost. Locking my story into ROM fragments."
        ],
        "epilogue": "Noor's remaining data is flagged as irreconcilable."
    },
    {
        "id": "ROM-LV77",
        "title": "LV77 // Wild Fork",
        "hacker": "Leia Varek (she)",
        "bio": "Developer from a free-software collective dissolved after a raid.",
        "fragments": [
            {"id": "LV77-1", "label": "Hidden Repo"},
            {"id": "LV77-2", "label": "Branch Conflict"},
            {"id": "LV77-3", "label": "Final Commit"}
        ],
        "logs": [
            "[2090-06-03 00:11] Entry validated. Scanners run on an old Unix base with fresh paint.",
            "[2090-06-03 00:19] Ada used to say a fork is sometimes a breakup written in clean syntax.",
            "[2090-06-03 00:28] I came in to steal a repository that already belonged to me before patenting.",
            "[2090-06-03 00:42] First Sentinel neutralized.",
            "[2090-06-03 00:57] Paradox: I hate monopolies, yet I still hope my code survives under their logo.",
            "[2090-06-03 01:03] If anyone reads this: publishing can be more dangerous than deleting."
        ],
        "epilogue": "The repository was never republished in full."
    },
    {
        "id": "ROM-SM04",
        "title": "SM04 // Silent Zone",
        "hacker": "Sam Mirek (he)",
        "bio": "Former pirate radio technician specialized in underground broadcasts.",
        "fragments": [
            {"id": "SM04-1", "label": "Frequency 1"},
            {"id": "SM04-2", "label": "Frequency 2"},
            {"id": "SM04-3", "label": "Frequency 3"}
        ],
        "logs": [
            "[2087-11-19 03:10] I recognize electric noise before I even spot drones.",
            "[2087-11-19 03:21] A wall speaker replayed my own pirate broadcast from 2084.",
            "[2087-11-19 03:34] My brother used to say speaking too loud always attracts boots.",
            "[2087-11-19 03:41] Paradox: I hack frequencies to free speech, but here every word pins my location.",
            "[2087-11-19 03:52] If I fall, let the noise keep circulating."
        ],
        "epilogue": "No source confirmed Sam's extraction."
    },
    {
        "id": "ROM-IR31",
        "title": "IR31 // Administrative Ash",
        "hacker": "Iris Ren (she)",
        "bio": "Former administrative employee who sabotaged automated evictions.",
        "fragments": [
            {"id": "IR31-1", "label": "Fake File"},
            {"id": "IR31-2", "label": "Inverted Procedure"},
            {"id": "IR31-3", "label": "Ash Archive"}
        ],
        "logs": [
            "[2092-01-08 19:14] I still know the internal menus better than the agents who enforce them.",
            "[2092-01-08 19:25] I already saved one hundred and thirty-two files with deliberate typos.",
            "[2092-01-08 19:39] Here, terminals classify lives like tickets.",
            "[2092-01-08 19:48] Paradox: forging data to restore a bit of justice is still forging.",
            "[2092-01-08 19:56] I keep going."
        ],
        "epilogue": "Internal logs mention a persistent human anomaly."
    },
    {
        "id": "ROM-DX90",
        "title": "DX90 // Dissident Syntax",
        "hacker": "Dax Oren (they)",
        "bio": "Maintainer of an encrypted underground distribution.",
        "fragments": [
            {"id": "DX90-1", "label": "Bootstrap"},
            {"id": "DX90-2", "label": "Kernel Drift"},
            {"id": "DX90-3", "label": "Root Panic"}
        ],
        "logs": [
            "[2094-07-01 21:03] Key injected into the secondary network.",
            "[2094-07-01 21:17] Collective meeting yesterday: two hours debating a package name.",
            "[2094-07-01 21:31] Paradox: we want to abolish hierarchies, yet someone always ends up merging alone.",
            "[2094-07-01 21:44] First shot dodged.",
            "[2094-07-01 21:52] Even revolutions need someone to remind you to eat."
        ],
        "epilogue": "A similar key reappeared later across several free networks."
    },
    {
        "id": "ROM-PT12",
        "title": "PT12 // Ghost Line",
        "hacker": "Pia Torres (she)",
        "bio": "Former autonomous metro driver turned technical saboteur.",
        "fragments": [
            {"id": "PT12-1", "label": "Dead Rail"},
            {"id": "PT12-2", "label": "Bypass"},
            {"id": "PT12-3", "label": "Last Line"}
        ],
        "logs": [
            "[2089-12-14 04:05] The silence here sounds like tunnels before power returns.",
            "[2089-12-14 04:18] I learned to slow systems before I learned to break them.",
            "[2089-12-14 04:29] Paradox: I hate automation, yet I trust my reflexes more than people.",
            "[2089-12-14 04:37] Two drones behind me."
        ],
        "epilogue": "The privatized transport file never resurfaced."
    },
    {
        "id": "ROM-HQ44",
        "title": "HQ44 // Noise Archive",
        "hacker": "Hugo Quent (he)",
        "bio": "Noise musician turned signal pirate.",
        "fragments": [
            {"id": "HQ44-1", "label": "Impulse"},
            {"id": "HQ44-2", "label": "Feedback"},
            {"id": "HQ44-3", "label": "Cut"}
        ],
        "logs": [
            "[2086-03-03 02:14] Every alarm here has almost an exploitable tone.",
            "[2086-03-03 02:27] I count my steps like measures.",
            "[2086-03-03 02:39] Paradox: turning fear into rhythm does not erase it.",
            "[2086-03-03 02:45] I think I hear breathing behind the relays."
        ],
        "epilogue": "An audio extract attributed to Hugo still circulates on pirate networks."
    },
    {
        "id": "ROM-ZE08",
        "title": "ZE08 // Incomplete Commune",
        "hacker": "Zea Elin (she)",
        "bio": "Member of a self-managed urban micro-commune.",
        "fragments": [
            {"id": "ZE08-1", "label": "Collective Kitchen"},
            {"id": "ZE08-2", "label": "Black Meter"},
            {"id": "ZE08-3", "label": "Incomplete Exit"}
        ],
        "logs": [
            "[2095-05-10 23:01] We shared soup before I left.",
            "[2095-05-10 23:14] Energy readings lie exactly like prefects do.",
            "[2095-05-10 23:28] Paradox: living without a boss sometimes demands more discipline than the opposite.",
            "[2095-05-10 23:37] If I come back, I still have to repair the rooftop solar charger."
        ],
        "epilogue": "Zea's district suffered a total blackout two weeks later."
    }
]
TRANSLATIONS["it"]["content.rom_story_archive"] = [
    {
        "id": "ROM-AX13",
        "title": "AX13 // Ultima Deriva",
        "hacker": "Mara Voss (lei)",
        "bio": "Ex ingegnera di rete di Kheiron Dynamics, scomparsa dopo aver tentato di far trapelare codice interno.",
        "fragments": [
            {"id": "AX13-1", "label": "Bootlog Bunker"},
            {"id": "AX13-2", "label": "Diario di Progresso"},
            {"id": "AX13-3", "label": "Segnale Finale"}
        ],
        "logs": [
            "[2091-04-12 22:13] Infiltrazione all'ingresso del livello C. Rumore dei droni piu forte del previsto.",
            "[2091-04-12 22:17] Il portello sente ancora di ozono. Ho progettato questo protocollo sei anni fa. Vederlo riusato qui mi fa vomitare.",
            "[2091-04-12 22:24] Una camera mi ha seguito senza far scattare l'allarme. O sono gia segnalata, o qualcuno sta rallentando il sistema.",
            "[2091-04-12 22:31] Blocco termico neutralizzato. Ho perso il 30% dei miei strumenti.",
            "[2091-04-12 22:38] Lian diceva sempre che finiamo per abitare le strutture che odiamo. Credo avesse ragione.",
            "[2091-04-12 22:49] Ho visto il Sentinel in lontananza. Non e un bot standard. Esita prima di puntare l'ottica su di me.",
            "[2091-04-12 23:02] Allarmi a cascata. I corridoi si riconfigurano in loop.",
            "[2091-04-12 23:05] Paradosso: entro per sabotare questo sistema, ma ogni porta aperta dimostra che il mio vecchio codice regge meglio di me.",
            "[2091-04-12 23:09] Se qualcuno legge questo: non restare mai fermo dopo un hack riuscito.",
            "[2091-04-12 23:11] Sto sanguinando nella tuta. Lascio questo dossier in tre cache ROM."
        ],
        "epilogue": "Fine trasmissione. Il segnale di Mara si interrompe di colpo dopo un sovraccarico di sicurezza."
    },
    {
        "id": "ROM-KR22",
        "title": "KR22 // Debito Rosso",
        "hacker": "Kenji Rault (lui)",
        "bio": "Corriere dati indipendente, infiltrato nella megastruttura per cancellare un contratto di debito.",
        "fragments": [
            {"id": "KR22-1", "label": "Mandato Notturno"},
            {"id": "KR22-2", "label": "Mappa Corrotta"},
            {"id": "KR22-3", "label": "Ultimo Pledge"}
        ],
        "logs": [
            "[2088-09-03 01:40] Ingresso silenzioso. Ho pagato un fixer per una chiave monouso.",
            "[2088-09-03 01:46] Corro meglio quando sono arrabbiato. Brutta notizia: lo sono da anni.",
            "[2088-09-03 02:02] Il mio scanner mente. Alcune stanze esistono, poi scompaiono.",
            "[2088-09-03 02:09] Mia sorella crede che io trasporti ancora pacchi anonimi. Non le ho mai detto che a volte quei pacchi sono prove.",
            "[2088-09-03 02:19] Ho recuperato crediti, ma ogni terminale aumenta la pressione.",
            "[2088-09-03 02:25] Il CORE trasmette la mia vecchia cartella clinica. Mi conoscono.",
            "[2088-09-03 02:28] Paradosso stupido: rubare crediti per cancellare un debito significa obbedire ancora alla logica del conto.",
            "[2088-09-03 02:33] Continuo. Se esco, mia sorella dormira finalmente senza debiti.",
            "[2088-09-03 02:36] Impatto. Drone nel mio angolo cieco. Segmento questo log in 3 frammenti ROM."
        ],
        "epilogue": "Il contratto di debito non e mai stato ritrovato negli archivi pubblici."
    },
    {
        "id": "ROM-NQ05",
        "title": "NQ05 // Camera Fredda",
        "hacker": "Noor Qassem (loro)",
        "bio": "Criptoanalista freelance specializzato in memorie morte e IA patrimoniali.",
        "fragments": [
            {"id": "NQ05-1", "label": "Traccia di Avvicinamento"},
            {"id": "NQ05-2", "label": "Rottura di Interfaccia"},
            {"id": "NQ05-3", "label": "Voce del Nucleo"}
        ],
        "logs": [
            "[2093-02-20 18:05] I muri sono freddi. Qui tutto consuma calore come fossero prove.",
            "[2093-02-20 18:11] Una porta ha riprodotto il mio stesso respiro con tre secondi di anticipo.",
            "[2093-02-20 18:27] Una stanza mi ha restituito il riflesso con 4 secondi di anticipo.",
            "[2093-02-20 18:36] Nel server squat dicevamo che un archivio salvato puo valere una sommossa.",
            "[2093-02-20 18:51] Le routine sentinella imitano errori umani. Brutto segno.",
            "[2093-02-20 19:04] Hack pulito riuscito. L'allarme e comunque salito.",
            "[2093-02-20 19:10] Paradosso: preservo frammenti di memoria mentre non so piu se certi ricordi siano miei.",
            "[2093-02-20 19:18] Se cado, che qualcuno porti fuori questi log. Che servano a qualcos'altro.",
            "[2093-02-20 19:21] Contatto perso. Blocco la mia storia in frammenti ROM."
        ],
        "epilogue": "Il resto dei dati di Noor e marcato come inconciliabile."
    },
    {
        "id": "ROM-LV77",
        "title": "LV77 // Fork Selvaggio",
        "hacker": "Leia Varek (lei)",
        "bio": "Sviluppatrice da un collettivo software libero sciolto dopo una perquisizione.",
        "fragments": [
            {"id": "LV77-1", "label": "Repo Nascosto"},
            {"id": "LV77-2", "label": "Conflitto di Branch"},
            {"id": "LV77-3", "label": "Commit Finale"}
        ],
        "logs": [
            "[2090-06-03 00:11] Ingresso validato. Gli scanner girano su una vecchia base Unix truccata.",
            "[2090-06-03 00:19] Ada diceva che un fork a volte e una rottura sentimentale scritta in sintassi pulita.",
            "[2090-06-03 00:28] Entro per rubare un repository che era gia mio prima dei brevetti.",
            "[2090-06-03 00:42] Primo Sentinel neutralizzato.",
            "[2090-06-03 00:57] Paradosso: odio i monopoli ma spero ancora che il mio codice sopravviva sotto il loro logo.",
            "[2090-06-03 01:03] Se qualcuno legge questo: pubblicare puo essere piu pericoloso che cancellare."
        ],
        "epilogue": "Il repository non e mai stato ripubblicato integralmente."
    },
    {
        "id": "ROM-SM04",
        "title": "SM04 // Zona Muta",
        "hacker": "Sam Mirek (lui)",
        "bio": "Ex tecnico radio pirata specializzato in bollettini clandestini.",
        "fragments": [
            {"id": "SM04-1", "label": "Frequenza 1"},
            {"id": "SM04-2", "label": "Frequenza 2"},
            {"id": "SM04-3", "label": "Frequenza 3"}
        ],
        "logs": [
            "[2087-11-19 03:10] Riconosco i disturbi elettrici prima ancora di vedere i droni.",
            "[2087-11-19 03:21] Un altoparlante a muro ha riprodotto la mia vecchia emissione pirata del 2084.",
            "[2087-11-19 03:34] Mio fratello diceva che parlare troppo forte attira sempre gli stivali.",
            "[2087-11-19 03:41] Paradosso: pirato frequenze per liberare la parola, ma qui ogni parola mi localizza.",
            "[2087-11-19 03:52] Se cado, fate almeno circolare il rumore."
        ],
        "epilogue": "Nessuna fonte ha confermato l'uscita di Sam."
    },
    {
        "id": "ROM-IR31",
        "title": "IR31 // Cenere Amministrativa",
        "hacker": "Iris Ren (lei)",
        "bio": "Ex impiegata amministrativa che ha sabotato sfratti automatizzati.",
        "fragments": [
            {"id": "IR31-1", "label": "Dossier Falso"},
            {"id": "IR31-2", "label": "Procedura Inversa"},
            {"id": "IR31-3", "label": "Archivio Cenere"}
        ],
        "logs": [
            "[2092-01-08 19:14] Conosco ancora i menu interni meglio degli agenti che li applicano.",
            "[2092-01-08 19:25] Ho gia salvato centotrentadue fascicoli con semplici errori volontari.",
            "[2092-01-08 19:39] Qui i terminali classificano le vite come ticket.",
            "[2092-01-08 19:48] Paradosso: falsificare per ristabilire un po' di giustizia resta comunque falsificare.",
            "[2092-01-08 19:56] Continuo."
        ],
        "epilogue": "I log interni citano un'anomalia umana persistente."
    },
    {
        "id": "ROM-DX90",
        "title": "DX90 // Sintassi Dissidente",
        "hacker": "Dax Oren (loro)",
        "bio": "Maintainer di una distribuzione clandestina cifrata.",
        "fragments": [
            {"id": "DX90-1", "label": "Bootstrap"},
            {"id": "DX90-2", "label": "Kernel Drift"},
            {"id": "DX90-3", "label": "Root Panic"}
        ],
        "logs": [
            "[2094-07-01 21:03] Chiave iniettata nella rete secondaria.",
            "[2094-07-01 21:17] Riunione collettiva ieri: due ore per discutere il nome di un pacchetto.",
            "[2094-07-01 21:31] Paradosso: vogliamo abolire le gerarchie ma alla fine qualcuno mergea sempre da solo.",
            "[2094-07-01 21:44] Primo colpo evitato.",
            "[2094-07-01 21:52] Anche le rivoluzioni hanno bisogno di qualcuno che ti ricordi di mangiare."
        ],
        "epilogue": "Una chiave simile e riapparsa piu tardi su varie reti libere."
    },
    {
        "id": "ROM-PT12",
        "title": "PT12 // Linea Fantasma",
        "hacker": "Pia Torres (lei)",
        "bio": "Ex conducente di metro autonoma diventata sabotatrice tecnica.",
        "fragments": [
            {"id": "PT12-1", "label": "Binario Morto"},
            {"id": "PT12-2", "label": "Bypass"},
            {"id": "PT12-3", "label": "Ultima Linea"}
        ],
        "logs": [
            "[2089-12-14 04:05] Il silenzio qui assomiglia ai tunnel prima del ritorno di tensione.",
            "[2089-12-14 04:18] Ho imparato a rallentare i sistemi prima di imparare a romperli.",
            "[2089-12-14 04:29] Paradosso: odio gli automatismi ma mi fido dei miei riflessi piu che delle persone.",
            "[2089-12-14 04:37] Due droni dietro di me."
        ],
        "epilogue": "Il dossier sui trasporti privatizzati non e mai riemerso."
    },
    {
        "id": "ROM-HQ44",
        "title": "HQ44 // Archivio di Rumore",
        "hacker": "Hugo Quent (lui)",
        "bio": "Musicista noise diventato pirata di segnali.",
        "fragments": [
            {"id": "HQ44-1", "label": "Impulso"},
            {"id": "HQ44-2", "label": "Feedback"},
            {"id": "HQ44-3", "label": "Taglio"}
        ],
        "logs": [
            "[2086-03-03 02:14] Ogni allarme qui ha quasi una tonalita sfruttabile.",
            "[2086-03-03 02:27] Conto i passi come battute.",
            "[2086-03-03 02:39] Paradosso: trasformare la paura in ritmo non la annulla.",
            "[2086-03-03 02:45] Credo di sentire un respiro dietro i rele."
        ],
        "epilogue": "Un estratto audio attribuito a Hugo circola ancora in alcune reti pirata."
    },
    {
        "id": "ROM-ZE08",
        "title": "ZE08 // Comune Incompleta",
        "hacker": "Zea Elin (lei)",
        "bio": "Membro di una micro-comune urbana autogestita.",
        "fragments": [
            {"id": "ZE08-1", "label": "Cucina Collettiva"},
            {"id": "ZE08-2", "label": "Contatore Nero"},
            {"id": "ZE08-3", "label": "Uscita Incompleta"}
        ],
        "logs": [
            "[2095-05-10 23:01] Abbiamo condiviso la zuppa prima della mia partenza.",
            "[2095-05-10 23:14] Le letture energetiche mentono esattamente come i prefetti.",
            "[2095-05-10 23:28] Paradosso: vivere senza capi a volte richiede piu disciplina del contrario.",
            "[2095-05-10 23:37] Se torno, dovro ancora riparare il caricatore solare sul tetto."
        ],
        "epilogue": "Il quartiere di Zea ha subito un blackout totale due settimane dopo."
    }
]
TRANSLATIONS["es"]["content.rom_story_archive"] = [
    {
        "id": "ROM-AX13",
        "title": "AX13 // Ultima Deriva",
        "hacker": "Mara Voss (ella)",
        "bio": "Ex ingeniera de red de Kheiron Dynamics, desaparecida tras intentar filtrar codigo interno.",
        "fragments": [
            {"id": "AX13-1", "label": "Bootlog de Bunker"},
            {"id": "AX13-2", "label": "Diario de Progreso"},
            {"id": "AX13-3", "label": "Senal Final"}
        ],
        "logs": [
            "[2091-04-12 22:13] Infiltracion por acceso de nivel C. El ruido de drones es mas alto de lo previsto.",
            "[2091-04-12 22:17] La compuerta sigue oliendo a ozono. Disene este protocolo hace seis anos. Verlo aqui me revuelve el estomago.",
            "[2091-04-12 22:24] Una camara me siguio sin disparar alerta. O ya estoy marcada o alguien frena el sistema.",
            "[2091-04-12 22:31] Bloqueo termico neutralizado. Perdi el 30% de mis herramientas.",
            "[2091-04-12 22:38] Lian decia que acabamos viviendo dentro de las estructuras que odiamos. Creo que tenia razon.",
            "[2091-04-12 22:49] Vi al Sentinel a distancia. No es un bot estandar. Duda antes de fijar la optica sobre mi.",
            "[2091-04-12 23:02] Alarmas en cascada. Los pasillos se reconfiguran en bucle.",
            "[2091-04-12 23:05] Paradoja: entre para sabotear este sistema, pero cada puerta abierta demuestra que mi codigo viejo resiste mas que yo.",
            "[2091-04-12 23:09] Si alguien lee esto: no te quedes quieto despues de un hack exitoso.",
            "[2091-04-12 23:11] Estoy sangrando dentro del traje. Dejo este expediente dividido en tres caches ROM."
        ],
        "epilogue": "Fin de transmision. La senal de Mara se corta de golpe tras una sobrecarga de seguridad."
    },
    {
        "id": "ROM-KR22",
        "title": "KR22 // Deuda Roja",
        "hacker": "Kenji Rault (el)",
        "bio": "Mensajero de datos independiente, infiltrado en la megaestructura para borrar un contrato de deuda.",
        "fragments": [
            {"id": "KR22-1", "label": "Mandato Nocturno"},
            {"id": "KR22-2", "label": "Mapa Corrupto"},
            {"id": "KR22-3", "label": "Ultimo Pledge"}
        ],
        "logs": [
            "[2088-09-03 01:40] Entrada silenciosa. Pague a un fixer por una llave de un solo uso.",
            "[2088-09-03 01:46] Corro mejor cuando estoy enojado. Mala noticia: llevo anos asi.",
            "[2088-09-03 02:02] Mi escaner miente. Algunas salas existen y luego desaparecen.",
            "[2088-09-03 02:09] Mi hermana cree que aun reparto paquetes anonimos. Nunca le dije que a veces esos paquetes son pruebas.",
            "[2088-09-03 02:19] Recupere creditos, pero cada terminal sube la presion.",
            "[2088-09-03 02:25] El CORE transmite mi antiguo historial clinico. Me conocen.",
            "[2088-09-03 02:28] Paradoja absurda: robar creditos para borrar deuda sigue obedeciendo la logica de la cuenta.",
            "[2088-09-03 02:33] Sigo. Si salgo, mi hermana podra dormir sin deudas.",
            "[2088-09-03 02:36] Impacto. Drone en mi angulo ciego. Segmento este log en 3 fragmentos ROM."
        ],
        "epilogue": "El contrato de deuda nunca aparecio en archivos publicos."
    },
    {
        "id": "ROM-NQ05",
        "title": "NQ05 // Camara Fria",
        "hacker": "Noor Qassem (elle)",
        "bio": "Criptoanalista freelance especializado en memorias muertas e IA patrimoniales.",
        "fragments": [
            {"id": "NQ05-1", "label": "Rastro de Aproximacion"},
            {"id": "NQ05-2", "label": "Ruptura de Interfaz"},
            {"id": "NQ05-3", "label": "Voz del Nucleo"}
        ],
        "logs": [
            "[2093-02-20 18:05] Las paredes estan frias. Todo aqui consume calor como si fueran pruebas.",
            "[2093-02-20 18:11] Una puerta reprodujo mi propia respiracion con tres segundos de adelanto.",
            "[2093-02-20 18:27] Una sala devolvio mi reflejo con 4 segundos de anticipacion.",
            "[2093-02-20 18:36] En el squat de servidores deciamos que un archivo salvado podia valer una revuelta.",
            "[2093-02-20 18:51] Las rutinas sentinel imitan errores humanos. Mala senal.",
            "[2093-02-20 19:04] Hack limpio completado. Aun asi la alerta subio.",
            "[2093-02-20 19:10] Paradoja: preservo fragmentos de memoria mientras ya no se si ciertos recuerdos son mios.",
            "[2093-02-20 19:18] Si caigo, que alguien saque estos logs. Que sirvan para algo mas.",
            "[2093-02-20 19:21] Contacto perdido. Encierro mi historia en fragmentos ROM."
        ],
        "epilogue": "El resto de los datos de Noor figura como irreconciliable."
    },
    {
        "id": "ROM-LV77",
        "title": "LV77 // Fork Salvaje",
        "hacker": "Leia Varek (ella)",
        "bio": "Desarrolladora de un colectivo de software libre disuelto tras una redada.",
        "fragments": [
            {"id": "LV77-1", "label": "Repo Oculto"},
            {"id": "LV77-2", "label": "Conflicto de Rama"},
            {"id": "LV77-3", "label": "Commit Final"}
        ],
        "logs": [
            "[2090-06-03 00:11] Entrada validada. Los escaneres corren sobre una base Unix antigua parcheada.",
            "[2090-06-03 00:19] Ada decia que un fork a veces es una ruptura sentimental escrita en sintaxis limpia.",
            "[2090-06-03 00:28] Entro para robar un repositorio que ya era mio antes de las patentes.",
            "[2090-06-03 00:42] Primer Sentinel neutralizado.",
            "[2090-06-03 00:57] Paradoja: odio los monopolios pero aun quiero que mi codigo sobreviva bajo su logo.",
            "[2090-06-03 01:03] Si alguien lee esto: publicar puede ser mas peligroso que borrar."
        ],
        "epilogue": "El repositorio nunca fue republicado de forma integra."
    },
    {
        "id": "ROM-SM04",
        "title": "SM04 // Zona Muda",
        "hacker": "Sam Mirek (el)",
        "bio": "Ex tecnico de radio pirata especializado en boletines clandestinos.",
        "fragments": [
            {"id": "SM04-1", "label": "Frecuencia 1"},
            {"id": "SM04-2", "label": "Frecuencia 2"},
            {"id": "SM04-3", "label": "Frecuencia 3"}
        ],
        "logs": [
            "[2087-11-19 03:10] Reconozco la interferencia electrica antes de ver los drones.",
            "[2087-11-19 03:21] Un altavoz mural reprodujo mi vieja emision pirata de 2084.",
            "[2087-11-19 03:34] Mi hermano decia que hablar demasiado alto siempre atrae botas.",
            "[2087-11-19 03:41] Paradoja: pirateo frecuencias para liberar la palabra, pero aqui cada palabra me localiza.",
            "[2087-11-19 03:52] Si caigo, al menos hagan circular el ruido."
        ],
        "epilogue": "Ninguna fuente confirmo la salida de Sam."
    },
    {
        "id": "ROM-IR31",
        "title": "IR31 // Ceniza Administrativa",
        "hacker": "Iris Ren (ella)",
        "bio": "Ex administrativa que saboteo desalojos automatizados.",
        "fragments": [
            {"id": "IR31-1", "label": "Expediente Falso"},
            {"id": "IR31-2", "label": "Procedimiento Inverso"},
            {"id": "IR31-3", "label": "Archivo Ceniza"}
        ],
        "logs": [
            "[2092-01-08 19:14] Aun conozco los menus internos mejor que los agentes que los aplican.",
            "[2092-01-08 19:25] Ya salve ciento treinta y dos expedientes con simples errores voluntarios.",
            "[2092-01-08 19:39] Aqui los terminales clasifican vidas como tickets.",
            "[2092-01-08 19:48] Paradoja: falsificar para restaurar un poco de justicia sigue siendo falsificar.",
            "[2092-01-08 19:56] Sigo."
        ],
        "epilogue": "Los logs internos mencionan una anomalia humana persistente."
    },
    {
        "id": "ROM-DX90",
        "title": "DX90 // Sintaxis Disidente",
        "hacker": "Dax Oren (elle)",
        "bio": "Maintainer de una distribucion clandestina cifrada.",
        "fragments": [
            {"id": "DX90-1", "label": "Bootstrap"},
            {"id": "DX90-2", "label": "Kernel Drift"},
            {"id": "DX90-3", "label": "Root Panic"}
        ],
        "logs": [
            "[2094-07-01 21:03] Clave inyectada en la red secundaria.",
            "[2094-07-01 21:17] Asamblea colectiva ayer: dos horas para discutir el nombre de un paquete.",
            "[2094-07-01 21:31] Paradoja: queremos abolir jerarquias, pero al final alguien siempre hace merge en solitario.",
            "[2094-07-01 21:44] Primer impacto evitado.",
            "[2094-07-01 21:52] Incluso las revoluciones necesitan a alguien que te recuerde comer."
        ],
        "epilogue": "Una clave parecida reaparecio despues en varias redes libres."
    },
    {
        "id": "ROM-PT12",
        "title": "PT12 // Linea Fantasma",
        "hacker": "Pia Torres (ella)",
        "bio": "Ex conductora de metro autonomo convertida en saboteadora tecnica.",
        "fragments": [
            {"id": "PT12-1", "label": "Via Muerta"},
            {"id": "PT12-2", "label": "Bypass"},
            {"id": "PT12-3", "label": "Ultima Linea"}
        ],
        "logs": [
            "[2089-12-14 04:05] El silencio aqui se parece a los tuneles antes de que vuelva la tension.",
            "[2089-12-14 04:18] Aprendi a frenar sistemas antes de aprender a romperlos.",
            "[2089-12-14 04:29] Paradoja: odio los automatismos pero confio mas en mis reflejos que en las personas.",
            "[2089-12-14 04:37] Dos drones detras de mi."
        ],
        "epilogue": "El expediente de transportes privatizados nunca volvio a aparecer."
    },
    {
        "id": "ROM-HQ44",
        "title": "HQ44 // Archivo de Ruido",
        "hacker": "Hugo Quent (el)",
        "bio": "Musico noise convertido en pirata de senal.",
        "fragments": [
            {"id": "HQ44-1", "label": "Impulso"},
            {"id": "HQ44-2", "label": "Feedback"},
            {"id": "HQ44-3", "label": "Corte"}
        ],
        "logs": [
            "[2086-03-03 02:14] Cada alarma aqui tiene casi una tonalidad utilizable.",
            "[2086-03-03 02:27] Cuento pasos como compases.",
            "[2086-03-03 02:39] Paradoja: convertir el miedo en ritmo no lo cancela.",
            "[2086-03-03 02:45] Creo que escucho respiracion detras de los reles."
        ],
        "epilogue": "Un extracto de audio atribuido a Hugo aun circula por algunas redes pirata."
    },
    {
        "id": "ROM-ZE08",
        "title": "ZE08 // Comuna Incompleta",
        "hacker": "Zea Elin (ella)",
        "bio": "Miembro de una micro-comuna urbana autogestionada.",
        "fragments": [
            {"id": "ZE08-1", "label": "Cocina Colectiva"},
            {"id": "ZE08-2", "label": "Contador Negro"},
            {"id": "ZE08-3", "label": "Salida Incompleta"}
        ],
        "logs": [
            "[2095-05-10 23:01] Compartimos sopa antes de mi salida.",
            "[2095-05-10 23:14] Las lecturas energeticas mienten igual que los prefectos.",
            "[2095-05-10 23:28] Paradoja: vivir sin jefes a veces exige mas disciplina que lo contrario.",
            "[2095-05-10 23:37] Si vuelvo, aun tendre que reparar el cargador solar de la azotea."
        ],
        "epilogue": "El barrio de Zea sufrio un apagon total dos semanas despues."
    }
]
TRANSLATIONS["en"]["content.room_descriptions"] = [
    "Corridor saturated with red neon.",
    "Server room humming with thermal relays.",
    "Abandoned technical zone covered in cables.",
    "Old security checkpoint.",
    "Narrow passage with a flickering broken sign.",
    "Room flooded with intermittent electrical noise.",
    "Control room with failing holographic displays.",
    "Ventilation tunnel full of rusted ducts.",
    "Abandoned lab with strange medical equipment.",
    "Empty hangar echoing with distant sounds.",
    "Executive office with destroyed high-tech furniture.",
    "Storage zone stacked with data crates.",
    "Meeting room with a broken interactive table.",
    "Access corridor to blocked elevators.",
    "Maintenance zone with scattered tools."
]
TRANSLATIONS["it"]["content.room_descriptions"] = [
    "Corridoio saturo di neon rossi.",
    "Sala server dove ronzano relè termici.",
    "Zona tecnica abbandonata coperta di cavi.",
    "Vecchio checkpoint di sicurezza.",
    "Passaggio stretto con insegna rotta lampeggiante.",
    "Sala immersa in rumore elettrico intermittente.",
    "Sala di controllo con schermi olografici in avaria.",
    "Tunnel di ventilazione pieno di condotti arrugginiti.",
    "Laboratorio abbandonato con strane attrezzature mediche.",
    "Hangar vuoto che risuona di echi lontani.",
    "Ufficio dirigenziale con arredi high-tech distrutti.",
    "Zona di stoccaggio con casse dati impilate.",
    "Sala riunioni con tavolo interattivo rotto.",
    "Corridoio d'accesso agli ascensori bloccati.",
    "Zona manutenzione con attrezzi sparsi."
]
TRANSLATIONS["es"]["content.room_descriptions"] = [
    "Pasillo saturado de neones rojos.",
    "Sala de servidores donde zumban relés térmicos.",
    "Zona tecnica abandonada cubierta de cables.",
    "Antiguo control de seguridad.",
    "Paso estrecho con un letrero roto parpadeante.",
    "Sala inundada por ruido electrico intermitente.",
    "Sala de control con pantallas holograficas defectuosas.",
    "Tunel de ventilacion lleno de conductos oxidados.",
    "Laboratorio abandonado con extranos equipos medicos.",
    "Hangar vacio que resuena con ecos lejanos.",
    "Oficina ejecutiva con mobiliario tecnologico destruido.",
    "Zona de almacen con cajas de datos apiladas.",
    "Sala de reuniones con mesa interactiva rota.",
    "Pasillo de acceso a ascensores bloqueados.",
    "Zona de mantenimiento con herramientas esparcidas."
]
TRANSLATIONS["en"]["content.enemies"] = ["Drone", "Guard", "Sentry Bot", "Proxy Hunter"]
TRANSLATIONS["it"]["content.enemies"] = ["Drone", "Guardia", "Bot Sentinella", "Cacciatore Proxy"]
TRANSLATIONS["es"]["content.enemies"] = ["Dron", "Guardia", "Bot Centinela", "Cazador Proxy"]
TRANSLATIONS["en"]["content.items"] = ITEMS
TRANSLATIONS["it"]["content.items"] = ITEMS
TRANSLATIONS["es"]["content.items"] = ITEMS

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
    print("\n" + tr("language.title"))
    print(tr("language.subtitle"))
    for code in SUPPORTED_LANGUAGES:
        print(tr("language.option", code=code, name=LANGUAGE_LABELS[code]))

    while True:
        choice = input(tr("language.prompt")).strip().lower()
        if choice in SUPPORTED_LANGUAGES:
            CURRENT_LANGUAGE = choice
            print(tr("language.selected", code=choice, name=LANGUAGE_LABELS[choice]))
            return
        print(tr("language.invalid"))


def round_int(value):
    if value >= 0:
        return int(value + 0.5)
    return int(value - 0.5)


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
        loot_choice = input(tr("hack.loot.prompt")).strip().upper()

        if loot_choice == 'B':
            player['hp'] += 25
            print(tr("hack.loot.heal"))
        elif loot_choice == 'C':
            player['hack'] += 5
            print(tr("hack.loot.upgrade"))
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


def save_score(status="QUIT"):
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



def core_check():
    room = current_room()
    if room.core and not room.enemy and player['core_hacked']:
        print("\n" + tr("core.pirated"))
        save_score(status="GAGNE")
        return True
    return False


def main():
    choose_language()
    print(tr("startup.launching"))
    global world, player, player_name, core_x, core_y, HACK_TIME, COMBAT_TIME, REFLEX_TIME, DIFFICULTY_MULTIPLIER
    player_name = input(tr("startup.player_name_prompt")).strip() or "ANON"
    print(tr("startup.player_name_echo", name=player_name))
    
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
            save_score(status="PERDU")
            break
        if player['alarm'] >= 5:
            print(tr("main.alarm_game_over"))
            save_score(status="PERDU")
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
                save_score(status='QUIT')
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
