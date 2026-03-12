import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(BASE_DIR, "lang")

MEGASTRUCTURES_FILES = {
    "fr": os.path.join(LANG_DIR, "megastructures_fr.json"),
    "en": os.path.join(LANG_DIR, "megastructures_en.json"),
    "es": os.path.join(LANG_DIR, "megastructures_es.json"),
    "it": os.path.join(LANG_DIR, "megastructures_it.json"),
}

BASE_WORLD_RULES = {
    "enemy_chance": 0.30,
    "locked_chance": 0.25,
    "terminal_chance": 0.25,
    "item_chance": 0.20,
    "scan_item_discovery_chance": 0.35,
    "energy_cost_scale": 1.0,
    "core_enemy_hp": 75,
    "alarm_reinforcement_chance": 0.25,
    "alarm_step": 1,
    "alarm_reinforcement_threshold": 4,
    "alarm_max": 5,
}

MAIL_TEMPLATES = [
    {
        "sender": "NODE-HERMES",
        "contact": "HX-11",
        "subject": "Alerte prioritaire: forte presence de gardes",
        "body": "La nouvelle megastructure est deja sous protection active. Attends-toi a des contacts hostiles frequents et a tres peu de secondes gratuites.",
        "starter_credits": 180,
        "starter_items": ["medkit", "energy_cell"],
        "modifiers": {"enemy_chance": 0.42},
    },
    {
        "sender": "SIGMA LIAISON",
        "contact": "SL-09",
        "subject": "Canal rouge: architecture verrouillee",
        "body": "Le batiment est segmente par des verrous hack superposes. Ne pars pas sans reserves ni sans une idee claire de ta sortie.",
        "starter_credits": 220,
        "starter_items": ["energy_cell"],
        "modifiers": {"locked_chance": 0.40, "terminal_chance": 0.30},
    },
    {
        "sender": "CROW-NET",
        "contact": "CR-88",
        "subject": "Interception: alerte en propagation acceleree",
        "body": "Les noeuds de surveillance relaient les alertes tres vite. Chaque erreur coutera plus cher et reviendra te retrouver plus tot.",
        "starter_credits": 200,
        "starter_items": ["medkit"],
        "modifiers": {"alarm_step": 2, "alarm_reinforcement_threshold": 3, "alarm_max": 4},
    },
    {
        "sender": "AZUR PROXY",
        "contact": "AZ-01",
        "subject": "Briefing: zone pauvre en loot",
        "body": "Peu d'objets recuperables sur place. Compense via la boutique avant insertion et ne compte pas sur la chance pour te reequiper.",
        "starter_credits": 260,
        "starter_items": ["medkit", "medkit"],
        "modifiers": {"item_chance": 0.10},
    },
    {
        "sender": "BLACK TRACE",
        "contact": "BT-404",
        "subject": "Dossier terrain: couloirs terminalises",
        "body": "Beaucoup de terminaux exposes et de verrous associes. Profil ideal pour un specialiste hack capable de rester calme sous minuterie hostile.",
        "starter_credits": 200,
        "starter_items": ["energy_cell", "energy_cell"],
        "modifiers": {"terminal_chance": 0.38, "locked_chance": 0.35},
    },
    {
        "sender": "MERCURY HAND",
        "contact": "MH-73",
        "subject": "Fenetre d'infiltration courte",
        "body": "On te reserve un slot d'entree limite. Le coeur devra tomber vite, avant que la structure n'apprenne ton rythme.",
        "starter_credits": 170,
        "starter_items": ["medkit"],
        "modifiers": {
            "enemy_chance": 0.36,
            "alarm_step": 2,
            "alarm_reinforcement_threshold": 3,
            "alarm_reinforcement_chance": 0.35,
            "alarm_max": 4,
        },
    },
    {
        "sender": "ECHO-DELTA",
        "contact": "ED-12",
        "subject": "Message compile: noyau partiellement nu",
        "body": "La securite de surface est agressive, mais quelques couloirs techniques restent ouverts a ceux qui lisent mieux les batiments que les panneaux.",
        "starter_credits": 210,
        "starter_items": ["energy_cell"],
        "modifiers": {
            "enemy_chance": 0.38,
            "terminal_chance": 0.32,
            "locked_chance": 0.20,
            "core_enemy_hp": 68,
        },
    },
    {
        "sender": "NIGHT COURRIER",
        "contact": "NC-57",
        "subject": "Priorite civique: droits numeriques en jeu",
        "body": "Une nouvelle megastructure vient d'etre detectee. Si elle passe en production, des quartiers entiers perdront leurs droits d'acces sans meme comprendre quand la coupure aura commence.",
        "starter_credits": 240,
        "starter_items": ["medkit", "energy_cell"],
        "modifiers": {"locked_chance": 0.34, "alarm_step": 2},
    },
    {
        "sender": "ARCHIVE NULL",
        "contact": "AN-00",
        "subject": "Trame tactique: patrouilles aleatoires",
        "body": "Les gardes changent leurs rondes sans motif lisible. Prepare des options offensives, defensives et surtout une bonne excuse de repli.",
        "starter_credits": 190,
        "starter_items": ["medkit"],
        "modifiers": {"enemy_chance": 0.40, "alarm_reinforcement_chance": 0.38},
    },
    {
        "sender": "FREELINE",
        "contact": "FL-33",
        "subject": "Signal public: infiltration recommandee",
        "body": "Tu restes notre meilleur point d'entree pour cette cible. Si cette structure tombe, plusieurs circuits civils recupereront un peu d'air avant la prochaine compression.",
        "starter_credits": 230,
        "starter_items": ["energy_cell", "medkit"],
        "modifiers": {"terminal_chance": 0.33, "item_chance": 0.16},
    },
    {
        "sender": "POLAR SECTOR",
        "contact": "PS-20",
        "subject": "Surcharge energetique probable",
        "body": "Les lignes d'alimentation sont instables. Chaque action active peut couter plus d'energie que prevu, et le batiment ne remboursera rien.",
        "starter_credits": 260,
        "starter_items": ["energy_cell", "energy_cell", "medkit"],
        "modifiers": {"energy_cost_scale": 1.35, "terminal_chance": 0.35},
    },
    {
        "sender": "WARDEN LEAK",
        "contact": "WL-66",
        "subject": "Noyau Sentinel renforce",
        "body": "La cellule centrale signale un CORE Sentinel renforce. L'engagement final sera plus dur et probablement moins propre que prevu.",
        "starter_credits": 280,
        "starter_items": ["medkit", "medkit", "energy_cell"],
        "modifiers": {"core_enemy_hp": 110, "enemy_chance": 0.34},
    },
    {
        "sender": "DEEP CARTO",
        "contact": "DC-05",
        "subject": "Caches objets detectes",
        "body": "La cartographie interne indique des depots utilitaires hors circuit. Si tu lis bien les angles morts, le scan devrait etre rentable.",
        "starter_credits": 170,
        "starter_items": ["medkit"],
        "modifiers": {"item_chance": 0.30, "scan_item_discovery_chance": 0.50},
    },
    {
        "sender": "LOCKSPINE",
        "contact": "LS-44",
        "subject": "Superposition de verrous neurocryptes",
        "body": "Les couloirs critiques sont fortement verrouilles, mais la densite des patrouilles baisse. Le batiment prefere te ralentir plutot que te poursuivre.",
        "starter_credits": 240,
        "starter_items": ["energy_cell", "energy_cell"],
        "modifiers": {"locked_chance": 0.48, "enemy_chance": 0.22, "terminal_chance": 0.33},
    },
    {
        "sender": "RED SPARK",
        "contact": "RS-91",
        "subject": "Propagation tactique des renforts",
        "body": "Le systeme de renfort repond vite aux anomalies. Evite les echecs successifs, ou la structure transformera ton erreur en habitude exploitable.",
        "starter_credits": 250,
        "starter_items": ["medkit", "energy_cell"],
        "modifiers": {
            "alarm_step": 2,
            "alarm_reinforcement_threshold": 2,
            "alarm_reinforcement_chance": 0.45,
            "alarm_max": 4,
        },
    },
]

