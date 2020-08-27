from main import wShell as sh
import re  # Regex support
import os
import stat

# TODO: Explanation of the regex(?)
regex_path = r"\"?([A-Z]:)?((\/|\\)[^\/\:\*\?\!\<\>\|]*)*(.[a-z0-9]+)?\"?"
regex_value = "(\\$[A-Za-z0-9]+|-?[0-9]+)"
regex_string = '"[^"]*"'


# TODO: check logic
def arithmetic_test(test: str):
    # -eq, -ne, -lt, -le, -gt, or -ge

    expr = ""
    for thing in test.split(" "):
        if thing.startswith('$'):
            if not sh.variables[thing[1:]]:
                return 3
            else:
                expr += str(sh.variables[thing[1:]]) + " "
        else:
            expr += thing + " "

    if '-ne' in expr.split(" "):
        expr = "not " + expr.replace("-ne", "==")

    expr = expr.replace("-eq", "==")
    expr = expr.replace("-lt", "<")
    expr = expr.replace("-le", "<=")
    expr = expr.replace("-gt", ">")
    expr = expr.replace("-ge", ">=")
    expr = expr.replace("!", "not ")

    return 0 if eval(expr) else 1


# TODO: support for all the arguments
def file_test(test: str):
    split = test.split(" ")
    file = split[1]

    if split[0] == '-b':                                    # File is block device
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISBLK(mode) else 0
    elif split[0] == '-c':                                  # File is a character device
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISCHR(mode) else 0
    elif split[0] == '-d':                                  # Path is a directory
        return 0 if os.path.isdir(file) else 1
    elif split[0] == '-e':                                  # Path exists
        return 0 if os.path.exists(file) else 1
    elif split[0] == '-f':                                  # Path is file
        return 0 if os.path.isfile(file) else 1
    elif split[0] == '-g':                                  # TODO: set-group-id (sgid) flag set on file or directory
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-G':                                  # TODO: group-id of file same as yours
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-h' or split[0] == '-L':              # File is a symbolic link
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISLNK(mode) else 0
    elif split[0] == '-k':                                  # sticky bit set
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISVTX(mode) else 0
    elif split[0] == '-N':                                  # TODO: File modified since it was last read
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-O':                                  # You are owner of file
        uid = os.stat(file).st_uid
        return 0 if uid == os.getuid() else 1
    elif split[0] == '-p':                                  # TODO: File is a pipe
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-r':                                  # File has read permission (for the user running the test)
        return 0 if os.access(file, os.R_OK) else 1
    elif split[0] == '-s':                                  # File is not zero size
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-S':                                  # TODO: File is a socket
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-t':                                  # TODO: File (descriptor) is associated with a terminal device
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-u':                                  # TODO: set-user-id (suid) flag set on file
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-w':                                  # File has write permission (for the user running the test)
        return 0 if os.access(file, os.W_OK) else 1
    elif split[0] == '-x':                                  # File has execute permission (for the user running the test)
        return 0 if os.access(file, os.X_OK) else 1

    return 2


# TODO: String logic

def do_test(args: str):
    if re.fullmatch("^" + regex_value + " -(eq|ne|le|lt|ge|gt) " + regex_value + "$", args):
        return arithmetic_test(args)
    elif re.fullmatch('^-([b-h]|G|k|L|O|p|[r-u]|S|w|x) ' + regex_path + '$', args):
        print("file")
    elif re.fullmatch('^-(z|n) ' + regex_string + '$', args) or \
            re.fullmatch('^' + regex_string + ' ?!?= ?' + regex_string + '$', args):
        print("String")
    else:
        print("other")

    args_split = args.split(" ")
    operators = -1

    i = 0
    for arg in args_split:
        if arg.startswith('-'):
            operators = i
            break

        i += 1

    if operators == -1:
        return 2  # TODO: Error message

    if operators > 0 and args_split[operators] in sh.arithmetic_ops:
        return arithmetic_test(reformat_test(args))

    return 3


def is_assignment(line: str):
    if re.fullmatch("^[A-Za-z]+[A-Za-z0-9]*[=][\"][A-Za-z0-9]+[\"]$", line):
        split = line.split("=")
        var_name = split[0]
        var_value = split[1]

        sh.variables[var_name] = var_value

        return True
    elif re.match("^[A-Za-z]+[A-Za-z0-9]*[=][A-Za-z0-9]+$", line):
        split = line.split("=")
        var_name = split[0]
        var_value = split[1]

        sh.variables[var_name] = float(var_value)

        return True

    return False
