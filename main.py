import cmd
import importlib.util
import json
import os
import re
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
    aliasfile = os.path.join(os.path.expanduser('~'), '.alias.cfg')

    # TODO: Explanation of the regex(?)
    regex_folder = r"\"?([A-Z]:)?((\/|\\)[^\/\:\*\?\!\<\>\|]*)+\"?"
    regex_path = r"\"?([A-Z]:)?((\/|\\)[^\/\:\*\?\!\<\>\|]*)*(.[\w]+)?\"?"
    regex_value = r"(\\$[\w]+|-?[0-9]+)"
    regex_variable = r"\$[\w]+"
    regex_string = r'"[^"]*"'

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

    def command_in_path(self, command: str):
        path_str = os.environ["PATH"]

        # WARNING! Order matters here because windows is separated by ';', but contains ':' (C:\...)
        if ';' in path_str:
            folders = path_str.split(";")
        else:
            folders = path_str.split(";")

        # TODO: Optimization
        for folder in folders:
            if not os.path.exists(folder):
                continue

            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)

                if not os.path.exists(file_path):
                    print(file + " does not exist")
                    continue

                if not file.find(command) == -1 and os.access(file_path, os.X_OK):
                    return True

        return False

    def system_var(self, name, args=""):
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

        if name == '*':
            # TODO: Unexpected result(?)
            return args

        if name == 'PATH':
            return os.environ['PATH']

        return ""

    # TODO: recognice variables not separated by spaces
    def replace_variables(self, args: str):
        expr = args
        status = 0

        for thing in re.finditer(self.regex_variable, args):
            if thing.group()[1:] in self.variables:
                expr = expr.replace(thing[0], str(self.variables[thing[0][1:]]))
            else:
                value = self.system_var(thing[0][1:])

                if not value:
                    status = 3
                else:
                    expr = expr.replace(thing[0], str(value))

        return expr, status

    def is_assignment(self, line: str):
        if re.fullmatch("^[A-Za-z_]\\w* ?= ?(\")?[^\"]+(\")?$", line):
            split = line.split("=")
            var_name = split[0]
            if var_name.endswith(" "):
                var_name = var_name[:-1]

            var_value = split[1]
            if var_value.startswith(" "):
                var_value = var_value[1:]

            self.variables[var_name] = var_value

            return True

        return False

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

    def do_reloadalias(self, line: str):  # TODO (1): handle exceptions
        """Reloads the alias file and parses it into internal memory."""
        with open(self.aliasfile, 'r') as a:
            self.aliases = json.loads(a.read())
            self.stdout.write("Aliases reloaded. Running `alias`...\n")
            self.onecmd("alias")
        return 0

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

    def populate_vars(self, args_list: list):
        args_number = len(args_list) - 1
        self.variables['#'] = args_number

        for arg_n in range(0, args_number + 1):
            self.variables[str(arg_n)] = args_list[arg_n]

        # If there are previous values for more arguments, delete them
        if str(args_number + 1) in self.variables:
            n = args_number + 1
            while str(n) in self.variables:
                self.variables.pop(str(n))
                n += 1

    def do_shell(self, line: str):
        return os.system(line)

    def precmd(self, line: str):
        if "&&" in line:
            split = line.split("&&")
            for command in split[1:]:
                self.cmdqueue.append(command)

            return split[0]

        # TODO: do this only if calling a script or similar
        self.populate_vars(line.split(' '))
        args_processed, exit_status = self.replace_variables(line)
        return args_processed

    def postcmd(self, stop, line: str):
        # Record history on temporal variable
        self.commands_temp_history.append(line)

        exit_status = 0 if stop is None else stop

        self.prompt = str(exit_status) + "<" + str(os.getcwd()) + ">"
        self.variables["?"] = exit_status

        return

    def default(self, line: str):
        args_list = line.split(' ')

        # COMMAND CHECKING
        if self.aliases.get(args_list[0], None):
            self.onecmd(self.aliases[args_list[0]])
        elif self.is_assignment(line):
            pass
        elif (os.path.isfile(args_list[0]) and os.access(args_list[0], os.X_OK)) or self.command_in_path(args_list[0]):
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

        # TODO: O(n^2 for the win)
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

        self.do_reloadalias("")

        self.variables["HISTFILE"] = os.path.join(os.getcwd(), '.bash_history')

        # TODO: Optimization
        # Load the command history
        if os.path.isfile(self.variables["HISTFILE"]):
            with open(self.variables["HISTFILE"], 'r') as f:
                for line in f.readlines():
                    split = line.split("\t")[1:]
                    number = split[0]
                    command = split[1].replace("\n", "")
                    self.commands_temp_history.append(command)


if __name__ == "__main__":
    wShell().cmdloop()