MAIL_TEMPLATE_TRANSLATIONS = {
    "en": {
        "NODE-HERMES": {
            "subject": "Priority alert: high guard presence",
            "body": "The new megastructure is already under active protection. Expect frequent hostile contact and very few free seconds.",
        },
        "SIGMA LIAISON": {
            "subject": "Red channel: locked architecture",
            "body": "The building is segmented by stacked hack locks. Do not deploy without reserves or without a clear exit plan.",
        },
        "CROW-NET": {
            "subject": "Intercept: accelerated alert propagation",
            "body": "Surveillance nodes relay alerts very quickly. Every mistake will cost more and circle back to you sooner.",
        },
        "AZUR PROXY": {
            "subject": "Briefing: low-loot zone",
            "body": "There is very little recoverable gear on site. Compensate at the shop before insertion and do not count on luck to re-equip you.",
        },
        "BLACK TRACE": {
            "subject": "Field file: terminal-heavy corridors",
            "body": "Many exposed terminals and linked locks. Ideal profile for a hack specialist who can stay calm under a hostile timer.",
        },
        "MERCURY HAND": {
            "subject": "Short infiltration window",
            "body": "Your entry slot is limited. The core has to fall fast, before the structure learns your rhythm.",
        },
        "ECHO-DELTA": {
            "subject": "Compiled signal: partially exposed core",
            "body": "Surface security is aggressive, but a few technical corridors remain open to people who read buildings better than signage.",
        },
        "NIGHT COURRIER": {
            "subject": "Civic priority: digital rights at risk",
            "body": "A new megastructure has been detected. If it goes live, entire districts will lose access rights without even knowing when the cutoff began.",
        },
        "ARCHIVE NULL": {
            "subject": "Tactical frame: random patrols",
            "body": "Guards rotate with no readable pattern. Prepare offensive options, defensive options, and above all a convincing fallback story.",
        },
        "FREELINE": {
            "subject": "Public signal: infiltration recommended",
            "body": "You remain our best point of entry for this target. If this structure falls, several civilian circuits will get a little breathing room before the next compression.",
        },
        "POLAR SECTOR": {
            "subject": "Likely energy overload",
            "body": "Power lines are unstable. Every active action may cost more energy than expected, and the building will not refund any of it.",
        },
        "WARDEN LEAK": {
            "subject": "Reinforced Sentinel core",
            "body": "The central cell reports a reinforced CORE Sentinel. The final engagement will be harder and probably dirtier than planned.",
        },
        "DEEP CARTO": {
            "subject": "Utility caches detected",
            "body": "Internal mapping points to off-grid utility depots. If you read the blind spots correctly, the scan should pay off.",
        },
        "LOCKSPINE": {
            "subject": "Neuro-crypt lock stacking",
            "body": "Critical corridors are heavily locked, but patrol density drops. The building would rather slow you down than chase you.",
        },
        "RED SPARK": {
            "subject": "Tactical reinforcement propagation",
            "body": "Reinforcement systems react fast to anomalies. Avoid chained failures, or the structure will turn your mistake into an exploitable habit.",
        },
    },
    "es": {
        "NODE-HERMES": {
            "subject": "Alerta prioritaria: alta presencia de guardias",
            "body": "La nueva megastructura ya esta bajo proteccion activa. Espera contactos hostiles frecuentes y muy pocos segundos gratuitos.",
        },
        "SIGMA LIAISON": {
            "subject": "Canal rojo: arquitectura bloqueada",
            "body": "El edificio esta segmentado por bloqueos hack superpuestos. No entres sin reservas ni sin una salida pensada con claridad.",
        },
        "CROW-NET": {
            "subject": "Intercepcion: propagacion acelerada de alerta",
            "body": "Los nodos de vigilancia retransmiten alertas muy rapido. Cada error costara mas y volvera a encontrarte antes.",
        },
        "AZUR PROXY": {
            "subject": "Briefing: zona con poco loot",
            "body": "Hay poco equipo recuperable en sitio. Compensalo en la tienda antes de entrar y no cuentes con la suerte para rearmarte.",
        },
        "BLACK TRACE": {
            "subject": "Dossier de campo: corredores con terminales",
            "body": "Hay muchos terminales expuestos y bloqueos asociados. Perfil ideal para un especialista hack capaz de mantenerse frio bajo cronometro hostil.",
        },
        "MERCURY HAND": {
            "subject": "Ventana de infiltracion corta",
            "body": "Tu ventana de entrada es limitada. El core debe caer rapido, antes de que la estructura aprenda tu ritmo.",
        },
        "ECHO-DELTA": {
            "subject": "Senal compilada: nucleo parcialmente expuesto",
            "body": "La seguridad de superficie es agresiva, pero algunos corredores tecnicos siguen abiertos para quien lee mejor los edificios que los letreros.",
        },
        "NIGHT COURRIER": {
            "subject": "Prioridad civica: derechos digitales en riesgo",
            "body": "Se detecto una nueva megastructura. Si entra en produccion, barrios enteros perderan derechos de acceso sin siquiera entender cuando empezo el corte.",
        },
        "ARCHIVE NULL": {
            "subject": "Trama tactica: patrullas aleatorias",
            "body": "Los guardias cambian sus rondas sin patron legible. Prepara opciones ofensivas, defensivas y, sobre todo, una excusa decente para retirarte.",
        },
        "FREELINE": {
            "subject": "Senal publica: infiltracion recomendada",
            "body": "Sigues siendo nuestro mejor punto de entrada para este objetivo. Si esta estructura cae, varios circuitos civiles recuperaran un poco de aire antes de la siguiente compresion.",
        },
        "POLAR SECTOR": {
            "subject": "Posible sobrecarga energetica",
            "body": "Las lineas de energia son inestables. Cada accion activa puede costar mas energia de la prevista, y el edificio no devolvera nada.",
        },
        "WARDEN LEAK": {
            "subject": "Nucleo Sentinel reforzado",
            "body": "La celda central reporta un CORE Sentinel reforzado. El enfrentamiento final sera mas duro y probablemente menos limpio de lo esperado.",
        },
        "DEEP CARTO": {
            "subject": "Caches utilitarios detectados",
            "body": "El mapeo interno indica depositos utilitarios fuera de red. Si lees bien los angulos muertos, el scan deberia rendir.",
        },
        "LOCKSPINE": {
            "subject": "Superposicion de bloqueos neurocripticos",
            "body": "Los corredores criticos estan muy bloqueados, pero la densidad de patrulla baja. El edificio prefiere frenarte antes que perseguirte.",
        },
        "RED SPARK": {
            "subject": "Propagacion tactica de refuerzos",
            "body": "El sistema de refuerzos responde rapido a las anomalias. Evita los fallos consecutivos, o la estructura convertira tu error en una costumbre explotable.",
        },
    },
    "it": {
        "NODE-HERMES": {
            "subject": "Allerta prioritaria: alta presenza di guardie",
            "body": "La nuova megastruttura e gia sotto protezione attiva. Aspettati contatti ostili frequenti e pochissimi secondi gratuiti.",
        },
        "SIGMA LIAISON": {
            "subject": "Canale rosso: architettura bloccata",
            "body": "L'edificio e segmentato da blocchi hack sovrapposti. Non entrare senza riserve e senza un'idea chiara della via d'uscita.",
        },
        "CROW-NET": {
            "subject": "Intercettazione: propagazione allarmi accelerata",
            "body": "I nodi di sorveglianza rilanciano gli allarmi molto in fretta. Ogni errore costera di piu e tornera a cercarti prima.",
        },
        "AZUR PROXY": {
            "subject": "Briefing: area povera di loot",
            "body": "C'e pochissimo equipaggiamento recuperabile sul posto. Compensa nel negozio prima dell'inserzione e non contare sulla fortuna per riequipaggiarti.",
        },
        "BLACK TRACE": {
            "subject": "Dossier operativo: corridoi pieni di terminali",
            "body": "Molti terminali esposti e blocchi associati. Profilo ideale per uno specialista hack capace di restare lucido sotto un timer ostile.",
        },
        "MERCURY HAND": {
            "subject": "Finestra di infiltrazione breve",
            "body": "Lo slot di ingresso e limitato. Il core deve cadere in fretta, prima che la struttura impari il tuo ritmo.",
        },
        "ECHO-DELTA": {
            "subject": "Segnale compilato: nucleo parzialmente esposto",
            "body": "La sicurezza di superficie e aggressiva, ma alcuni corridoi tecnici restano aperti a chi sa leggere un edificio meglio della segnaletica.",
        },
        "NIGHT COURRIER": {
            "subject": "Priorita civica: diritti digitali a rischio",
            "body": "Una nuova megastruttura e stata rilevata. Se entra in produzione, interi quartieri perderanno diritti di accesso senza nemmeno capire quando e cominciato il taglio.",
        },
        "ARCHIVE NULL": {
            "subject": "Schema tattico: pattuglie casuali",
            "body": "Le guardie cambiano giro senza uno schema leggibile. Prepara opzioni offensive, difensive e soprattutto una buona ragione per ritirarti.",
        },
        "FREELINE": {
            "subject": "Segnale pubblico: infiltrazione raccomandata",
            "body": "Resti il nostro miglior punto di ingresso per questo bersaglio. Se questa struttura cade, diversi circuiti civili recupereranno un po di respiro prima della prossima compressione.",
        },
        "POLAR SECTOR": {
            "subject": "Probabile sovraccarico energetico",
            "body": "Le linee di alimentazione sono instabili. Ogni azione attiva puo costare piu energia del previsto, e l'edificio non rimborsera niente.",
        },
        "WARDEN LEAK": {
            "subject": "Nucleo Sentinel rinforzato",
            "body": "La cella centrale segnala un CORE Sentinel rinforzato. Lo scontro finale sara piu duro e probabilmente meno pulito del previsto.",
        },
        "DEEP CARTO": {
            "subject": "Cache utilitarie rilevate",
            "body": "La mappatura interna mostra depositi utilitari fuori rete. Se leggi bene gli angoli ciechi, lo scan dovrebbe rendere.",
        },
        "LOCKSPINE": {
            "subject": "Sovrapposizione di blocchi neuro-criptati",
            "body": "I corridoi critici sono fortemente bloccati, ma la densita delle pattuglie cala. L'edificio preferisce rallentarti piuttosto che inseguirti.",
        },
        "RED SPARK": {
            "subject": "Propagazione tattica dei rinforzi",
            "body": "Il sistema di rinforzi reagisce rapidamente alle anomalie. Evita fallimenti in catena, o la struttura trasformera il tuo errore in un'abitudine sfruttabile.",
        },
    },
}


