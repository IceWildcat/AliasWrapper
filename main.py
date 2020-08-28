import cmd
import os
import json
from functools import wraps

def add_method(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func  # returning func means func can still be used normally
    return decorator


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
    commands_temp_history = ""
    command_history_count = 0

    def emptyline(self):
        return

    def do_quit(self, args: str):
        """Exit the program."""

        # Record history on log file (.bash_history)
        with open(self.variables['HISTFILE'], 'a+') as f:
            f.write(self.commands_temp_history)

        exit(0)

    def do_shell(self, line: str):
        return os.system(line)

    def postcmd(self, stop, line: str):
        # Record history on temporal variable
        self.commands_temp_history += "\t" + str(self.command_history_count) + "\t" + line + "\r\n"

        exit_status = 0 if stop is None else stop
        self.prompt = str(exit_status) + "<" + str(os.getcwd()) + ">"
        self.variables["?"] = exit_status
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
            self.stdout.write("Alias file not found, creating...\n")
            with open(self.aliasfile, 'a') as a:
                a.write(json.dumps(self.aliases))
        __do_reloadalias = getattr(self, 'do_reloadalias', None)
        if(__do_reloadalias):
            __do_reloadalias("")
        else:
            self.stdout.write("ERROR: cannot reload aliases!\n")

        self.variables["?"] = "0"
        self.variables["BASHPID"] = os.getpid()
        self.variables["$"] = os.getpid()
        self.variables["HISTFILE"] = os.getcwd() + ".bash_history"


if __name__ == "__main__":
    wShell().cmdloop()
