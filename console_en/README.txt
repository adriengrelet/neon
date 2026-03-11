NEON NODE - Personal console (EN)

This folder is your private space inside the network.
The in-game console reads and writes files directly here.

Access from game:
- console
- ssh <player>@console

Tree:
- logs/ : system logs and technical traces
- missions/ : active objectives, contracts, briefs
- stats/ : data snapshots and exports
- mail/ : incoming messages
- archive/ : older captures and historical files
- notes/ : your personal notes

Available console commands:
- ls [path] : list files/directories
- cd <dir> : enter directory
- cd .. : go up
- cd : go back to console root
- pwd : print current path
- cat <file> : read text file
- tree : print a simple directory tree
- status : show in-game player status
- history : show recent commands
- whoami : show your identity
- mail : quick access to mail folder
- nano <file> : edit/create a file
- help : show help
- exit : leave console and return to game

Nano mode (minimal):
- Write: type lines of text
- Save: :w (or :write, ^O, CTRL O)
- Quit: :q (or :quit, ^X, CTRL X)

Technical notes:
- Paths are sandboxed: you cannot escape console_en/
- Content is local and editable without changing Python code
- Files can evolve dynamically with player progression
