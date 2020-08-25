import cmd
import os
import json


class wShell(cmd.Cmd):
    prompt = str(os.getcwd()) + '>'
    aliases = {
        'exit': 'quit'
    }
    aliasfile = str(os.path.expanduser("~")) + "\\.alias.cfg"

    variables = {}
    last_exit_status = 0
    remembered_dirs = [os.getcwd()]
    arithmetic_ops = ["-eq", "-ne", "-lt", "-le", "-gt", "-ge"]

    from built_in import alias, cd, dirs, echo, logic
    from extras import cat, ls, path

    @staticmethod
    def emptyline():
        return

    @staticmethod
    def do_quit(args: str):
        """Exit the program."""
        exit(0)

    @staticmethod
    def do_shell(line: str):
        return os.system(line)

    def postcmd(self, stop, line: str):
        self.prompt = str(0 if stop is None else stop) + "<" + str(os.getcwd()) + ">"
        return

    def default(self, line: str):
        args_list = line.split(' ')
        if self.aliases.get(args_list[0], None):
            self.onecmd(self.aliases[args_list[0]])
        elif logic.is_assignment(line):
            print(self.variables)
        elif path.command_in_path(args_list[0]) or os.path.isfile(args_list[0]):
            # If the command is a file found in the PATH or the command itself is a file, execute it as is
            return self.do_shell(' '.join(args_list))
        else:
            super().default(line)

        return

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)
        if not (os.path.isfile(self.aliasfile)):
            stdout.write("Alias file not found, creating...\n")
            with open(self.aliasfile, 'a') as a:
                a.write(json.dumps(self.aliases))
        alias.do_reloadalias("")


if __name__ == "__main__":
    wShell().cmdloop()
