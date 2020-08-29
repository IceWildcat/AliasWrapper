import cmd
import importlib.util
import json
import os
from functools import wraps


funcfolders = ['built_in', 'extras']


def selfwrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


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
    commands_temp_history = []

    def emptyline(self):
        return

    def do_quit(self, args: str):
        """Exit the program."""

        # TODO: Optimization
        # Record history on log file (.bash_history)
        with open(self.variables['HISTFILE'], 'w') as f:
            f.write(self.get_formatted_history())

        exit(0)

    def system_var(self, name):
        if name == '?':
            return self.last_exit_status

        if name == 'BASHPID':
            return os.getpid()

        if name == '$':
            return os.getpid()

        if name == 'PWD':
            return os.getcwd()

        if name == 'HISTSIZE':
            return os.path.getsize(self.variables['HISTFILE'])

        return ""

    def replace_variables(self, args: str):
        expr = ""
        status = 0

        for thing in args.split(" "):
            if thing.startswith('$'):
                if thing[1:] in self.variables:
                    expr += str(self.variables[thing[1:]]) + " "
                else:
                    value = self.system_var(thing[1:])

                    if not value:
                        status = 3

                    expr += str(value) + " "
            else:
                expr += thing + " "

        return expr, status

    def get_formatted_history(self):
        hist = ""
        count = 0
        for command in self.commands_temp_history:
            hist += "\t" + str(count) + "\t" + command + "\n"
            count += 1

        return hist

    def do_history(self, args: str):
        self.stdout.write(f'{self.get_formatted_history()}\n')
        return 0

    def do_shell(self, line: str):
        return os.system(line)

    def postcmd(self, stop, line: str):
        # Record history on temporal variable
        self.commands_temp_history.append(line)

        exit_status = 0 if stop is None else stop

        self.prompt = str(exit_status) + "<" + str(os.getcwd()) + ">"
        self.variables["?"] = exit_status

        return

    def default(self, line: str):
        args_list = line.split(' ')
        if self.aliases.get(args_list[0], None):
            self.onecmd(self.aliases[args_list[0]])
        elif self.is_assignment(line):
            pass
        elif self.command_in_path(args_list[0]) or os.path.isfile(args_list[0]):
            # If the command is a file found in the PATH or the command itself is a file, execute it as is
            return self.do_shell(' '.join(args_list))
        else:
            super().default(line)

        return

    loadedmodules = []

    def loadmodule(self, name: str):
        # TODO: check if module is already loaded
        spec = importlib.util.find_spec(name)
        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)
        self.loadedmodules.append(lib)
        setattr(lib, 'sh', self)  # Hacky thing to pass the wShell instance to the module
        for thing in dir(lib):
            if not str(thing).startswith('_'):
                doelement = getattr(lib, thing)
                if callable(doelement):
                    setattr(wShell, doelement.__name__, selfwrap(doelement))
                    # print(doelement.__name__)

        return

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)
        if not (os.path.isfile(self.aliasfile)):
            self.stdout.write("Alias file not found, creating...\n")
            with open(self.aliasfile, 'a') as a:
                a.write(json.dumps(self.aliases))

        # O(n^2 for the win)
        for foldname in funcfolders:
            with os.scandir(foldname) as folder:
                for fil in folder:
                    if fil.is_dir():
                        continue  # TODO: recursion over folders maybe?
                    if fil.name.endswith('.py'):
                        importname = foldname + '.' + fil.name[:-3]  # remove '.py' from filename
                        try:
                            self.loadmodule(importname)
                        except Exception as e:
                            print('Oops,something went poof.')
                            # TODO: handle exceptions at importing the modules
                            raise e

        # That shit went too deep sorry im at phone

        __do_reloadalias = getattr(self, 'do_reloadalias', None)
        if __do_reloadalias:
            __do_reloadalias("")
        else:
            self.stdout.write("ERROR: cannot reload aliases!\n")

        self.variables["HISTFILE"] = os.getcwd() + "\\.bash_history"

        # TODO: Optimization
        # Load the command history
        with open(self.variables["HISTFILE"], 'r') as f:
            for line in f.readlines():
                split = line.split("\t")[1:]
                number = split[0]
                command = split[1].replace("\n", "")
                self.commands_temp_history.append(command)


if __name__ == "__main__":
    wShell().cmdloop()
