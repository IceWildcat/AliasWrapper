import cmd
import os
import json
import re
import stat


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

    regex_path = r"\"?([A-Z]:)?((\/|\\)[^\/\:\*\?\!\<\>\|]*)*(.[a-z0-9]+)?\"?"
    regex_value = "(\\$[A-Za-z0-9]+|-?[0-9]+)"
    regex_string = '"[^"]*"'

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

    def do_pushd(self, args: str):  # TODO: arguments  [-n] [+N | -N | dir]
        """Save the current directory into a stack and move to a new directory.
        Usage: pushd [-n] [+N | -N | dir]"""
        if not os.path.isdir(args):
            return 1  # TODO: Error message

        self.remembered_dirs.append(args)
        self.cmdqueue.append("dirs")
        self.cmdqueue.append("cd " + args)

    def do_popd(self, args: str):  # TODO: arguments [-n] [+N | -N]
        """popd can be used to return back to the previous directory that is on top of the stack.
        Usage: popd [-n] [+N | -N]"""
        if len(self.remembered_dirs) == 0:
            return 1  # TODO: Error message

        dir_pop = self.remembered_dirs.pop()
        self.stdout.write(f'{dir_pop}\n')
        self.cmdqueue.append("cd " + dir_pop)

    def do_dirs(self, args: str):  # TODO: arguments: [-clpv] [+N] [-N]
        """Display the list of currently remembered directories. By default, it includes the directory you are currently in. A directory can get into the list via pushd command followed by the dir name and can be removed via popd command.
        Usage: dirs  [-clpv] [+N] [-N]"""
        if len(args) == 1:
            args_list = [arg for arg in args if not arg == '-']

            if 'c' in args_list:
                self.remembered_dirs = [os.getcwd()]
                return 0

        dir_output = "\t".join(self.remembered_dirs) + "\t" + os.getcwd()
        self.stdout.write(f'{dir_output}\n')

    def do_echo(self, args: str):  # TODO: options
        """Writes its arguments to standard output.
        Usage: echo [option(s)] [string(s)]"""
        args_processed = self.replace_variables(args)
        self.stdout.write(f"{args_processed}\n")

    def do_cd(self, args: str):  # TODO: options
        """Changes the current working directory.
        Usage: cd [option] [directory]"""
        n = -1
        try:
            os.chdir(args)
            n = 0
        except OSError as e:
            n = e.errno
            self.stdout.write(f"cd: {e.strerror}\n\n")
        finally:
            return n

    def arithmetic_logic(self, args: str):
        # -eq, -ne, -lt, -le, -gt, or -ge

        if '-ne' in args.split(" "):
            args = "not " + args.replace("-ne", "==")

        args = args.replace("-eq", "==")
        args = args.replace("-lt", "<")
        args = args.replace("-le", "<=")
        args = args.replace("-gt", ">")
        args = args.replace("-ge", ">=")
        args = args.replace("!", "not ")

        return 0 if eval(args) else 1

    def file_logic(self, args: str):
        split = args.split(" ")
        file = split[1]

        if split[0] == '-b':                            # File is block device
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISBLK(mode) else 1
        elif split[0] == '-c':                          # File is a character device
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISCHR(mode) else 1
        elif split[0] == '-d':                          # Path is a directory
            return 0 if os.path.isdir(file) else 1
        elif split[0] == '-e':                          # Path exists
            return 0 if os.path.exists(file) else 1
        elif split[0] == '-f':                          # Path is file
            return 0 if os.path.isfile(file) else 1
        elif split[0] == '-g':                          # set-group-id (sgid) flag set on file or directory
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISGID(mode) else 1
        elif split[0] == '-G':                          # group-id of file same as yours
            gid = os.stat(file).st_gid
            return 0 if gid == os.getgid() else 1
        elif split[0] == '-h' or split[0] == '-L':      # File is a symbolic link
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISLNK(mode) else 1
        elif split[0] == '-k':                          # sticky bit set
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISVTX(mode) else 1
        elif split[0] == '-N':                          # File modified since it was last read
            last_modified = os.path.getmtime(file)
            last_read = os.path.getatime(file)
            return 0 if last_read < last_modified else 1
        elif split[0] == '-O':                          # You are owner of file
            uid = os.stat(file).st_uid
            return 0 if uid == os.getuid() else 1
        elif split[0] == '-p':                          # File is a pipe TODO: check logic
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISFIFO(mode) else 0
        elif split[0] == '-r':                          # File has read permission (for the user running the test)
            return 0 if os.access(file, os.R_OK) else 1
        elif split[0] == '-s':                          # File is not zero size
            return os.path.getsize(file)
        elif split[0] == '-S':                          # File is a socket
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISSOCK(mode) else 1
        elif split[0] == '-t':                          # TODO: File (descriptor) is associated with a terminal device
            self.stdout.write(f"Unimplemented method\n")
            return 3
        elif split[0] == '-u':                          # set-user-id (suid) flag set on file
            mode = os.stat(file).st_mode
            return 0 if stat.S_ISUID(mode) else 1
        elif split[0] == '-w':                          # File has write permission (for the user running the test)
            return 0 if os.access(file, os.W_OK) else 1
        elif split[0] == '-x':                          # File has execute permission (for the user running the test)
            return 0 if os.access(file, os.X_OK) else 1

        return 2

    def string_logic(self, args: str):
        return 0

    def replace_variables(self, args: str):
        expr = ""
        for thing in args.split(" "):
            if thing.startswith('$'):
                if not self.variables[thing[1:]]:
                    return 3
                else:
                    expr += str(self.variables[thing[1:]]) + " "
            else:
                expr += thing + " "

        return expr

    def do_test(self, args: str):
        processed_line = self.replace_variables(args)

        if re.fullmatch("^" + self.regex_value + " -(eq|ne|le|lt|ge|gt) " + self.regex_value + "$", args):
            return self.arithmetic_logic(processed_line)
        elif re.fullmatch('^-([b-h]|G|k|L|O|p|[r-u]|S|w|x) ' + self.regex_path + '$', args):
            return self.file_logic(processed_line)
        elif re.fullmatch('^-[zn] ' + self.regex_string + '$', args) or \
                re.fullmatch('^' + self.regex_string + ' ?!?= ?' + self.regex_string + '$', args):
            return self.string_logic(processed_line)

        print("other")

        return 3

    def is_assignment(self, line: str):
        if re.fullmatch("^[A-Za-z]+[A-Za-z0-9]*[=][\"][A-Za-z0-9]+[\"]$", line):
            split = line.split("=")
            var_name = split[0]
            var_value = split[1]

            self.variables[var_name] = var_value

            return True
        elif re.match("^[A-Za-z]+[A-Za-z0-9]*[=][A-Za-z0-9]+$", line):
            split = line.split("=")
            var_name = split[0]
            var_value = split[1]

            self.variables[var_name] = float(var_value)

            return True

        return False

    def do_cat(self, args: str):
        """It has three related functions with regard to text files: displaying them, combining copies of them and creating new ones.
        Usage: cat [options] [filenames] [-] [filenames]"""
        args_split = args.split(" ")
        args_list = [arg for arg in args_split[0] if not arg == '-'] if args_split[0].startswith('-') else None
        files = [f for f in args_split if not f.startswith('-')]

        for f in files:
            n = 0
            if not os.path.isfile(f):
                return 1  # TODO: Error message

            file = open(f, 'r')
            for line in file.readlines():  # TODO: possible optimization(?)
                if args_list is not None and 'n' in args_list:
                    n += 1
                    self.stdout.write(f'{str(n) + ") " + line}')
                else:
                    self.stdout.write(f'{line}')

            file.close()
            self.stdout.write('\n\n')

    def ls_logic(self, filename, args_list):  # TODO: flags dFil[a,h,s]rRsStX
        """Given a file name and the argument list, determines if it sould be shown or not.
        :param filename: Name of the file being evaluated
        :param args_list: List of arguments
        :return: True (show file) | False (don't show file)
        """
        return 'a' in args_list or not filename.startswith('.')  # If not flag 'a', show only not hidden files

    def do_ls(self, args: str):
        """List files and directories.
        Usage: ls [options] [directory]"""
        ls_dir = '../built_in'
        if len(args.split(" ")) > 2:
            args_split = args.split(" ")
            args_index = 0 if args_split[0].startswith('-') else 1  # Find the index for the flags

            args_list = [arg for arg in args_split[args_index] if
                         not arg == '-']  # With that index, get the flags as a list

            ls_dir = args_split[1 - args_index]  # The directory is the other argument

            if os.path.isdir(ls_dir):  # If the directory does not exist, return error
                return 1  # TODO: Error message

        else:
            args_list = [arg for arg in args
                         if not arg == '-']  # If there is only one argument (or none) it is much more straight-forward

        # Get a sorted list of all the files inside the directory.
        files = sorted([f for f in os.listdir(ls_dir) if self.ls_logic(f, args_list)], key=lambda f: f.lower())
        # print(*files, sep='\t\t')  # TODO: Wrap the lines

        files_output = "\t\t".join(files)
        self.stdout.write(f'{files_output}\n')

        return 0  # Success

    def command_in_path(self, exe: str):
        """Checks in every address in the system PATH enviroment variable whether the command exists or not.
        :param exe: Program name without extension
        :return: True (exists) | False (not exists)"""
        # TODO: make platform-independant?
        for path in os.environ['PATH'].split(";"):  # For each value in the PATH
            if not os.path.isdir(path):  # If the PATH address is not valid, move on
                continue

            if exe + '.exe' in os.listdir(
                    path):  # However, if an executable file with the given name exists, return True
                return True

        return False  # Otherwise, return False (the command is not in PATH)

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
        self.do_reloadalias("")

        self.variables["?"] = "0"
        self.variables["BASHPID"] = os.getpid()
        self.variables["$"] = os.getpid()
        self.variables["HISTFILE"] = os.getcwd() + ".bash_history"


if __name__ == "__main__":
    wShell().cmdloop()
