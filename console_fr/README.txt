NEON NODE - Console personnelle (FR)

Ce dossier represente votre espace prive dans le reseau.
La console in-game lit et ecrit directement ici.

Acces depuis le jeu:
- console
- ssh <player>@console

Arborescence:
- logs/ : journaux systeme, traces techniques
- missions/ : objectifs actifs, contrats, briefs
- stats/ : exports et snapshots de donnees
- mail/ : messages entrants
- archive/ : captures anciennes et dossiers historises
- notes/ : vos notes personnelles

Commandes disponibles dans la console:
- ls [path] : lister fichiers/dossiers
- cd <dir> : entrer dans un dossier
- cd .. : remonter
- cd : revenir a la racine console
- pwd : afficher le chemin courant
- cat <fichier> : lire un fichier texte
- tree : afficher une arborescence simple
- status : afficher le status joueur in-game
- history : afficher les dernieres commandes
- whoami : afficher votre identite
- mail : acces rapide au dossier mail
- nano <fichier> : editer/creer un fichier
- help : afficher l'aide
- exit : quitter la console et revenir au jeu

Mode nano (minimal):
- Ecrire: tapez du texte ligne par ligne
- Sauver: :w (ou :write, ^O, CTRL O)
- Quitter: :q (ou :quit, ^X, CTRL X)

Notes techniques:
- Les chemins sont sandboxes: impossible de sortir de console_fr/
- Le contenu est local et editable sans modifier le code Python
- Les fichiers peuvent evoluer selon la progression du joueur
