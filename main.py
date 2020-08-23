import cmd
import json
import os


class wShell(cmd.Cmd):
    prompt = str(os.getcwd()) + '>'
    aliases = {
        'exit': 'quit'
    }
    aliasfile = str(os.path.expanduser("~")) + "\\.alias.cfg"

    def emptyline(self):
        return

    def do_alias(self, args: str):  # TODO: clean this shit
        """Register or check a command alias. It autosaves it to the alias file.
      Usage: alias <alias> [command] [args...]"""
        l = args.split(' ')
        # print(l)
        if args == '':
            self.stdout.write(self.do_alias.__doc__)
            self.stdout.write(f"\nAliases: {str(self.aliases)}\n")
        else:
            cmd, arg, lin = self.parseline(args)
            if self.aliases.get(l[0], None):
                if len(l) < 2:
                    self.stdout.write(f'{l[0]}: {str(self.aliases.get(l[0], "You fucked up"))}')
                else:
                    self.stdout.write(
                        f'MODIFYING {l[0]}: {str(self.aliases.get(l[0], "?¿?¿Data race?"))} -> {str(arg)}')
                    self.aliases[l[0]] = arg
            else:
                print(arg)
                self.aliases[l[0]] = arg
            with open(self.aliasfile, 'w') as a:  # TODO (1): handle exceptions
                a.write(json.dumps(self.aliases))
                self.stdout.write("Aliases saved.\n")

        self.stdout.write("\n")

        return

    def do_unalias(self, args: str):
        """Unregister a command alias. It autosaves it to the alias file.
      Usage: unalias <alias>"""
        l = args.split(' ')
        # print(l)
        if args == '':
            self.stdout.write(self.do_alias.__doc__)
        else:
            cmd, arg, lin = self.parseline(args)
            if self.aliases.pop(l[0], None):
                self.stdout.write(f'"{l[0]}" removed.\n')
            else:
                self.stdout.write(f'{l[0]} was not an alias.\n')
            with open(self.aliasfile, 'w') as a:  # TODO (1): handle exceptions
                a.write(json.dumps(self.aliases))
                self.stdout.write("Aliases saved.\n")

        self.stdout.write("\n")

        return

    def do_quit(self, args: str):
        """Exit the program."""
        exit(0)

    def do_cd(self, args: str):
        """Changes the current working directory."""
        n = -1
        try:
            n = os.chdir(args)
        except OSError as e:
            n = e.errno
            self.stdout.write(f"cd: {e.strerror}\n\n")
        finally:
            return n

    def do_reloadalias(self, line: str):  # TODO (1): handle exceptions
        """Reloads the alias file and parses it into internal memory."""
        with open(self.aliasfile, 'r') as a:
            self.aliases = json.loads(a.read())
            self.stdout.write("Aliases reloaded. Running `alias`...\n")
            self.onecmd("alias")
        return 0

    def do_shell(self, line: str):
        return os.system(line)

    def command_in_path(self, exe):
        """Checks in every address in the system PATH enviroment variable whether the command exists or not. If it does,
        it executes it. Otherwise, returns False"""

        for path in os.environ['PATH'].split(";"):  # For each value in the PATH
            if not os.path.isdir(path):  # If the PATH address is not valid, move on
                continue

            if exe + '.exe' in os.listdir(path):  # However, if an executable file with the given name exists,
                return True   # Execute it with the given arguments

        return False  # Otherwise, return False (the command is not in PATH)

    def postcmd(self, stop, line: str):
        self.prompt = str(0 if stop is None else stop) + "<" + str(os.getcwd()) + ">"
        return

    def default(self, line: str):
        l = line.split(' ')
        if self.aliases.get(l[0], None):
            self.onecmd(self.aliases[l[0]])
        elif self.command_in_path(l[0]):
            return os.system(' '.join(l))
        else:
            super().default(line)

        return

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)
        if not (os.path.isfile(self.aliasfile)):
            self.stdout.write("Alias file not found, creating...\n")
            with open(self.aliasfile, 'a') as a:
                a.write(json.dumps(self.aliases))
        self.do_reloadalias("")


if __name__ == "__main__":
    wShell().cmdloop()
