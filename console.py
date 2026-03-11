#!/usr/bin/env python3
import os
import sys
from typing import Callable, Dict, List, Optional

try:
    import readline
except ImportError:  # pragma: no cover - platform dependent
    readline = None


class NeonConsole:
    """Immersive player console sandboxed to a language-specific root folder."""

    def __init__(
        self,
        player_name: str,
        language: str,
        status_callback: Optional[Callable[[], None]] = None,
        prompt_prefix: str = "neon",
    ):
        self.player_name = (player_name or "ANON").strip() or "ANON"
        self.language = (language or "fr").strip().lower() or "fr"
        self.status_callback = status_callback
        self.prompt_prefix = prompt_prefix

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.console_root = os.path.realpath(os.path.join(self.base_dir, f"console_{self.language}"))
        os.makedirs(self.console_root, exist_ok=True)

        # Ensure expected folders exist for future dynamic content.
        for folder in ("logs", "missions", "stats", "mail", "archive", "notes"):
            os.makedirs(os.path.join(self.console_root, folder), exist_ok=True)

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
        rel = os.path.relpath(self.current_dir, self.console_root)
        if rel == ".":
            return "~"
        return "~/" + rel.replace("\\\\", "/")

    def _resolve_path(self, path: str) -> str:
        if not path:
            return self.current_dir

        if path.startswith("/"):
            candidate = os.path.join(self.console_root, path.lstrip("/"))
        else:
            candidate = os.path.join(self.current_dir, path)

        return os.path.realpath(candidate)

    def _is_inside_root(self, path: str) -> bool:
        root = self.console_root
        try:
            return os.path.commonpath([root, path]) == root
        except ValueError:
            return False

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
        print("  nano <file>       Minimal line editor")
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

        print(f"\\n[nano] Editing: {os.path.relpath(target, self.console_root)}")
        print("[nano] Enter text. Footer commands: ^O save | ^X quit")
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
                out_path = target
                name_prompt = input("Write file name (blank keeps current): ").strip()
                if name_prompt:
                    maybe = self._safe_target(name_prompt)
                    if not maybe:
                        continue
                    out_path = maybe

                try:
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "w", encoding="utf-8") as f:
                        if buffer:
                            f.write("\\n".join(buffer) + "\\n")
                        else:
                            f.write("")
                    rel = os.path.relpath(out_path, self.console_root)
                    print(f"[nano] wrote {rel}")
                    target = out_path
                except OSError as exc:
                    print(f"Write error: {exc}")
                continue

            if normalized in quit_triggers:
                print("[nano] Exit editor")
                break

            buffer.append(line)

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

def launch_console(player_name: str, language: str, status_callback: Optional[Callable[[], None]] = None):
    shell = NeonConsole(player_name=player_name, language=language, status_callback=status_callback)
    shell.run()
