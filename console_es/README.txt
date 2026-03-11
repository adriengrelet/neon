NEON NODE - Consola personal (ES)

Esta carpeta representa tu espacio privado dentro de la red.
La consola del juego lee y escribe archivos directamente aqui.

Acceso desde el juego:
- console
- ssh <player>@console

Arbol:
- logs/ : registros del sistema y trazas tecnicas
- missions/ : objetivos activos, contratos, briefings
- stats/ : snapshots y exportes de datos
- mail/ : mensajes entrantes
- archive/ : capturas antiguas e historicas
- notes/ : notas personales

Comandos disponibles en consola:
- ls [path] : listar archivos/carpetas
- cd <dir> : entrar en carpeta
- cd .. : subir un nivel
- cd : volver a la raiz de consola
- pwd : mostrar ruta actual
- cat <archivo> : leer archivo de texto
- tree : mostrar arbol simple
- status : mostrar estado del jugador in-game
- history : mostrar comandos recientes
- whoami : mostrar tu identidad
- mail : acceso rapido a la carpeta mail
- nano <archivo> : editar/crear un archivo
- help : mostrar ayuda
- exit : salir de la consola y volver al juego

Modo nano (minimal):
- Escribir: teclea lineas de texto
- Guardar: :w (o :write, ^O, CTRL O)
- Salir: :q (o :quit, ^X, CTRL X)

Notas tecnicas:
- Rutas en sandbox: no puedes salir de console_es/
- El contenido es local y editable sin tocar el codigo Python
- Los archivos pueden evolucionar con la progresion del jugador
