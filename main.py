import cmd
import json
import os
import re


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

    import built_in
    # from built_in import alias, cd, dirs, echo, test

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

    @staticmethod
    def command_in_path(exe: str):
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
        elif self.is_assignment(line):
            print(self.variables)
        elif self.command_in_path(args_list[0]) or os.path.isfile(args_list[0]):
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
        do_reloadalias("")


if __name__ == "__main__":
    wShell().cmdloop()
