#!/usr/bin/env python3
import os
import select
import shutil
import sys
from typing import Callable, Dict, List, Optional

try:
    import readline
except ImportError:  # pragma: no cover - platform dependent
    readline = None

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - platform dependent
    termios = None
    tty = None


class NeonConsole:
    """Immersive player console sandboxed to a language-specific root folder."""

    def __init__(
        self,
        player_name: str,
        language: str,
        status_callback: Optional[Callable[[], None]] = None,
        code_input_callback: Optional[Callable[[str], str]] = None,
        prompt_prefix: str = "neon",
    ):
        self.player_name = (player_name or "ANON").strip() or "ANON"
        self.language = (language or "fr").strip().lower() or "fr"
        self.status_callback = status_callback
        self.code_input_callback = code_input_callback
        self.prompt_prefix = prompt_prefix

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.console_root = os.path.realpath(os.path.join(self.base_dir, f"console_{self.language}"))
        self.shared_stats_dir = os.path.realpath(os.path.join(self.base_dir, "stats"))
        os.makedirs(self.console_root, exist_ok=True)
        os.makedirs(self.shared_stats_dir, exist_ok=True)

        # Ensure expected folders exist for future dynamic content.
        for folder in ("logs", "missions", "mail", "archive", "notes"):
            os.makedirs(os.path.join(self.console_root, folder), exist_ok=True)
        self._mount_shared_stats()

        self.current_dir = self.console_root
        self.history: List[str] = []
        self.running = True
        self._readline_prev_completer = None
        self._readline_prev_delims = None

        self.console_commands: Dict[str, Callable[[List[str]], None]] = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "cat": self.cmd_cat,
            "tree": self.cmd_tree,
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "status": self.cmd_status,
            "history": self.cmd_history,
            "whoami": self.cmd_whoami,
            "mail": self.cmd_mail,
            "nano": self.cmd_nano,
            "code_input": self.cmd_code_input,
        }

    def run(self):
        print("\\n[neon-console] Secure channel established.")
        print(f"[neon-console] root: console_{self.language}")
        print("Type 'help' for available commands.")

        self._setup_tab_completion()

        try:
            while self.running:
                try:
                    raw = input(f"{self.player_name}@{self.prompt_prefix}:{self._display_cwd()}$ ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\\n[neon-console] Session closed.")
                    break

                if not raw:
                    continue

                self.history.append(raw)
                parts = raw.split()
                command = parts[0].lower()
                args = parts[1:]

                func = self.console_commands.get(command)
                if func:
                    func(args)
                else:
                    print("Unknown command. Type 'help'.")
        finally:
            self._teardown_tab_completion()

    def _setup_tab_completion(self):
        if readline is None:
            return
        self._readline_prev_completer = readline.get_completer()
        self._readline_prev_delims = readline.get_completer_delims()
        readline.set_completer_delims(" \t\n\"'`@$><=;|&{(")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._complete)

    def _teardown_tab_completion(self):
        if readline is None:
            return
        readline.set_completer(self._readline_prev_completer)
        if self._readline_prev_delims is not None:
            readline.set_completer_delims(self._readline_prev_delims)

    def _complete(self, text: str, state: int):
        if readline is None:
            return None

        line = readline.get_line_buffer()
        begidx = readline.get_begidx()
        matches = self._build_completion_matches(line, begidx, text)
        if state < len(matches):
            return matches[state]
        return None

    def _build_completion_matches(self, line: str, begidx: int, text: str) -> List[str]:
        before = line[:begidx]
        parts_before = before.split()

        # First token: complete command names.
        if not parts_before:
            commands = sorted(self.console_commands.keys())
            return [f"{cmd} " for cmd in commands if cmd.startswith(text)]

        command = parts_before[0].lower()
        if command not in {"ls", "cd", "cat", "nano"}:
            return []

        only_dirs = command == "cd"
        return self._complete_paths(text, only_dirs=only_dirs)

    def _complete_paths(self, raw_token: str, only_dirs: bool) -> List[str]:
        token = raw_token or ""

        if "/" in token:
            parent_part, name_prefix = token.rsplit("/", 1)
            if token.startswith("/") and parent_part == "":
                parent_input = "/"
            else:
                parent_input = parent_part
            display_prefix = parent_part + "/"
        else:
            parent_input = ""
            name_prefix = token
            display_prefix = ""

        base_dir = self.current_dir if parent_input == "" else self._resolve_path(parent_input)
        if not self._is_inside_root(base_dir) or not os.path.isdir(base_dir):
            return []

        matches: List[str] = []
        for name in sorted(os.listdir(base_dir)):
            if not name.startswith(name_prefix):
                continue
            full = os.path.join(base_dir, name)
            is_dir = os.path.isdir(full)
            if only_dirs and not is_dir:
                continue

            completed = f"{display_prefix}{name}"
            if is_dir:
                completed += "/"
            else:
                completed += " "
            matches.append(completed)

        return matches

    def _display_cwd(self) -> str:
        if self._is_within(self.current_dir, self.shared_stats_dir):
            rel = os.path.relpath(self.current_dir, self.shared_stats_dir)
            if rel == ".":
                return "~/stats"
            return "~/stats/" + rel.replace("\\", "/")

        rel = os.path.relpath(self.current_dir, self.console_root)
        if rel == ".":
            return "~"
        return "~/" + rel.replace("\\", "/")

    def _mount_shared_stats(self):
        console_stats_path = os.path.join(self.console_root, "stats")
        if os.path.islink(console_stats_path):
            if os.path.realpath(console_stats_path) == self.shared_stats_dir:
                return
            os.unlink(console_stats_path)
        elif os.path.isdir(console_stats_path):
            for name in sorted(os.listdir(console_stats_path)):
                src = os.path.join(console_stats_path, name)
                dst = os.path.join(self.shared_stats_dir, name)
                if os.path.isfile(src):
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            try:
                os.rmdir(console_stats_path)
            except OSError:
                # Keep local fallback directory if the link cannot be mounted.
                return
        elif os.path.exists(console_stats_path):
            return

        try:
            os.symlink(self.shared_stats_dir, console_stats_path)
        except OSError:
            os.makedirs(console_stats_path, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        if not path:
            return self.current_dir

        if path.startswith("/"):
            candidate = os.path.join(self.console_root, path.lstrip("/"))
        else:
            candidate = os.path.join(self.current_dir, path)

        return os.path.realpath(candidate)

    def _is_within(self, path: str, root: str) -> bool:
        target = os.path.realpath(path)
        base = os.path.realpath(root)
        try:
            return os.path.commonpath([base, target]) == base
        except ValueError:
            return False

    def _is_inside_root(self, path: str) -> bool:
        return self._is_within(path, self.console_root) or self._is_within(path, self.shared_stats_dir)

    def _safe_target(self, path: str) -> Optional[str]:
        target = self._resolve_path(path)
        if not self._is_inside_root(target):
            print("Access denied: path escapes console root.")
            return None
        return target

    def cmd_ls(self, args: List[str]):
        target = self.current_dir
        if args:
            maybe = self._safe_target(args[0])
            if not maybe:
                return
            target = maybe

        if not os.path.exists(target):
            print("No such file or directory.")
            return

        if os.path.isfile(target):
            print(os.path.basename(target))
            return

        entries = sorted(os.listdir(target))
        if not entries:
            print("(empty)")
            return

        for name in entries:
            full = os.path.join(target, name)
            suffix = "/" if os.path.isdir(full) else ""
            print(f"{name}{suffix}")

    def cmd_cd(self, args: List[str]):
        if not args:
            self.current_dir = self.console_root
            return

        dest = args[0]
        if dest == "..":
            parent = os.path.realpath(os.path.join(self.current_dir, ".."))
            if self._is_inside_root(parent):
                self.current_dir = parent
            else:
                self.current_dir = self.console_root
            return

        target = self._safe_target(dest)
        if not target:
            return

        if not os.path.exists(target) or not os.path.isdir(target):
            print("No such directory.")
            return

        self.current_dir = target

    def cmd_pwd(self, args: List[str]):
        _ = args
        print(self._display_cwd())

    def cmd_cat(self, args: List[str]):
        if not args:
            print("Usage: cat <file>")
            return

        target = self._safe_target(args[0])
        if not target:
            return

        if not os.path.exists(target) or not os.path.isfile(target):
            print("No such file.")
            return

        try:
            with open(target, "r", encoding="utf-8") as f:
                print(f.read().rstrip("\\n"))
        except OSError as exc:
            print(f"Read error: {exc}")

    def cmd_tree(self, args: List[str]):
        _ = args
        print(self._display_cwd())
        self._print_tree(self.current_dir, "")

    def _print_tree(self, root: str, prefix: str):
        entries = sorted(os.listdir(root))
        for idx, name in enumerate(entries):
            full = os.path.join(root, name)
            last = idx == len(entries) - 1
            branch = "`-- " if last else "|-- "
            suffix = "/" if os.path.isdir(full) else ""
            print(prefix + branch + name + suffix)
            if os.path.isdir(full):
                ext = "    " if last else "|   "
                self._print_tree(full, prefix + ext)

    def cmd_help(self, args: List[str]):
        _ = args
        print("Available commands:")
        print("  ls [path]         List files/directories")
        print("  cd <dir>          Enter directory")
        print("  cd ..             Go up one level")
        print("  cd                Go back to console root")
        print("  pwd               Show current path")
        print("  cat <file.txt>    Print file content")
        print("  tree              Print current directory tree")
        print("  status            Show in-game player status")
        print("  history           Show recent commands")
        print("  whoami            Show player identity")
        print("  mail              Quick access to mail folder")
        print("  code_input <code> Redeem tactical terminal code")
        print("  nano <file>       Interactive text editor")
        print("  help              Show this help")
        print("  exit              Return to game")

    def cmd_exit(self, args: List[str]):
        _ = args
        self.running = False
        print("[neon-console] Returning to game loop.")

    def cmd_status(self, args: List[str]):
        _ = args
        if self.status_callback:
            self.status_callback()
        else:
            print("Status unavailable.")

    def cmd_history(self, args: List[str]):
        _ = args
        if not self.history:
            print("No command history.")
            return

        for idx, item in enumerate(self.history[-30:], start=max(1, len(self.history) - 29)):
            print(f"{idx:>3}: {item}")

    def cmd_whoami(self, args: List[str]):
        _ = args
        print(f"{self.player_name}@console")
        print(f"language={self.language} root=console_{self.language}")

    def cmd_mail(self, args: List[str]):
        _ = args
        mail_dir = os.path.join(self.console_root, "mail")
        self.current_dir = mail_dir
        print("Switched to ~/mail")

        inbox = os.path.join(mail_dir, "inbox.txt")
        if os.path.isfile(inbox):
            print("---- inbox.txt ----")
            try:
                with open(inbox, "r", encoding="utf-8") as f:
                    print(f.read().rstrip("\\n"))
            except OSError as exc:
                print(f"Read error: {exc}")

    def cmd_code_input(self, args: List[str]):
        if not args:
            print("Usage: code_input <code>")
            return

        if self.code_input_callback is None:
            print("Code system unavailable.")
            return

        code = args[0].strip()
        if not code:
            print("Usage: code_input <code>")
            return

        try:
            result = self.code_input_callback(code)
        except Exception as exc:
            print(f"Code processing error: {exc}")
            return

        if result:
            print(str(result))
        else:
            print("Code rejected.")

    def cmd_nano(self, args: List[str]):
        if not args:
            print("Usage: nano <file>")
            return

        # Bare names are resolved from the current directory.
        target = self._safe_target(args[0])
        if not target:
            return

        parent = os.path.dirname(target)
        if not self._is_inside_root(parent):
            print("Access denied.")
            return

        os.makedirs(parent, exist_ok=True)

        buffer: List[str] = []
        if os.path.isfile(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    buffer = f.read().splitlines()
            except OSError as exc:
                print(f"Read error: {exc}")
                return

        if self._supports_interactive_nano():
            self._run_interactive_nano(target, buffer)
            return

        # Fallback editor for terminals that do not support raw key capture.
        self._run_legacy_nano(target, buffer)

    def _supports_interactive_nano(self) -> bool:
        return (
            termios is not None
            and tty is not None
            and sys.stdin.isatty()
            and sys.stdout.isatty()
        )

    def _write_nano_buffer(self, target: str, buffer: List[str]):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            if not buffer or (len(buffer) == 1 and buffer[0] == ""):
                f.write("")
            else:
                f.write("\n".join(buffer) + "\n")

    def _run_legacy_nano(self, target: str, buffer: List[str]):
        print(f"\n[nano] Editing: {os.path.relpath(target, self.console_root)}")
        print("[nano] Legacy mode. Footer commands: ^O save | ^X quit")
        print("[nano] Reliable aliases: :w save | :q quit | CTRL O | CTRL X")
        if buffer:
            print("[nano] Existing content:")
            for line in buffer:
                print(line)

        while True:
            line = self._read_line_no_readline(": ")
            stripped = line.strip()
            normalized = stripped.upper()

            save_triggers = {
                ":W",
                ":WRITE",
                "^O",
                "CTRL O",
                "CTRL+O",
                "SAVE",
                "/SAVE",
                chr(15),
            }
            quit_triggers = {
                ":Q",
                ":QUIT",
                "^X",
                "CTRL X",
                "CTRL+X",
                "QUIT",
                "/QUIT",
                chr(24),
            }

            if normalized in save_triggers:
                try:
                    self._write_nano_buffer(target, buffer)
                    rel = os.path.relpath(target, self.console_root)
                    print(f"[nano] wrote {rel}")
                except OSError as exc:
                    print(f"Write error: {exc}")
                continue

            if normalized in quit_triggers:
                print("[nano] Exit editor")
                break

            buffer.append(line)

    def _render_nano_screen(
        self,
        target: str,
        buffer: List[str],
        cursor_row: int,
        cursor_col: int,
        row_offset: int,
        col_offset: int,
        status: str,
        dirty: bool,
    ):
        size = shutil.get_terminal_size((80, 24))
        width = max(20, int(size.columns))
        height = max(8, int(size.lines))
        content_rows = max(1, height - 2)

        if cursor_row < row_offset:
            row_offset = cursor_row
        if cursor_row >= row_offset + content_rows:
            row_offset = cursor_row - content_rows + 1

        if cursor_col < col_offset:
            col_offset = cursor_col
        if cursor_col >= col_offset + width:
            col_offset = cursor_col - width + 1

        if self._is_within(target, self.shared_stats_dir):
            rel = "stats/" + os.path.relpath(target, self.shared_stats_dir)
        else:
            rel = os.path.relpath(target, self.console_root)
        marker = "*" if dirty else "-"
        header = f"[nano] {rel} ({marker})"

        lines = [header[:width].ljust(width)]
        for idx in range(content_rows):
            file_row = row_offset + idx
            line = "~"
            if file_row < len(buffer):
                line = buffer[file_row][col_offset : col_offset + width]
            lines.append(line[:width].ljust(width))

        footer = status or "CTRL+O save | CTRL+X quit | CTRL+K cut | CTRL+U paste"
        lines.append(footer[:width].ljust(width))

        output = ["\x1b[2J\x1b[H"]
        for idx, screen_line in enumerate(lines, start=1):
            output.append(f"\x1b[{idx};1H{screen_line}")

        cursor_screen_row = 2 + (cursor_row - row_offset)
        cursor_screen_col = 1 + (cursor_col - col_offset)
        cursor_screen_col = max(1, min(width, cursor_screen_col))
        output.append(f"\x1b[{cursor_screen_row};{cursor_screen_col}H")

        sys.stdout.write("".join(output))
        sys.stdout.flush()
        return row_offset, col_offset

    def _read_nano_key(self, fd: int):
        key = os.read(fd, 1)
        if not key:
            return None

        if key == b"\x18":
            return "CTRL_X"
        if key == b"\x0f":
            return "CTRL_O"
        if key == b"\x0b":
            return "CTRL_K"
        if key == b"\x15":
            return "CTRL_U"
        if key in (b"\r", b"\n"):
            return "ENTER"
        if key in (b"\x7f", b"\x08"):
            return "BACKSPACE"
        if key == b"\t":
            return "TAB"

        if key == b"\x1b":
            seq = b""
            while True:
                ready, _, _ = select.select([fd], [], [], 0.005)
                if not ready:
                    break
                seq += os.read(fd, 1)
                if seq in (b"[A", b"[B", b"[C", b"[D", b"[H", b"[F", b"OH", b"OF"):
                    break
                if seq.endswith(b"~"):
                    break

            mapping = {
                b"[A": "UP",
                b"[B": "DOWN",
                b"[C": "RIGHT",
                b"[D": "LEFT",
                b"[3~": "DELETE",
                b"[H": "HOME",
                b"[F": "END",
                b"OH": "HOME",
                b"OF": "END",
            }
            return mapping.get(seq)

        try:
            text = key.decode("utf-8")
        except UnicodeDecodeError:
            return None
        if text.isprintable():
            return text
        return None

    def _run_interactive_nano(self, target: str, buffer: List[str]):
        if not buffer:
            buffer = [""]

        cursor_row = 0
        cursor_col = 0
        row_offset = 0
        col_offset = 0
        status = "CTRL+O save | CTRL+X quit | CTRL+K cut | CTRL+U paste"
        dirty = False
        exit_armed = False
        cut_buffer = ""

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                row_offset, col_offset = self._render_nano_screen(
                    target,
                    buffer,
                    cursor_row,
                    cursor_col,
                    row_offset,
                    col_offset,
                    status,
                    dirty,
                )
                key = self._read_nano_key(fd)
                if key is None:
                    continue

                if key == "CTRL_X":
                    if dirty and not exit_armed:
                        status = "Unsaved changes. Ctrl+O save | Ctrl+X quit"
                        exit_armed = True
                        continue
                    break

                exit_armed = False
                line = buffer[cursor_row]

                if key == "CTRL_O":
                    try:
                        self._write_nano_buffer(target, buffer)
                        if self._is_within(target, self.shared_stats_dir):
                            rel = "stats/" + os.path.relpath(target, self.shared_stats_dir)
                        else:
                            rel = os.path.relpath(target, self.console_root)
                        status = f"[nano] wrote {rel}"
                        dirty = False
                    except OSError as exc:
                        status = f"Write error: {exc}"
                    continue

                if key == "CTRL_K":
                    if not buffer:
                        status = "Nothing to cut"
                        continue

                    cut_buffer = buffer[cursor_row]
                    if len(buffer) == 1:
                        buffer[0] = ""
                        cursor_row = 0
                        cursor_col = 0
                    else:
                        del buffer[cursor_row]
                        cursor_row = min(cursor_row, len(buffer) - 1)
                        cursor_col = min(cursor_col, len(buffer[cursor_row]))
                    dirty = True
                    status = "[nano] line cut"
                    continue

                if key == "CTRL_U":
                    if cut_buffer == "":
                        status = "Cut buffer empty"
                        continue

                    current_line = buffer[cursor_row]
                    left = current_line[:cursor_col]
                    right = current_line[cursor_col:]
                    buffer[cursor_row] = left + cut_buffer + right
                    cursor_col += len(cut_buffer)
                    dirty = True
                    status = "[nano] text pasted"
                    continue

                if key == "UP":
                    cursor_row = max(0, cursor_row - 1)
                    cursor_col = min(cursor_col, len(buffer[cursor_row]))
                    status = ""
                    continue

                if key == "DOWN":
                    cursor_row = min(len(buffer) - 1, cursor_row + 1)
                    cursor_col = min(cursor_col, len(buffer[cursor_row]))
                    status = ""
                    continue

                if key == "LEFT":
                    if cursor_col > 0:
                        cursor_col -= 1
                    elif cursor_row > 0:
                        cursor_row -= 1
                        cursor_col = len(buffer[cursor_row])
                    status = ""
                    continue

                if key == "RIGHT":
                    if cursor_col < len(line):
                        cursor_col += 1
                    elif cursor_row < len(buffer) - 1:
                        cursor_row += 1
                        cursor_col = 0
                    status = ""
                    continue

                if key == "HOME":
                    cursor_col = 0
                    status = ""
                    continue

                if key == "END":
                    cursor_col = len(line)
                    status = ""
                    continue

                if key == "ENTER":
                    left = line[:cursor_col]
                    right = line[cursor_col:]
                    buffer[cursor_row] = left
                    buffer.insert(cursor_row + 1, right)
                    cursor_row += 1
                    cursor_col = 0
                    dirty = True
                    status = ""
                    continue

                if key == "BACKSPACE":
                    if cursor_col > 0:
                        buffer[cursor_row] = line[: cursor_col - 1] + line[cursor_col:]
                        cursor_col -= 1
                        dirty = True
                    elif cursor_row > 0:
                        prev_len = len(buffer[cursor_row - 1])
                        buffer[cursor_row - 1] = buffer[cursor_row - 1] + line
                        del buffer[cursor_row]
                        cursor_row -= 1
                        cursor_col = prev_len
                        dirty = True
                    status = ""
                    continue

                if key == "DELETE":
                    if cursor_col < len(line):
                        buffer[cursor_row] = line[:cursor_col] + line[cursor_col + 1 :]
                        dirty = True
                    elif cursor_row < len(buffer) - 1:
                        buffer[cursor_row] = line + buffer[cursor_row + 1]
                        del buffer[cursor_row + 1]
                        dirty = True
                    status = ""
                    continue

                insert_text = ""
                if key == "TAB":
                    insert_text = "    "
                elif isinstance(key, str) and len(key) == 1:
                    insert_text = key

                if insert_text:
                    buffer[cursor_row] = line[:cursor_col] + insert_text + line[cursor_col:]
                    cursor_col += len(insert_text)
                    dirty = True
                    status = ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.flush()

        print("[nano] Exit editor")

    def _read_line_no_readline(self, prompt: str) -> str:
        # Bypass readline key bindings so CTRL+O / CTRL+X can be captured as text controls.
        sys.stdout.write(prompt)
        sys.stdout.flush()
        raw = sys.stdin.readline()
        if raw == "":
            raise EOFError
        if raw.endswith("\n"):
            return raw[:-1]
        return raw

def launch_console(
    player_name: str,
    language: str,
    status_callback: Optional[Callable[[], None]] = None,
    code_input_callback: Optional[Callable[[str], str]] = None,
):
    shell = NeonConsole(
        player_name=player_name,
        language=language,
        status_callback=status_callback,
        code_input_callback=code_input_callback,
    )
    shell.run()