def clamp(value, low, high):
    return max(low, min(high, value))


def load_megastructures(language="fr"):
    lang = (language or "fr").strip().lower()
    candidates = []

    lang_file = MEGASTRUCTURES_FILES.get(lang)
    if lang_file:
        candidates.append(lang_file)
    if MEGASTRUCTURES_FILES["fr"] not in candidates:
        candidates.append(MEGASTRUCTURES_FILES["fr"])
    candidates.append(os.path.join(LANG_DIR, "megastructures.json"))
    candidates.append(os.path.join(BASE_DIR, "megastructures.json"))

    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            return data
    return []


def _find_structure_by_id(structures, structure_id):
    for structure in structures:
        if structure.get("id") == structure_id:
            return structure
    return None


def choose_structure_for_run(profile, structures):
    if not structures:
        return None

    preferred = None
    if profile:
        preferred = profile.get("next_structure_id")
    if preferred:
        found = _find_structure_by_id(structures, preferred)
        if found:
            return found

    return random.choice(structures)


def _random_2097_timestamp():
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"2097-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"


def build_briefing_mail(player_name, structure, tr, language="fr"):
    template = random.choice(MAIL_TEMPLATES)
    lang = (language or "fr").strip().lower()
    localized = MAIL_TEMPLATE_TRANSLATIONS.get(lang, {}).get(template["sender"], {})
    subject_base = localized.get("subject", template["subject"])
    body = localized.get("body", template["body"])
    mission_id = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"
    timestamp = _random_2097_timestamp()
    subject = f"{subject_base} [{structure.get('id', 'UNKNOWN')}]"

    lines = [
        f"{tr('quest.mail.from')}: {template['sender']} <{template['contact']}>",
        f"{tr('quest.mail.to')}: {player_name}",
        f"{tr('quest.mail.timestamp')}: {timestamp}",
        f"{tr('quest.mail.subject')}: {subject}",
        "",
        tr("quest.mail.greeting", player_name=player_name),
        body,
        tr(
            "quest.mail.target",
            title=structure.get("title", "Unknown Megastructure"),
            structure_id=structure.get("id", "N/A"),
        ),
        tr("quest.mail.objective"),
        "",
        tr("quest.mail.starter.title"),
        tr("quest.mail.starter.credits", credits=template["starter_credits"]),
        tr(
            "quest.mail.starter.items",
            items=", ".join(template["starter_items"]) if template["starter_items"] else tr("quest.mail.none"),
        ),
        "",
        tr("quest.mail.reply"),
        f"{tr('quest.mail.mission_id')}: {mission_id}",
    ]

    return {
        "mission_id": mission_id,
        "timestamp": timestamp,
        "subject": subject,
        "sender": template["sender"],
        "contact": template["contact"],
        "starter_credits": int(template["starter_credits"]),
        "starter_items": list(template["starter_items"]),
        "modifiers": dict(template["modifiers"]),
        "text": "\n".join(lines),
    }


