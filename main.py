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
        args_list = args.split(' ')
        # print(l)
        if args == '':
            self.stdout.write(self.do_alias.__doc__)
            self.stdout.write(f"\nAliases: {str(self.aliases)}\n")
        else:
            cmd, arg, lin = self.parseline(args)
            if self.aliases.get(args_list[0], None):
                if len(args_list) < 2:
                    self.stdout.write(f'{args_list[0]}: {str(self.aliases.get(args_list[0], "You fucked up"))}')
                else:
                    self.stdout.write(
                        f'MODIFYING {args_list[0]}: {str(self.aliases.get(args_list[0], "?¿?¿Data race?"))} -> {str(arg)}')
                    self.aliases[args_list[0]] = arg
            else:
                print(arg)
                self.aliases[args_list[0]] = arg
            with open(self.aliasfile, 'w') as a:  # TODO (1): handle exceptions
                a.write(json.dumps(self.aliases))
                self.stdout.write("Aliases saved.\n")

        self.stdout.write("\n")

        return

    def do_ls(self, args: str):  # TODO: flags dFil[a,h,s]rRsStX
        ls_dir = '.'
        if len(args) > 1:
            args_index = 0 if args[0].startswith('-') else 1  # Find the index for the flags

            args_list = [arg for arg in args[args_index] if not arg == '-']  # With that index, get the flags as a list

            ls_dir = args[1 - args_index]  # The directory is the other argument

            if os.path.isdir(ls_dir):  # If the directory does not exist, return error
                return 1

        else:
            args_list = [arg for arg in args
                         if not arg == '-']  # If there is only one argument (or none) it is much more straight-forward

        # Get a sorted list of all the files inside the directory.
        files = sorted([f for f in os.listdir(ls_dir)
                        if ('a' in args_list or not f.startswith('.'))  # If not flag 'a', show only not hidden files
                        ], key=lambda f: f.lower())
        # print(*files, sep='\t\t')  # TODO: Wrap the lines

        files_output = "\t\t".join(files)
        self.stdout.write(f'{files_output}\n')

        return 0  # Success

    def do_unalias(self, args: str):
        """Unregister a command alias. It autosaves it to the alias file.
      Usage: unalias <alias>"""
        args_list = args.split(' ')
        # print(l)
        if args == '':
            self.stdout.write(self.do_alias.__doc__)
        else:
            cmd, arg, lin = self.parseline(args)
            if self.aliases.pop(args_list[0], None):
                self.stdout.write(f'"{args_list[0]}" removed.\n')
            else:
                self.stdout.write(f'{args_list[0]} was not an alias.\n')
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
            os.chdir(args)
            n = 0
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

    def command_in_path(self, exe: str):
        """Checks in every address in the system PATH enviroment variable whether the command exists or not. If it does,
        it executes it. Otherwise, returns False"""

        for path in os.environ['PATH'].split(";"):  # For each value in the PATH
            if not os.path.isdir(path):  # If the PATH address is not valid, move on
                continue

            if exe + '.exe' in os.listdir(
                    path):  # However, if an executable file with the given name exists, return True
                return True

        return False  # Otherwise, return False (the command is not in PATH)

    def postcmd(self, stop, line: str):
        self.prompt = str(0 if stop is None else stop) + "<" + str(os.getcwd()) + ">"
        return

    def default(self, line: str):
        args_list = line.split(' ')
        if self.aliases.get(args_list[0], None):
            self.onecmd(self.aliases[args_list[0]])
        elif self.command_in_path(args_list[0]) or os.path.isfile(args_list[0]):
            # If the command is a file found in the PATH or the command itself is a file, execute it as is
            return self.do_shell(' '.join(args_list))
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
