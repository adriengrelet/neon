NEON NODE - Console personale (IT)

Questa cartella rappresenta il tuo spazio privato nella rete.
La console in-game legge e scrive file direttamente qui.

Accesso dal gioco:
- console
- ssh <player>@console

Struttura:
- logs/ : log di sistema e tracce tecniche
- missions/ : obiettivi attivi, contratti, briefing
- stats/ : snapshot ed export dati
- mail/ : messaggi in arrivo
- archive/ : catture vecchie e file storici
- notes/ : note personali

Comandi disponibili nella console:
- ls [path] : elencare file/cartelle
- cd <dir> : entrare in una cartella
- cd .. : salire di livello
- cd : tornare alla radice console
- pwd : mostrare il percorso corrente
- cat <file> : leggere un file di testo
- tree : mostrare un albero semplice
- status : mostrare lo stato giocatore in-game
- history : mostrare i comandi recenti
- whoami : mostrare la tua identita
- mail : accesso rapido alla cartella mail
- nano <file> : modificare/creare un file
- help : mostrare aiuto
- exit : uscire dalla console e tornare al gioco

Modalita nano (minimale):
- Scrivere: digita testo riga per riga
- Salvare: :w (oppure :write, ^O, CTRL O)
- Uscire: :q (oppure :quit, ^X, CTRL X)

Note tecniche:
- Percorsi in sandbox: non puoi uscire da console_it/
- Il contenuto e locale e modificabile senza toccare il codice Python
- I file possono evolvere con la progressione del giocatore
