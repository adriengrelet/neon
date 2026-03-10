#!/usr/bin/env python3
# Language dictionary extracted from neon.py

TRANSLATIONS_FR = {'language.title': '=== CHOIX DE LANGUE ===',
 'language.subtitle': 'Codes disponibles :',
 'language.option': '- {code} : {name}',
 'language.prompt': 'Langue (fr/en/it/es) > ',
 'language.selected': 'Langue active : {code} ({name})',
 'language.invalid': 'Code invalide. Utilise fr, en, it, es.',
 'statusline.compact': 'HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3',
 'leaderboard.title': '=== LEADERBOARD ===',
 'leaderboard.entry': '#{idx} {line}',
 'leaderboard.none': 'Aucun score enregistré.',
 'intro.press_enter': 'Appuie sur Entree pour commencer...',
 'startup.launching': 'Lancement du jeu...',
 'startup.player_name_prompt': 'Nom du joueur : ',
 'startup.player_name_echo': 'Joueur: {name}',
 'startup.difficulty_title': '=== SELECTION DIFFICULTE ===',
 'startup.difficulty_1': '1. Balade cyber   - Hack : 60s  Combat : 10s  Reflexe : 6s  Multiplicateur de points : 1x',
 'startup.difficulty_2': '2. Epreuve cyber  - Hack : 45s  Combat : 6s   Reflexe : 4s  Multiplicateur de points : 2x',
 'startup.difficulty_3': '3. Transpiration cyber - Hack : 30s  Combat : 4s   Reflexe : 2s  Multiplicateur de points : '
                         '3x',
 'startup.difficulty_4': '4. Violence cyber - Hack : 20s  Combat : 3s   Reflexe : 3s  Multiplicateur de points : 4x',
 'startup.difficulty_prompt': 'Choisir le niveau (1-4) : ',
 'startup.difficulty_invalid': 'Niveau invalide, difficulte 3 selectionnee par defaut.',
 'map.title': '=== MAP ===',
 'map.legend': 'Légende: P=Player | C=Core | .=Salle visitée | E=Ennemi | L=Loot | F=Fragment | M=Multi | #=Inconnue',
 'describe.enemy_present': '⚠ Ennemi présent : {enemy}',
 'describe.core_hp': 'HP du CORE Sentinel : {hp}',
 'describe.locked': '🔒 Salle verrouillée.',
 'describe.terminal': '💻 Terminal détecté.',
 'describe.item_visible': '📦 Objet visible : {item}',
 'describe.fragment_visible': '🧩 Fragment ROM detecte : {fragment_id}',
 'describe.core_detected': '===== ☢ CORE CENTRAL détecté ! =====',
 'move.locked_exit': '🔒 Impossible de sortir : verrouillage actif.',
 'move.wall': 'Mur structurel.',
 'scan.title': '=== SCAN PROFOND ===',
 'scan.cost': 'Coût énergétique du scan : {cost}',
 'scan.object_found': 'Objet caché détecté : {item}',
 'scan.lock_pulse': 'Le verrouillage pulse à fréquence variable.',
 'scan.ports_open': "Ports d'intrusion encore ouverts.",
 'scan.rom_signature': 'Signature ROM fragmentaire detectee dans la salle.',
 'scan.nothing': 'Rien de nouveau détecté.',
 'echo.title': '=== ECHO ETENDU ===',
 'echo.cost': "Coût énergétique de l'echo : {cost}",
 'echo.detected': 'Signatures détectées autour de toi : {count}',
 'echo.none': 'Aucune signature tactique détectée autour de toi.',
 'story.title': '=== DOSSIER ROM DECHIFFRE ===',
 'story.id': 'ID: {id}',
 'story.name': 'Titre: {title}',
 'story.hacker': 'Hacker: {hacker}',
 'story.context': 'Contexte: {context}',
 'story.logs': '--- LOGS ---',
 'story.epilogue': '--- EPILOGUE ---',
 'fragments.title': '=== FRAGMENTS ROM ===',
 'fragments.count': 'Collecte: {found}/{total}',
 'fragments.line': '[{mark}] {id} - {label}',
 'fragments.unlocked': 'Acces au dossier narratif complet debloque.',
 'fragments.read_prompt': "Lire l'histoire maintenant ? (y/n) ",
 'fragments.incomplete': "Recupere les 3 fragments pour dechiffrer l'histoire complete.",
 'hack.matrix.title': "=== MATRICE D'INTRUSION ===",
 'hack.matrix.sequence': 'Séquence cible : {sequence}',
 'hack.matrix.rules': 'Étape 1 libre | Étape 2 même colonne | Étape 3 même ligne',
 'hack.matrix.step_prompt': 'Étape {step} > ',
 'hack.matrix.timeout': 'Temps dépassé',
 'hack.matrix.incorrect': 'Code incorrect',
 'hack.matrix.same_column': 'Même colonne requise',
 'hack.matrix.same_row': 'Même ligne requise',
 'core_hint.east': "INDICE : Le core est à l'est.",
 'core_hint.west': "INDICE : Le core est à l'ouest.",
 'core_hint.south': 'INDICE : Le core est au sud.',
 'core_hint.north': 'INDICE : Le core est au nord.',
 'hack.blocked_core': "Le CORE est protégé. Neutralise d'abord l'ennemi présent.",
 'hack.nothing': 'Rien à pirater ici.',
 'hack.title': '=== HACK ===',
 'hack.cost': 'Coût énergétique : {cost}',
 'hack.alarm_triggered': '⚠ Attention Alarme niveau {alarm} enclenchée !',
 'hack.alarm_enemy': "🚨 Ennemi d'alarme déployé dans cette salle !",
 'hack.reduced': 'Hack réduit à {hack}',
 'hack.standard_success': '💻 Hack standard réussi. Choix du loot :',
 'hack.fragment_ping': '🛰️ Intel terminal : signatures ROM repérées sur la carte ({count}).',
 'hack.fragment_ping_none': 'Intel terminal : aucune signature ROM inconnue à révéler.',
 'hack.loot.a': 'A. Crédits',
 'hack.loot.b': 'B. Soin neurocyber (+25 HP)',
 'hack.loot.c': 'C. Upgrade hack (+5 HK)',
 'hack.loot.d': 'D. Soin cybernétique (+10 HP)',
 'hack.loot.prompt': 'Loot > ',
 'hack.loot.heal': '🧠 Soin appliqué : +25 HP',
 'hack.loot.upgrade': '⚙ Upgrade hack appliqué : +5 HK',
 'hack.loot.cyber_heal': '⚕️ Soin cybernétique appliqué : +10 HP',
 'hack.loot.credits': '💰 Loot crédits obtenu : +{credits}',
 'hack.success.credits': '💻 Hack réussi ! +{credits} crédits',
 'hack.alarm_reduced': 'Alarme réduite de 1.',
 'hack.unlock_room': '🔓 Salle déverrouillée.',
 'hack.core_pirated': '☢ CORE piraté. Extraction possible.',
 'hack.done_ms': 'Hack réalisé en {ms} ms',
 'attack.no_target': 'Aucune cible.',
 'attack.stance.aggressive': "L'ennemi charge avec agressivité, prêt à frapper fort.",
 'attack.stance.defensive': "L'ennemi se retranche derrière des défenses solides.",
 'attack.stance.unstable': "L'ennemi bouge de manière erratique et imprévisible.",
 'attack.prompt': 'Combat : A frontal | B feinte | C surcharge (choix en {time}s)',
 'attack.choice_prompt': 'Choix > ',
 'attack.timeout': 'Temps de réaction trop long : action de combat automatisée aléatoire.',
 'attack.reflex_prompt': '⚡ Réflexe : tape {char} vite',
 'attack.reflex.success': 'Réussi en {ms} ms ! Bonus : dégâts réduits.',
 'attack.reflex.failure': 'Échec en {ms} ms ! Malus : dégâts augmentés.',
 'attack.bonus.surcharge': 'Augmentation surcharge activée : dégâts réduits !',
 'attack.bonus.force': 'Augmentation force activée : dégâts réduits !',
 'attack.bonus.vitesse': 'Augmentation vitesse activée : dégâts réduits !',
 'attack.core.hit': 'Tu attaques le CORE Sentinel ! Dégâts : {damage}',
 'attack.core.hp': 'HP du CORE Sentinel : {hp}',
 'attack.core.counter': 'Le CORE Sentinel contre-attaque ! Tu encaisses {damage} dégâts.',
 'attack.core.neutralized': 'CORE Sentinel neutralisé !',
 'attack.core.remaining_hack': 'Le Sentinel est tombé, mais il reste à hacker le CORE.',
 'attack.neutralize': 'Tu neutralises {enemy}',
 'attack.taken': 'Tu encaisses {damage} dégâts',
 'enemy_attack.core': "⚠️ Le CORE Sentinel t'attaque ! Tu encaisses {damage} dégâts.",
 'enemy_attack.normal': "⚠️ {enemy} t'attaque ! Tu encaisses {damage} dégâts.",
 'take.fragment': 'Fragment ROM recupere : {fragment_id} ({count}/3)',
 'take.item': 'Pris : {item}',
 'take.none': 'Rien à prendre.',
 'use.absent': 'Objet absent.',
 'use.used': '{item} utilisé.',
 'inventory.title': 'Inventaire :',
 'inventory.empty': 'Vide',
 'inventory.medkit': '- medkit : restaure 25 HP',
 'inventory.energy_cell': '- energy_cell : restaure 25 énergie',
 'inventory.exploit_chip': '- exploit_chip : +10 hack',
 'status.title': '=== MATERIEL AUGMENTE ===',
 'status.synaptique': '- Augmentation synaptique : +10s au temps de hack',
 'status.surcharge': '- Augmentation surcharge : améliore surcharge en combat',
 'status.interface': '- Interface neuronale hacker augmentée : matrice réduite de 1',
 'status.combat_chip': "- Chip de combat : double le temps d'action en combat",
 'status.force': '- Augmentation force : améliore attaque frontale en combat',
 'status.vitesse': '- Augmentation vitesse : améliore feinte en combat',
 'status.dissipateur': '- Dissipateur énergétique : divise par 2 les coûts en énergie des actions',
 'status.none': 'Aucun',
 'status.characteristics': '=== CARACTERISTIQUES ===',
 'status.line': 'HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}',
 'status.fragments': 'Fragments ROM: {count}/3',
 'help.commands': 'Commandes : n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <objet> | '
                  'inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q',
 'shop.title': '=== MAGASIN ===',
 'shop.credits': 'Crédits disponibles : {credits}',
 'shop.items': 'Items disponibles :',
 'shop.item.1': '1. Augmentation synaptique - 100 crédits : +10s au temps de hack',
 'shop.item.2': '2. Augmentation surcharge - 100 crédits : améliore surcharge en combat',
 'shop.item.3': '3. Interface neuronale hacker augmentée - 150 crédits : matrice réduite de 1',
 'shop.item.4': '4. Chip de combat - 150 crédits : double le temps pour agir en combat',
 'shop.item.5': '5. Augmentation force - 100 crédits : améliore attaque frontale en combat',
 'shop.item.6': '6. Augmentation vitesse - 100 crédits : améliore feinte en combat',
 'shop.item.7': '7. Dissipateur énergétique - 300 crédits : divise par 2 les coûts en EN des actions',
 'shop.item.0': '0. Quitter',
 'shop.prompt': 'Choix > ',
 'shop.buy.1': 'Augmentation synaptique achetée ! +10s au temps de hack.',
 'shop.buy.2': 'Augmentation surcharge achetée ! Surcharge améliorée en combat.',
 'shop.buy.3': 'Interface neuronale achetée ! Matrice réduite de 1.',
 'shop.buy.4': 'Chip de combat acheté ! Temps de combat doublé.',
 'shop.buy.5': 'Augmentation force achetée ! Attaque frontale améliorée.',
 'shop.buy.6': 'Augmentation vitesse achetée ! Feinte améliorée.',
 'shop.buy.7': 'Dissipateur énergétique acheté ! Les coûts EN des actions sont divisés par 2.',
 'shop.invalid': 'Choix invalide ou insuffisant de crédits.',
 'enemy_turn.reinforcement': '⚠ Renfort système détecté',
 'score.title': '=== SCORE FINAL ===',
 'score.base': 'Score de base: {score}',
 'score.rom_bonus': 'Bonus fragments ROM: {bonus}',
 'score.time_bonus': 'Bonus temps total: {bonus}',
 'score.hack_bonus': 'Bonus temps hack: {bonus}',
 'score.rank': 'Votre score vous classe #{rank}.',
 'core.pirated': '=== CORE PIRATÉ ===',
 'main.spawn': 'spawn position {x},{y}',
 'main.core': 'core position {x},{y}',
 'main.story_channel': 'Canal ROM detecte: dossier {story_id} fragmente en 3 caches.',
 'main.death': 'Tu tombes dans le réseau.',
 'main.alarm_game_over': '🚨 Alarme maximale atteinte ! Game over.',
 'ui.choice_prompt': 'Choix > ',
 'ui.reflex_input_prompt': '> ',
 'ui.command_prompt': '\n> ',
 'ui.quit_confirm': 'Voulez-vous quitter la partie en cours ? (y/n) ',
 'ui.replay_prompt': 'Rejouer ? (y/n) ',
 'ui.unknown_command': 'Commande inconnue.',
 'error.unhandled': 'Une erreur est survenue : {error}',
 'intro.full': '\n'
               '==============================\n'
               '        NEON NODE v6\n'
               '==============================\n'
               '\n'
               'Infiltre la mégastructure.\n'
               'Atteins le CORE central, pirate-le, et ressors vivant.\n'
               '\n'
               'Pour les hacks :\n'
               '- Plus ton hack est élevé, plus la matrice est petite.\n'
               '- Étape 1 : libre de trouver la bonne valeur hexa dans la matrice (qui doit correspondre à la première '
               'valeur du code demandé).\n'
               "- Étape 2 : doit être dans la même colonne que l'étape 1.\n"
               "- Étape 3 : doit être dans la même ligne que l'étape 2.\n"
               '\n'
               'Le temps est limité pour réussir le hack, et échouer augmente ton alarme et réduit ton hack.\n'
               '\n'
               'Des crédits sont gagnés en piratant des terminaux, et peuvent être utilisés pour acheter des '
               'améliorations dans le shop.\n'
               'Plus tu hackes vite, plus tu gagnes de crédits !\n'
               '\n'
               'Commandes :\n'
               ' north / n : se déplacer vers le nord\n'
               ' south / s : se déplacer vers le sud\n'
               " east / e : se déplacer vers l'est\n"
               " west / w  : se déplacer vers l'ouest\n"
               ' scan / sc : scanner la salle pour trouver des objets cachés ou des indices\n'
               ' echo / ec : sonder les salles autour de toi et révéler des marqueurs tactiques sur la carte\n'
               ' hack / h : tenter de pirater un terminal ou de désactiver un verrouillage\n'
               ' attack : engager le combat contre un ennemi présent\n'
               ' take / t : ramasser un objet visible dans la salle ou découvert en scan\n'
               " use <objet> / u <objet> : utiliser un objet de l'inventaire (ex: use medkit)\n"
               ' map / m : afficher la carte du niveau (P = position, C = core, . = salle visitée, # = salle non '
               'visitée)\n'
               " inventory / inv : afficher l'inventaire\n"
               ' status / stat : afficher le statut et les améliorations\n'
               ' fragments / fra : afficher les fragments ROM collectés et le dossier narratif\n'
               ' shop / sh : accéder au magasin pour acheter des améliorations avec les crédits\n'
               ' help / he : afficher les commandes\n'
               ' quit / q : quitter le jeu\n',
 'content.room_descriptions': ['Couloir saturé de néons rouges.',
                               'Salle serveur où bourdonnent des relais thermiques.',
                               'Zone technique abandonnée couverte de câbles.',
                               'Ancien checkpoint de sécurité.',
                               'Passage étroit où clignote une enseigne cassée.',
                               'Salle noyée dans un bruit électrique intermittent.',
                               'Salle de contrôle avec écrans holographiques défaillants.',
                               'Tunnel de ventilation rempli de conduits rouillés.',
                               'Laboratoire abandonné avec équipements médicaux étranges.',
                               "Hangar vide résonnant d'échos lointains.",
                               'Bureau exécutif avec mobilier high-tech détruit.',
                               'Zone de stockage avec caisses de données empilées.',
                               'Salle de réunion avec table interactive brisée.',
                               "Couloir d'accès aux ascenseurs bloqués.",
                               'Zone de maintenance avec outils éparpillés.'],
 'content.enemies': ['Drone', 'Guard', 'Sentry Bot', 'Proxy Hunter'],
 'content.items': ['medkit', 'energy_cell', 'exploit_chip'],
 'content.rom_story_archive': [{'id': 'ROM-AX13',
                                'title': 'AX13 // Derniere Derive',
                                'hacker': 'Mara Voss (elle)',
                                'bio': 'Ex-ingenieure reseau de Kheiron Dynamics, disparue apres avoir tente de faire '
                                       'fuiter du code interne.',
                                'fragments': [{'id': 'AX13-1', 'label': 'Bootlog Bunker'},
                                              {'id': 'AX13-2', 'label': 'Journal de Progression'},
                                              {'id': 'AX13-3', 'label': 'Signal de Fin'}],
                                'logs': ['[2091-04-12 22:13] Infiltration entree niveau C. Bruit des drones plus fort '
                                         'que prevu.',
                                         "[2091-04-12 22:17] Le sas sent toujours l'ozone. J'avais dessine ce "
                                         'protocole il y a six ans. Le voir reutilise ici donne envie de vomir.',
                                         "[2091-04-12 22:24] Une camera m'a suivie sans declencher d'alerte. Soit je "
                                         "suis deja referencee, soit quelqu'un ralentit le systeme.",
                                         "[2091-04-12 22:31] Verrouillage thermique neutralise. J'ai perdu 30% de mes "
                                         'outils.',
                                         "[2091-04-12 22:38] Lian disait toujours qu'on finit par habiter les "
                                         "structures qu'on deteste. Je crois qu'elle avait raison.",
                                         "[2091-04-12 22:49] J'ai vu le sentinel au loin. Ce n'est pas un bot "
                                         'standard. Il hesite avant de tourner son optique vers moi.',
                                         '[2091-04-12 23:02] Alarmes en cascade. Les couloirs se reconfigurent en '
                                         'boucle.',
                                         "[2091-04-12 23:05] Paradoxe: j'entre pour saboter ce systeme, mais chaque "
                                         'porte ouverte prouve que mon ancien code tient encore mieux que moi.',
                                         "[2091-04-12 23:09] Si quelqu'un lit ca: ne reste jamais immobile apres un "
                                         'hack reussi.',
                                         '[2091-04-12 23:11] Je saigne dans ma combinaison. Je laisse ce dossier dans '
                                         'trois caches ROM.'],
                                'epilogue': 'Fin de transmission. Le signal de Mara coupe net apres une surcharge de '
                                            'securite.'},
                               {'id': 'ROM-KR22',
                                'title': 'KR22 // Dette Rouge',
                                'hacker': 'Kenji Rault (il)',
                                'bio': 'Courrier de donnees indep, infiltrait la megastructure pour effacer un contrat '
                                       'de dette.',
                                'fragments': [{'id': 'KR22-1', 'label': 'Mandat Nocturne'},
                                              {'id': 'KR22-2', 'label': 'Map Corrompue'},
                                              {'id': 'KR22-3', 'label': 'Dernier Pledge'}],
                                'logs': ["[2088-09-03 01:40] Entree silencieuse. J'ai paye un fixeur pour une cle "
                                         'monousage.',
                                         '[2088-09-03 01:46] Je cours mieux quand je suis en colere. Mauvaise '
                                         'nouvelle: je suis en colere depuis des annees.',
                                         '[2088-09-03 02:02] Mon scanner ment. Certaines salles existent puis '
                                         'disparaissent.',
                                         '[2088-09-03 02:09] Ma soeur croit que je transporte encore des colis '
                                         "anonymes. Je n'ai jamais ose lui dire que parfois les colis sont des "
                                         'preuves.',
                                         "[2088-09-03 02:19] J'ai recupere des credits, mais chaque terminal augmente "
                                         'la pression.',
                                         '[2088-09-03 02:25] Le CORE diffuse mon ancien dossier medical. Ils me '
                                         'connaissent.',
                                         '[2088-09-03 02:28] Paradoxe idiot: voler des credits pour effacer une dette, '
                                         "c'est encore obeir a la logique du compte.",
                                         '[2088-09-03 02:33] Je continue. Si je sors, ma soeur dort enfin sans dette.',
                                         '[2088-09-03 02:36] Impact. Drone dans mon angle mort. Je segmente le journal '
                                         'en 3 ROM.'],
                                'epilogue': "Le contrat de dette n'a jamais ete retrouve dans les archives publiques."},
                               {'id': 'ROM-NQ05',
                                'title': 'NQ05 // Chambre Froide',
                                'hacker': 'Noor Qassem (iel)',
                                'bio': 'Cryptanalyste freelance specialise dans les memoires mortes et les IA '
                                       'patrimoniales.',
                                'fragments': [{'id': 'NQ05-1', 'label': "Trace d'Approche"},
                                              {'id': 'NQ05-2', 'label': "Rupture d'Interface"},
                                              {'id': 'NQ05-3', 'label': 'Voix du Noyau'}],
                                'logs': ['[2093-02-20 18:05] Les murs sont froids. Tout ici consomme la chaleur comme '
                                         'des preuves.',
                                         '[2093-02-20 18:11] Une porte a rejoue ma propre respiration avec trois '
                                         "secondes d'avance.",
                                         "[2093-02-20 18:27] Une salle m'a rendu mon propre reflet avec 4 secondes "
                                         "d'avance.",
                                         "[2093-02-20 18:36] Dans le squat serveur on disait qu'une archive sauvee "
                                         'vaut parfois une emeute.',
                                         '[2093-02-20 18:51] Les routines sentinelles miment des erreurs humaines. '
                                         'Mauvais signe.',
                                         "[2093-02-20 19:04] J'ai reussi un hack propre. L'alarme est quand meme "
                                         'montee.',
                                         '[2093-02-20 19:10] Paradoxe: je preserve des fragments de memoire alors que '
                                         'je ne sais meme plus si certains souvenirs sont a moi.',
                                         "[2093-02-20 19:18] Si je tombe, que quelqu'un sorte ces logs. Que ca serve a "
                                         'autre chose.',
                                         '[2093-02-20 19:21] Contact perdu. Je verrouille mon histoire en fragments '
                                         'ROM.'],
                                'epilogue': 'Le reste des donnees de Noor est marque comme irreconciliable.'},
                               {'id': 'ROM-LV77',
                                'title': 'LV77 // Fork Sauvage',
                                'hacker': 'Leia Varek (elle)',
                                'bio': "Developpeuse issue d'un collectif logiciel libre dissous apres perquisition.",
                                'fragments': [{'id': 'LV77-1', 'label': 'Depot Cache'},
                                              {'id': 'LV77-2', 'label': 'Conflit de Branche'},
                                              {'id': 'LV77-3', 'label': 'Commit Final'}],
                                'logs': ['[2090-06-03 00:11] Entree validee. Les scanners tournent sur une vieille '
                                         'base Unix maquillee.',
                                         "[2090-06-03 00:19] Ada disait qu'un fork est parfois une rupture amoureuse "
                                         'en syntaxe propre.',
                                         "[2090-06-03 00:28] J'entre pour voler un depot qui m'appartenait deja avant "
                                         'brevetage.',
                                         '[2090-06-03 00:42] Premier sentinel neutralise.',
                                         "[2090-06-03 00:57] Paradoxe: je hais les monopoles mais j'espere encore que "
                                         'mon code survive sous leur logo.',
                                         "[2090-06-03 01:03] Si quelqu'un lit ceci: publier reste parfois plus "
                                         "dangereux qu'effacer."],
                                'epilogue': "Le depot n'a jamais ete republie integralement."},
                               {'id': 'ROM-SM04',
                                'title': 'SM04 // Zone Muette',
                                'hacker': 'Sam Mirek (il)',
                                'bio': 'Ancien technicien radio pirate specialise dans les bulletins clandestins.',
                                'fragments': [{'id': 'SM04-1', 'label': 'Frequence 1'},
                                              {'id': 'SM04-2', 'label': 'Frequence 2'},
                                              {'id': 'SM04-3', 'label': 'Frequence 3'}],
                                'logs': ['[2087-11-19 03:10] Je reconnais les parasites electriques avant meme les '
                                         'drones.',
                                         '[2087-11-19 03:21] Une enceinte murale rejoue ma propre emission pirate de '
                                         '2084.',
                                         '[2087-11-19 03:34] Mon frere disait que parler trop fort finit toujours par '
                                         'attirer des bottes.',
                                         '[2087-11-19 03:41] Paradoxe: je pirate des frequences pour liberer la '
                                         'parole, mais ici chaque mot me localise.',
                                         '[2087-11-19 03:52] Si je tombe, laissez au moins le bruit circuler.'],
                                'epilogue': "Aucune source n'a confirme la sortie de Sam."},
                               {'id': 'ROM-IR31',
                                'title': 'IR31 // Cendre Administrative',
                                'hacker': 'Iris Ren (elle)',
                                'bio': 'Ex-employee administrative ayant sabote des expulsions automatisees.',
                                'fragments': [{'id': 'IR31-1', 'label': 'Dossier Faux'},
                                              {'id': 'IR31-2', 'label': 'Procedure Inverse'},
                                              {'id': 'IR31-3', 'label': 'Archive Cendre'}],
                                'logs': ['[2092-01-08 19:14] Je connais encore les menus internes mieux que les agents '
                                         'qui les appliquent.',
                                         "[2092-01-08 19:25] J'ai deja sauve cent trente-deux dossiers avec de simples "
                                         'fautes volontaires.',
                                         '[2092-01-08 19:39] Ici les terminaux classent les vies comme des tickets.',
                                         '[2092-01-08 19:48] Paradoxe: falsifier pour retablir un peu de justice reste '
                                         'quand meme falsifier.',
                                         '[2092-01-08 19:56] Je continue.'],
                                'epilogue': 'Les journaux internes mentionnent une anomalie humaine persistante.'},
                               {'id': 'ROM-DX90',
                                'title': 'DX90 // Syntaxe Dissidente',
                                'hacker': 'Dax Oren (iel)',
                                'bio': "Mainteneur d'une distribution clandestine chiffree.",
                                'fragments': [{'id': 'DX90-1', 'label': 'Bootstrap'},
                                              {'id': 'DX90-2', 'label': 'Kernel Drift'},
                                              {'id': 'DX90-3', 'label': 'Root Panic'}],
                                'logs': ['[2094-07-01 21:03] Cle injectee dans le reseau secondaire.',
                                         "[2094-07-01 21:17] Reunion collective hier: deux heures pour debattre d'un "
                                         'nom de paquet.',
                                         '[2094-07-01 21:31] Paradoxe: nous voulons abolir les hierarchies mais '
                                         "quelqu'un finit toujours par merger seul.",
                                         '[2094-07-01 21:44] Premier tir evite.',
                                         "[2094-07-01 21:52] Meme les revolutions ont besoin de quelqu'un qui pense a "
                                         'te rappeler de manger.'],
                                'epilogue': 'Une cle similaire a reapparu plus tard sur plusieurs reseaux libres.'},
                               {'id': 'ROM-PT12',
                                'title': 'PT12 // Ligne Fantome',
                                'hacker': 'Pia Torres (elle)',
                                'bio': 'Ancienne conductrice de metro autonome devenue saboteuse technique.',
                                'fragments': [{'id': 'PT12-1', 'label': 'Rail Mort'},
                                              {'id': 'PT12-2', 'label': 'Bypass'},
                                              {'id': 'PT12-3', 'label': 'Derniere Ligne'}],
                                'logs': ['[2089-12-14 04:05] Le silence ici ressemble aux tunnels avant remise sous '
                                         'tension.',
                                         "[2089-12-14 04:18] J'ai appris a ralentir les systemes avant d'apprendre a "
                                         'les casser.',
                                         '[2089-12-14 04:29] Paradoxe: je hais les automatismes mais je fais confiance '
                                         "a mes reflexes plus qu'aux gens.",
                                         '[2089-12-14 04:37] Deux drones derriere moi.'],
                                'epilogue': "Le dossier des transports privatise n'a jamais refait surface."},
                               {'id': 'ROM-HQ44',
                                'title': 'HQ44 // Archive de Bruit',
                                'hacker': 'Hugo Quent (il)',
                                'bio': 'Musicien noise devenu pirate de signaux.',
                                'fragments': [{'id': 'HQ44-1', 'label': 'Impulse'},
                                              {'id': 'HQ44-2', 'label': 'Feedback'},
                                              {'id': 'HQ44-3', 'label': 'Cut'}],
                                'logs': ['[2086-03-03 02:14] Chaque alarme ici a presque une tonalite exploitable.',
                                         '[2086-03-03 02:27] Je compte mes pas comme des mesures.',
                                         "[2086-03-03 02:39] Paradoxe: transformer la peur en rythme ne l'annule pas.",
                                         '[2086-03-03 02:45] Je crois entendre un souffle derriere les relais.'],
                                'epilogue': 'Un extrait audio attribue a Hugo circule encore dans certains reseaux '
                                            'pirates.'},
                               {'id': 'ROM-ZE08',
                                'title': 'ZE08 // Commune Incomplete',
                                'hacker': 'Zea Elin (elle)',
                                'bio': "Membre d'une micro-commune urbaine autogeree.",
                                'fragments': [{'id': 'ZE08-1', 'label': 'Cuisine Collective'},
                                              {'id': 'ZE08-2', 'label': 'Compteur Noir'},
                                              {'id': 'ZE08-3', 'label': 'Sortie Incomplete'}],
                                'logs': ['[2095-05-10 23:01] On a partage la soupe avant mon depart.',
                                         '[2095-05-10 23:14] Les relevés energetiques mentent exactement comme les '
                                         'prefets.',
                                         '[2095-05-10 23:28] Paradoxe: vivre sans chef demande parfois plus de '
                                         "discipline que l'inverse.",
                                         '[2095-05-10 23:37] Si je reviens, il faudra encore reparer le chargeur '
                                         'solaire du toit.'],
                                'epilogue': 'Le quartier de Zea a subi une coupure totale deux semaines plus tard.'}]}
