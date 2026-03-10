#!/usr/bin/env python3
# Language dictionary extracted from neon.py

TRANSLATIONS_IT = {'language.title': '=== SCELTA LINGUA ===',
 'language.subtitle': 'Codici disponibili:',
 'language.option': '- {code} : {name}',
 'language.prompt': 'Lingua (fr/en/it/es) > ',
 'language.selected': 'Lingua attiva: {code} ({name})',
 'language.invalid': 'Codice non valido. Usa fr, en, it, es.',
 'statusline.compact': 'HP:{hp} EN:{energy} HK:{hack} AL:{alarm} CR:{credits} FR:{fragments}/3',
 'leaderboard.title': '=== CLASSIFICA ===',
 'leaderboard.entry': '#{idx} {line}',
 'leaderboard.none': 'Nessun punteggio registrato.',
 'intro.press_enter': 'Premi Invio per iniziare...',
 'startup.launching': 'Avvio del gioco...',
 'startup.player_name_prompt': 'Nome giocatore: ',
 'startup.player_name_echo': 'Giocatore: {name}',
 'startup.difficulty_title': '=== SELEZIONE DIFFICOLTA ===',
 'startup.difficulty_1': '1. Passeggiata cyber - Hack: 60s  Combattimento: 10s  Riflesso: 6s  Moltiplicatore punti: 1x',
 'startup.difficulty_2': '2. Prova cyber - Hack: 45s  Combattimento: 6s   Riflesso: 4s  Moltiplicatore punti: 2x',
 'startup.difficulty_3': '3. Sudore cyber - Hack: 30s  Combattimento: 4s   Riflesso: 2s  Moltiplicatore punti: 3x',
 'startup.difficulty_4': '4. Violenza cyber - Hack: 20s  Combattimento: 3s   Riflesso: 3s  Moltiplicatore punti: 4x',
 'startup.difficulty_prompt': 'Scegli livello (1-4): ',
 'startup.difficulty_invalid': 'Livello non valido, selezionata la difficolta 3 di default.',
 'map.title': '=== MAPPA ===',
 'map.legend': 'Legenda: P=Giocatore | C=Core | .=Stanza visitata | E=Nemico | L=Loot | F=Frammento | M=Multi | '
               '#=Sconosciuta',
 'describe.enemy_present': '⚠ Nemico presente: {enemy}',
 'describe.core_hp': 'HP CORE Sentinel: {hp}',
 'describe.locked': '🔒 Stanza bloccata.',
 'describe.terminal': '💻 Terminale rilevato.',
 'describe.item_visible': '📦 Oggetto visibile: {item}',
 'describe.fragment_visible': '🧩 Frammento ROM rilevato: {fragment_id}',
 'describe.core_detected': '===== ☢ CORE CENTRALE rilevato! =====',
 'move.locked_exit': '🔒 Impossibile uscire: blocco attivo.',
 'move.wall': 'Muro strutturale.',
 'scan.title': '=== SCANSIONE PROFONDA ===',
 'scan.cost': 'Costo energetico scansione: {cost}',
 'scan.object_found': 'Oggetto nascosto rilevato: {item}',
 'scan.lock_pulse': 'Il blocco pulsa a frequenza variabile.',
 'scan.ports_open': 'Porte di intrusione ancora aperte.',
 'scan.rom_signature': 'Firma ROM frammentaria rilevata in questa stanza.',
 'scan.nothing': 'Nessuna novita rilevata.',
 'echo.title': '=== ECHO ESTESO ===',
 'echo.cost': 'Costo energetico echo: {cost}',
 'echo.detected': 'Firme tattiche rilevate attorno a te: {count}',
 'echo.none': 'Nessuna firma tattica rilevata attorno a te.',
 'story.title': '=== FILE ROM DECIFRATO ===',
 'story.id': 'ID: {id}',
 'story.name': 'Titolo: {title}',
 'story.hacker': 'Hacker: {hacker}',
 'story.context': 'Contesto: {context}',
 'story.logs': '--- LOG ---',
 'story.epilogue': '--- EPILOGO ---',
 'fragments.title': '=== FRAMMENTI ROM ===',
 'fragments.count': 'Raccolta: {found}/{total}',
 'fragments.line': '[{mark}] {id} - {label}',
 'fragments.unlocked': 'Accesso al dossier narrativo completo sbloccato.',
 'fragments.read_prompt': 'Leggere ora la storia? (y/n) ',
 'fragments.incomplete': 'Recupera tutti e 3 i frammenti per decifrare la storia completa.',
 'hack.matrix.title': '=== MATRICE DI INTRUSIONE ===',
 'hack.matrix.sequence': 'Sequenza obiettivo: {sequence}',
 'hack.matrix.rules': 'Passo 1 libero | Passo 2 stessa colonna | Passo 3 stessa riga',
 'hack.matrix.step_prompt': 'Passo {step} > ',
 'hack.matrix.timeout': 'Tempo scaduto',
 'hack.matrix.incorrect': 'Codice errato',
 'hack.matrix.same_column': 'Richiesta stessa colonna',
 'hack.matrix.same_row': 'Richiesta stessa riga',
 'core_hint.east': 'INDIZIO: Il core e a est.',
 'core_hint.west': 'INDIZIO: Il core e a ovest.',
 'core_hint.south': 'INDIZIO: Il core e a sud.',
 'core_hint.north': 'INDIZIO: Il core e a nord.',
 'hack.blocked_core': 'Il CORE e protetto. Neutralizza prima il nemico presente.',
 'hack.nothing': 'Niente da hackerare qui.',
 'hack.title': '=== HACK ===',
 'hack.cost': 'Costo energetico: {cost}',
 'hack.alarm_triggered': '⚠ Attenzione: allarme livello {alarm} attivato!',
 'hack.alarm_enemy': "🚨 Nemico d'allarme dispiegato in questa stanza!",
 'hack.reduced': 'Hack ridotto a {hack}',
 'hack.standard_success': '💻 Hack standard riuscito. Scegli il loot:',
 'hack.fragment_ping': '🛰️ Intel terminale: firme ROM mappate ({count}).',
 'hack.fragment_ping_none': 'Intel terminale: nessuna firma ROM sconosciuta da rivelare.',
 'hack.loot.a': 'A. Crediti',
 'hack.loot.b': 'B. Cura neurocyber (+25 HP)',
 'hack.loot.c': 'C. Upgrade hack (+5 HK)',
 'hack.loot.d': 'D. Cura cibernetica (+10 HP)',
 'hack.loot.prompt': 'Loot > ',
 'hack.loot.heal': '🧠 Cura applicata: +25 HP',
 'hack.loot.upgrade': '⚙ Upgrade hack applicato: +5 HK',
 'hack.loot.cyber_heal': '⚕️ Cura cibernetica applicata: +10 HP',
 'hack.loot.credits': '💰 Loot crediti ottenuto: +{credits}',
 'hack.success.credits': '💻 Hack riuscito! +{credits} crediti',
 'hack.alarm_reduced': 'Allarme ridotto di 1.',
 'hack.unlock_room': '🔓 Stanza sbloccata.',
 'hack.core_pirated': '☢ CORE hackerato. Estrazione possibile.',
 'hack.done_ms': 'Hack completato in {ms} ms',
 'attack.no_target': 'Nessun bersaglio.',
 'attack.stance.aggressive': 'Il nemico carica con aggressivita, pronto a colpire forte.',
 'attack.stance.defensive': 'Il nemico si barrica dietro difese solide.',
 'attack.stance.unstable': 'Il nemico si muove in modo erratico e imprevedibile.',
 'attack.prompt': 'Combattimento: A frontale | B finta | C sovraccarico (scegli entro {time}s)',
 'attack.choice_prompt': 'Scelta > ',
 'attack.timeout': 'Tempo di reazione troppo lungo: azione casuale selezionata.',
 'attack.reflex_prompt': '⚡ Riflesso: digita {char} in fretta',
 'attack.reflex.success': 'Riuscito in {ms} ms! Bonus: danni ridotti.',
 'attack.reflex.failure': 'Fallito in {ms} ms! Malus: danni aumentati.',
 'attack.bonus.surcharge': 'Sovraccarico attivato: danni ridotti!',
 'attack.bonus.force': 'Potenziamento forza attivato: danni ridotti!',
 'attack.bonus.vitesse': 'Potenziamento velocita attivato: danni ridotti!',
 'attack.core.hit': 'Attacchi il CORE Sentinel! Danni: {damage}',
 'attack.core.hp': 'HP CORE Sentinel: {hp}',
 'attack.core.counter': 'Il CORE Sentinel contrattacca! Subisci {damage} danni.',
 'attack.core.neutralized': 'CORE Sentinel neutralizzato!',
 'attack.core.remaining_hack': 'Sentinel abbattuto, ma devi ancora hackerare il CORE.',
 'attack.neutralize': 'Neutralizzi {enemy}',
 'attack.taken': 'Subisci {damage} danni',
 'enemy_attack.core': '⚠️ Il CORE Sentinel ti attacca! Subisci {damage} danni.',
 'enemy_attack.normal': '⚠️ {enemy} ti attacca! Subisci {damage} danni.',
 'take.fragment': 'Frammento ROM recuperato: {fragment_id} ({count}/3)',
 'take.item': 'Preso: {item}',
 'take.none': 'Niente da prendere.',
 'use.absent': 'Oggetto assente.',
 'use.used': '{item} usato.',
 'inventory.title': 'Inventario:',
 'inventory.empty': 'Vuoto',
 'inventory.medkit': '- medkit: ripristina 25 HP',
 'inventory.energy_cell': '- energy_cell: ripristina 25 energia',
 'inventory.exploit_chip': '- exploit_chip: +10 hack',
 'status.title': '=== EQUIPAGGIAMENTO AUMENTATO ===',
 'status.synaptique': '- Potenziamento sinaptico: +10s al tempo di hack',
 'status.surcharge': '- Potenziamento sovraccarico: migliora il sovraccarico in combattimento',
 'status.interface': '- Interfaccia neurale hacker avanzata: matrice ridotta di 1',
 'status.combat_chip': "- Chip da combattimento: raddoppia il tempo d'azione in combattimento",
 'status.force': "- Potenziamento forza: migliora l'attacco frontale",
 'status.vitesse': '- Potenziamento velocita: migliora la finta',
 'status.dissipateur': '- Dissipatore energetico: dimezza i costi energetici delle azioni',
 'status.none': 'Nessuno',
 'status.characteristics': '=== CARATTERISTICHE ===',
 'status.line': 'HP (Heal Points):{hp} EN (Energy):{energy} HK (Hack):{hack} AL (Alarm):{alarm} CR (Credits):{credits}',
 'status.fragments': 'Frammenti ROM: {count}/3',
 'help.commands': 'Comandi: n s e w | scan/sc | echo/ec | hack/h | attack/at | take/t | use/u <oggetto> | '
                  'inventory/inv | map/m | status/stat | fragments/fra | shop/sh | help/he | quit/q',
 'shop.title': '=== NEGOZIO ===',
 'shop.credits': 'Crediti disponibili: {credits}',
 'shop.items': 'Oggetti disponibili:',
 'shop.item.1': '1. Potenziamento sinaptico - 100 crediti: +10s al tempo di hack',
 'shop.item.2': '2. Potenziamento sovraccarico - 100 crediti: migliora il sovraccarico in combattimento',
 'shop.item.3': '3. Interfaccia neurale hacker avanzata - 150 crediti: matrice ridotta di 1',
 'shop.item.4': '4. Chip da combattimento - 150 crediti: raddoppia il tempo per agire in combattimento',
 'shop.item.5': '5. Potenziamento forza - 100 crediti: migliora attacco frontale',
 'shop.item.6': '6. Potenziamento velocita - 100 crediti: migliora finta',
 'shop.item.7': '7. Dissipatore energetico - 300 crediti: dimezza i costi EN delle azioni',
 'shop.item.0': '0. Esci',
 'shop.prompt': 'Scelta > ',
 'shop.buy.1': 'Potenziamento sinaptico acquistato! +10s al tempo di hack.',
 'shop.buy.2': 'Potenziamento sovraccarico acquistato! Sovraccarico migliorato in combattimento.',
 'shop.buy.3': 'Interfaccia neurale acquistata! Matrice ridotta di 1.',
 'shop.buy.4': 'Chip da combattimento acquistato! Tempo di combattimento raddoppiato.',
 'shop.buy.5': 'Potenziamento forza acquistato! Attacco frontale migliorato.',
 'shop.buy.6': 'Potenziamento velocita acquistato! Finta migliorata.',
 'shop.buy.7': 'Dissipatore energetico acquistato! I costi EN delle azioni sono dimezzati.',
 'shop.invalid': 'Scelta non valida o crediti insufficienti.',
 'enemy_turn.reinforcement': '⚠ Rinforzo di sistema rilevato',
 'score.title': '=== PUNTEGGIO FINALE ===',
 'score.base': 'Punteggio base: {score}',
 'score.rom_bonus': 'Bonus frammenti ROM: {bonus}',
 'score.time_bonus': 'Bonus tempo totale: {bonus}',
 'score.hack_bonus': 'Bonus tempo hack: {bonus}',
 'score.rank': 'Il tuo punteggio ti classifica #{rank}.',
 'core.pirated': '=== CORE HACKERATO ===',
 'main.spawn': 'posizione spawn {x},{y}',
 'main.core': 'posizione core {x},{y}',
 'main.story_channel': 'Canale ROM rilevato: dossier {story_id} frammentato in 3 cache.',
 'main.death': 'Cadi nella rete.',
 'main.alarm_game_over': '🚨 Allarme massimo raggiunto! Game over.',
 'ui.choice_prompt': 'Scelta > ',
 'ui.reflex_input_prompt': '> ',
 'ui.command_prompt': '\n> ',
 'ui.quit_confirm': 'Vuoi uscire dalla partita in corso? (y/n) ',
 'ui.replay_prompt': 'Rigiocare? (y/n) ',
 'ui.unknown_command': 'Comando sconosciuto.',
 'error.unhandled': 'Si e verificato un errore: {error}',
 'intro.full': '\n'
               '==============================\n'
               '    NEON NODE v6\n'
               '==============================\n'
               '\n'
               'Infiltrati nella megastruttura.\n'
               'Raggiungi il CORE centrale, hackeralo ed esci vivo.\n'
               '\n'
               'Per gli hack:\n'
               '- Piu alto e il tuo hack, piu piccola e la matrice.\n'
               '- Passo 1: trova liberamente il valore esadecimale corretto nella matrice (deve corrispondere al primo '
               'valore richiesto).\n'
               '- Passo 2: deve essere nella stessa colonna del passo 1.\n'
               '- Passo 3: deve essere nella stessa riga del passo 2.\n'
               '\n'
               'Esempio tutorial (matrice fittizia):\n'
               '      1    2    3    4\n'
               ' A   9C   55   BD   E1\n'
               ' B   F2   AA   2D   6C\n'
               ' C   1D   B4   91   D9\n'
               ' D   0F   7A   C7   3F\n'
               '\n'
               '- Sequenza richiesta: AA -> 7A -> 3F\n'
               '- Passo 1: B2 (OK, B2 = AA)\n'
               '- Passo 2: D2 (OK, stessa colonna di B2, e D2 = 7A)\n'
               '- Passo 3: D4 (OK, stessa riga di D2, e D4 = 3F)\n'
               '- Input finale valido: B2 -> D2 -> D4\n'
               '\n'
               "Il tempo e limitato per completare l'hack; fallire aumenta l'allarme e riduce il tuo hack.\n"
               '\n'
               'I crediti si ottengono hackerando terminali e possono essere usati per comprare potenziamenti nel '
               'negozio.\n'
               'Piu velocemente hackeri, piu crediti guadagni!\n'
               '\n'
               'Comandi:\n'
               ' north / n : muoversi a nord\n'
               ' south / s : muoversi a sud\n'
               ' east / e : muoversi a est\n'
               ' west / w  : muoversi a ovest\n'
               ' scan / sc : scandire la sala per trovare oggetti nascosti o indizi\n'
               ' echo / ec : sondare le sale vicine e rivelare marcatori tattici sulla mappa\n'
               ' hack / h : tentare di hackerare un terminale o disattivare un blocco\n'
               ' attack : ingaggiare combattimento con un nemico presente\n'
               ' take / t : raccogliere un oggetto visibile nella sala o trovato con scan\n'
               " use <oggetto> / u <oggetto> : usare un oggetto dell'inventario (es: use medkit)\n"
               ' map / m : mostrare la mappa del livello (P = posizione, C = core, . = sala visitata, # = sala non '
               'visitata)\n'
               ' inventory / inv : mostrare inventario\n'
               ' status / stat : mostrare stato e potenziamenti\n'
               ' fragments / fra : mostrare frammenti ROM raccolti e dossier narrativo\n'
               ' shop / sh : aprire il negozio per comprare potenziamenti con i crediti\n'
               ' help / he : mostrare i comandi\n'
               ' quit / q : uscire dal gioco\n',
 'content.rom_story_archive': [{'id': 'ROM-AX13',
                                'title': 'AX13 // Ultima Deriva',
                                'hacker': 'Mara Voss (lei)',
                                'bio': 'Ex ingegnera di rete di Kheiron Dynamics, scomparsa dopo aver tentato di far '
                                       'trapelare codice interno.',
                                'fragments': [{'id': 'AX13-1', 'label': 'Bootlog Bunker'},
                                              {'id': 'AX13-2', 'label': 'Diario di Progresso'},
                                              {'id': 'AX13-3', 'label': 'Segnale Finale'}],
                                'logs': ["[2091-04-12 22:13] Infiltrazione all'ingresso del livello C. Rumore dei "
                                         'droni piu forte del previsto.',
                                         '[2091-04-12 22:17] Il portello sente ancora di ozono. Ho progettato questo '
                                         'protocollo sei anni fa. Vederlo riusato qui mi fa vomitare.',
                                         "[2091-04-12 22:24] Una camera mi ha seguito senza far scattare l'allarme. O "
                                         'sono gia segnalata, o qualcuno sta rallentando il sistema.',
                                         '[2091-04-12 22:31] Blocco termico neutralizzato. Ho perso il 30% dei miei '
                                         'strumenti.',
                                         '[2091-04-12 22:38] Lian diceva sempre che finiamo per abitare le strutture '
                                         'che odiamo. Credo avesse ragione.',
                                         '[2091-04-12 22:49] Ho visto il Sentinel in lontananza. Non e un bot '
                                         "standard. Esita prima di puntare l'ottica su di me.",
                                         '[2091-04-12 23:02] Allarmi a cascata. I corridoi si riconfigurano in loop.',
                                         '[2091-04-12 23:05] Paradosso: entro per sabotare questo sistema, ma ogni '
                                         'porta aperta dimostra che il mio vecchio codice regge meglio di me.',
                                         '[2091-04-12 23:09] Se qualcuno legge questo: non restare mai fermo dopo un '
                                         'hack riuscito.',
                                         '[2091-04-12 23:11] Sto sanguinando nella tuta. Lascio questo dossier in tre '
                                         'cache ROM.'],
                                'epilogue': 'Fine trasmissione. Il segnale di Mara si interrompe di colpo dopo un '
                                            'sovraccarico di sicurezza.'},
                               {'id': 'ROM-KR22',
                                'title': 'KR22 // Debito Rosso',
                                'hacker': 'Kenji Rault (lui)',
                                'bio': 'Corriere dati indipendente, infiltrato nella megastruttura per cancellare un '
                                       'contratto di debito.',
                                'fragments': [{'id': 'KR22-1', 'label': 'Mandato Notturno'},
                                              {'id': 'KR22-2', 'label': 'Mappa Corrotta'},
                                              {'id': 'KR22-3', 'label': 'Ultimo Pledge'}],
                                'logs': ['[2088-09-03 01:40] Ingresso silenzioso. Ho pagato un fixer per una chiave '
                                         'monouso.',
                                         '[2088-09-03 01:46] Corro meglio quando sono arrabbiato. Brutta notizia: lo '
                                         'sono da anni.',
                                         '[2088-09-03 02:02] Il mio scanner mente. Alcune stanze esistono, poi '
                                         'scompaiono.',
                                         '[2088-09-03 02:09] Mia sorella crede che io trasporti ancora pacchi anonimi. '
                                         'Non le ho mai detto che a volte quei pacchi sono prove.',
                                         '[2088-09-03 02:19] Ho recuperato crediti, ma ogni terminale aumenta la '
                                         'pressione.',
                                         '[2088-09-03 02:25] Il CORE trasmette la mia vecchia cartella clinica. Mi '
                                         'conoscono.',
                                         '[2088-09-03 02:28] Paradosso stupido: rubare crediti per cancellare un '
                                         'debito significa obbedire ancora alla logica del conto.',
                                         '[2088-09-03 02:33] Continuo. Se esco, mia sorella dormira finalmente senza '
                                         'debiti.',
                                         '[2088-09-03 02:36] Impatto. Drone nel mio angolo cieco. Segmento questo log '
                                         'in 3 frammenti ROM.'],
                                'epilogue': 'Il contratto di debito non e mai stato ritrovato negli archivi pubblici.'},
                               {'id': 'ROM-NQ05',
                                'title': 'NQ05 // Camera Fredda',
                                'hacker': 'Noor Qassem (loro)',
                                'bio': 'Criptoanalista freelance specializzato in memorie morte e IA patrimoniali.',
                                'fragments': [{'id': 'NQ05-1', 'label': 'Traccia di Avvicinamento'},
                                              {'id': 'NQ05-2', 'label': 'Rottura di Interfaccia'},
                                              {'id': 'NQ05-3', 'label': 'Voce del Nucleo'}],
                                'logs': ['[2093-02-20 18:05] I muri sono freddi. Qui tutto consuma calore come fossero '
                                         'prove.',
                                         '[2093-02-20 18:11] Una porta ha riprodotto il mio stesso respiro con tre '
                                         'secondi di anticipo.',
                                         '[2093-02-20 18:27] Una stanza mi ha restituito il riflesso con 4 secondi di '
                                         'anticipo.',
                                         '[2093-02-20 18:36] Nel server squat dicevamo che un archivio salvato puo '
                                         'valere una sommossa.',
                                         '[2093-02-20 18:51] Le routine sentinella imitano errori umani. Brutto segno.',
                                         "[2093-02-20 19:04] Hack pulito riuscito. L'allarme e comunque salito.",
                                         '[2093-02-20 19:10] Paradosso: preservo frammenti di memoria mentre non so '
                                         'piu se certi ricordi siano miei.',
                                         '[2093-02-20 19:18] Se cado, che qualcuno porti fuori questi log. Che servano '
                                         "a qualcos'altro.",
                                         '[2093-02-20 19:21] Contatto perso. Blocco la mia storia in frammenti ROM.'],
                                'epilogue': 'Il resto dei dati di Noor e marcato come inconciliabile.'},
                               {'id': 'ROM-LV77',
                                'title': 'LV77 // Fork Selvaggio',
                                'hacker': 'Leia Varek (lei)',
                                'bio': 'Sviluppatrice da un collettivo software libero sciolto dopo una perquisizione.',
                                'fragments': [{'id': 'LV77-1', 'label': 'Repo Nascosto'},
                                              {'id': 'LV77-2', 'label': 'Conflitto di Branch'},
                                              {'id': 'LV77-3', 'label': 'Commit Finale'}],
                                'logs': ['[2090-06-03 00:11] Ingresso validato. Gli scanner girano su una vecchia base '
                                         'Unix truccata.',
                                         '[2090-06-03 00:19] Ada diceva che un fork a volte e una rottura sentimentale '
                                         'scritta in sintassi pulita.',
                                         '[2090-06-03 00:28] Entro per rubare un repository che era gia mio prima dei '
                                         'brevetti.',
                                         '[2090-06-03 00:42] Primo Sentinel neutralizzato.',
                                         '[2090-06-03 00:57] Paradosso: odio i monopoli ma spero ancora che il mio '
                                         'codice sopravviva sotto il loro logo.',
                                         '[2090-06-03 01:03] Se qualcuno legge questo: pubblicare puo essere piu '
                                         'pericoloso che cancellare.'],
                                'epilogue': 'Il repository non e mai stato ripubblicato integralmente.'},
                               {'id': 'ROM-SM04',
                                'title': 'SM04 // Zona Muta',
                                'hacker': 'Sam Mirek (lui)',
                                'bio': 'Ex tecnico radio pirata specializzato in bollettini clandestini.',
                                'fragments': [{'id': 'SM04-1', 'label': 'Frequenza 1'},
                                              {'id': 'SM04-2', 'label': 'Frequenza 2'},
                                              {'id': 'SM04-3', 'label': 'Frequenza 3'}],
                                'logs': ['[2087-11-19 03:10] Riconosco i disturbi elettrici prima ancora di vedere i '
                                         'droni.',
                                         '[2087-11-19 03:21] Un altoparlante a muro ha riprodotto la mia vecchia '
                                         'emissione pirata del 2084.',
                                         '[2087-11-19 03:34] Mio fratello diceva che parlare troppo forte attira '
                                         'sempre gli stivali.',
                                         '[2087-11-19 03:41] Paradosso: pirato frequenze per liberare la parola, ma '
                                         'qui ogni parola mi localizza.',
                                         '[2087-11-19 03:52] Se cado, fate almeno circolare il rumore.'],
                                'epilogue': "Nessuna fonte ha confermato l'uscita di Sam."},
                               {'id': 'ROM-IR31',
                                'title': 'IR31 // Cenere Amministrativa',
                                'hacker': 'Iris Ren (lei)',
                                'bio': 'Ex impiegata amministrativa che ha sabotato sfratti automatizzati.',
                                'fragments': [{'id': 'IR31-1', 'label': 'Dossier Falso'},
                                              {'id': 'IR31-2', 'label': 'Procedura Inversa'},
                                              {'id': 'IR31-3', 'label': 'Archivio Cenere'}],
                                'logs': ['[2092-01-08 19:14] Conosco ancora i menu interni meglio degli agenti che li '
                                         'applicano.',
                                         '[2092-01-08 19:25] Ho gia salvato centotrentadue fascicoli con semplici '
                                         'errori volontari.',
                                         '[2092-01-08 19:39] Qui i terminali classificano le vite come ticket.',
                                         "[2092-01-08 19:48] Paradosso: falsificare per ristabilire un po' di "
                                         'giustizia resta comunque falsificare.',
                                         '[2092-01-08 19:56] Continuo.'],
                                'epilogue': "I log interni citano un'anomalia umana persistente."},
                               {'id': 'ROM-DX90',
                                'title': 'DX90 // Sintassi Dissidente',
                                'hacker': 'Dax Oren (loro)',
                                'bio': 'Maintainer di una distribuzione clandestina cifrata.',
                                'fragments': [{'id': 'DX90-1', 'label': 'Bootstrap'},
                                              {'id': 'DX90-2', 'label': 'Kernel Drift'},
                                              {'id': 'DX90-3', 'label': 'Root Panic'}],
                                'logs': ['[2094-07-01 21:03] Chiave iniettata nella rete secondaria.',
                                         '[2094-07-01 21:17] Riunione collettiva ieri: due ore per discutere il nome '
                                         'di un pacchetto.',
                                         '[2094-07-01 21:31] Paradosso: vogliamo abolire le gerarchie ma alla fine '
                                         'qualcuno mergea sempre da solo.',
                                         '[2094-07-01 21:44] Primo colpo evitato.',
                                         '[2094-07-01 21:52] Anche le rivoluzioni hanno bisogno di qualcuno che ti '
                                         'ricordi di mangiare.'],
                                'epilogue': 'Una chiave simile e riapparsa piu tardi su varie reti libere.'},
                               {'id': 'ROM-PT12',
                                'title': 'PT12 // Linea Fantasma',
                                'hacker': 'Pia Torres (lei)',
                                'bio': 'Ex conducente di metro autonoma diventata sabotatrice tecnica.',
                                'fragments': [{'id': 'PT12-1', 'label': 'Binario Morto'},
                                              {'id': 'PT12-2', 'label': 'Bypass'},
                                              {'id': 'PT12-3', 'label': 'Ultima Linea'}],
                                'logs': ['[2089-12-14 04:05] Il silenzio qui assomiglia ai tunnel prima del ritorno di '
                                         'tensione.',
                                         '[2089-12-14 04:18] Ho imparato a rallentare i sistemi prima di imparare a '
                                         'romperli.',
                                         '[2089-12-14 04:29] Paradosso: odio gli automatismi ma mi fido dei miei '
                                         'riflessi piu che delle persone.',
                                         '[2089-12-14 04:37] Due droni dietro di me.'],
                                'epilogue': 'Il dossier sui trasporti privatizzati non e mai riemerso.'},
                               {'id': 'ROM-HQ44',
                                'title': 'HQ44 // Archivio di Rumore',
                                'hacker': 'Hugo Quent (lui)',
                                'bio': 'Musicista noise diventato pirata di segnali.',
                                'fragments': [{'id': 'HQ44-1', 'label': 'Impulso'},
                                              {'id': 'HQ44-2', 'label': 'Feedback'},
                                              {'id': 'HQ44-3', 'label': 'Taglio'}],
                                'logs': ['[2086-03-03 02:14] Ogni allarme qui ha quasi una tonalita sfruttabile.',
                                         '[2086-03-03 02:27] Conto i passi come battute.',
                                         '[2086-03-03 02:39] Paradosso: trasformare la paura in ritmo non la annulla.',
                                         '[2086-03-03 02:45] Credo di sentire un respiro dietro i rele.'],
                                'epilogue': 'Un estratto audio attribuito a Hugo circola ancora in alcune reti '
                                            'pirata.'},
                               {'id': 'ROM-ZE08',
                                'title': 'ZE08 // Comune Incompleta',
                                'hacker': 'Zea Elin (lei)',
                                'bio': 'Membro di una micro-comune urbana autogestita.',
                                'fragments': [{'id': 'ZE08-1', 'label': 'Cucina Collettiva'},
                                              {'id': 'ZE08-2', 'label': 'Contatore Nero'},
                                              {'id': 'ZE08-3', 'label': 'Uscita Incompleta'}],
                                'logs': ['[2095-05-10 23:01] Abbiamo condiviso la zuppa prima della mia partenza.',
                                         '[2095-05-10 23:14] Le letture energetiche mentono esattamente come i '
                                         'prefetti.',
                                         '[2095-05-10 23:28] Paradosso: vivere senza capi a volte richiede piu '
                                         'disciplina del contrario.',
                                         '[2095-05-10 23:37] Se torno, dovro ancora riparare il caricatore solare sul '
                                         'tetto.'],
                                'epilogue': 'Il quartiere di Zea ha subito un blackout totale due settimane dopo.'}],
 'content.room_descriptions': ['Corridoio saturo di neon rossi.',
                               'Sala server dove ronzano relè termici.',
                               'Zona tecnica abbandonata coperta di cavi.',
                               'Vecchio checkpoint di sicurezza.',
                               'Passaggio stretto con insegna rotta lampeggiante.',
                               'Sala immersa in rumore elettrico intermittente.',
                               'Sala di controllo con schermi olografici in avaria.',
                               'Tunnel di ventilazione pieno di condotti arrugginiti.',
                               'Laboratorio abbandonato con strane attrezzature mediche.',
                               'Hangar vuoto che risuona di echi lontani.',
                               'Ufficio dirigenziale con arredi high-tech distrutti.',
                               'Zona di stoccaggio con casse dati impilate.',
                               'Sala riunioni con tavolo interattivo rotto.',
                               "Corridoio d'accesso agli ascensori bloccati.",
                               'Zona manutenzione con attrezzi sparsi.'],
 'content.enemies': ['Drone', 'Guardia', 'Bot Sentinella', 'Cacciatore Proxy'],
 'content.items': ['medkit', 'energy_cell', 'exploit_chip']}