def _console_root(language):
    lang = language if language in ("fr", "en", "es", "it") else "fr"
    return f"console_{lang}"


def copy_mail_to_console(language, mail_data):
    root = _console_root(language)
    mail_dir = os.path.join(root, "mail")
    os.makedirs(mail_dir, exist_ok=True)
    file_name = f"qmail_{mail_data['mission_id']}.txt"
    path = os.path.join(mail_dir, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(mail_data["text"] + "\n")
    return path


def copy_discovery_to_console(language, current_structure, next_structure, tr):
    root = _console_root(language)
    missions_dir = os.path.join(root, "missions")
    os.makedirs(missions_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"discovery_{stamp}.txt"
    path = os.path.join(missions_dir, file_name)

    lines = [
        tr("quest.discovery.file.completed", structure_id=current_structure.get("id", "UNKNOWN")),
        tr("quest.discovery.file.cleared", title=current_structure.get("title", "Unknown")),
        "",
        tr("quest.discovery.file.next"),
        f"- {tr('quest.discovery.file.id')}: {next_structure.get('id', 'N/A')}",
        f"- {tr('quest.discovery.file.name')}: {next_structure.get('title', 'Unknown')}",
        f"- {tr('quest.discovery.file.intel')}: {next_structure.get('bio', tr('quest.discovery.file.no_intel'))}",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def build_world_rules(modifiers):
    rules = dict(BASE_WORLD_RULES)
    if not isinstance(modifiers, dict):
        return rules

    for key, value in modifiers.items():
        rules[key] = value

    rules["enemy_chance"] = clamp(float(rules.get("enemy_chance", 0.30)), 0.05, 0.90)
    rules["locked_chance"] = clamp(float(rules.get("locked_chance", 0.25)), 0.05, 0.90)
    rules["terminal_chance"] = clamp(float(rules.get("terminal_chance", 0.25)), 0.05, 0.90)
    rules["item_chance"] = clamp(float(rules.get("item_chance", 0.20)), 0.02, 0.90)
    rules["scan_item_discovery_chance"] = clamp(float(rules.get("scan_item_discovery_chance", 0.35)), 0.05, 0.95)
    rules["energy_cost_scale"] = clamp(float(rules.get("energy_cost_scale", 1.0)), 0.50, 2.00)
    rules["core_enemy_hp"] = max(40, int(rules.get("core_enemy_hp", 75)))
    rules["alarm_reinforcement_chance"] = clamp(float(rules.get("alarm_reinforcement_chance", 0.25)), 0.05, 0.95)
    rules["alarm_step"] = max(1, int(rules.get("alarm_step", 1)))
    rules["alarm_reinforcement_threshold"] = max(1, int(rules.get("alarm_reinforcement_threshold", 4)))
    rules["alarm_max"] = max(rules["alarm_reinforcement_threshold"] + 1, int(rules.get("alarm_max", 5)))
    return rules


def apply_starter_pack_to_profile(profile, path, save_profile, starter_credits, starter_items):
    if not profile or not path:
        return

    profile["bank_credits"] = int(profile.get("bank_credits", 0)) + int(starter_credits)

    bank_inventory = profile.get("bank_inventory", [])
    if not isinstance(bank_inventory, list):
        bank_inventory = []
    for item in starter_items:
        bank_inventory.append(item)
    profile["bank_inventory"] = bank_inventory

    save_profile(profile, path)


def unlock_next_structure(profile, path, save_profile, structures, current_structure_id):
    if not profile or not path or not structures:
        return None

    visited = profile.get("visited_structures", [])
    if not isinstance(visited, list):
        visited = []
    if current_structure_id and current_structure_id not in visited:
        visited.append(current_structure_id)

    unvisited = [structure for structure in structures if structure.get("id") not in visited]
    if unvisited:
        next_structure = random.choice(unvisited)
    else:
        next_structure = random.choice(structures)

    profile["visited_structures"] = visited
    profile["next_structure_id"] = next_structure.get("id")
    save_profile(profile, path)
    return next_structure