from main import wShell as sh
import re  # Regex support
import os
import stat

# TODO: Explanation of the regex(?)
regex_path = r"\"?([A-Z]:)?((\/|\\)[^\/\:\*\?\!\<\>\|]*)*(.[a-z0-9]+)?\"?"
regex_value = "(\\$[A-Za-z0-9]+|-?[0-9]+)"
regex_string = '"[^"]*"'


# TODO: check logic
def arithmetic_logic(args: str):
    # -eq, -ne, -lt, -le, -gt, or -ge

    if '-ne' in expr.split(" "):
        expr = "not " + expr.replace("-ne", "==")

    expr = expr.replace("-eq", "==")
    expr = expr.replace("-lt", "<")
    expr = expr.replace("-le", "<=")
    expr = expr.replace("-gt", ">")
    expr = expr.replace("-ge", ">=")
    expr = expr.replace("!", "not ")

    return 0 if eval(expr) else 1


def file_logic(args: str):
    split = args.split(" ")
    file = split[1]

    if split[0] == '-b':                                    # File is block device
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISBLK(mode) else 1
    elif split[0] == '-c':                                  # File is a character device
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISCHR(mode) else 1
    elif split[0] == '-d':                                  # Path is a directory
        return 0 if os.path.isdir(file) else 1
    elif split[0] == '-e':                                  # Path exists
        return 0 if os.path.exists(file) else 1
    elif split[0] == '-f':                                  # Path is file
        return 0 if os.path.isfile(file) else 1
    elif split[0] == '-g':                                  # set-group-id (sgid) flag set on file or directory
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISGID(mode) else 1
    elif split[0] == '-G':                                  # group-id of file same as yours
        gid = os.stat(file).st_gid
        return 0 if gid == os.getgid() else 1
    elif split[0] == '-h' or split[0] == '-L':              # File is a symbolic link
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISLNK(mode) else 1
    elif split[0] == '-k':                                  # sticky bit set
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISVTX(mode) else 1
    elif split[0] == '-N':                                  # File modified since it was last read
        last_modified = os.path.getmtime(file)
        last_read = os.path.getatime(file)
        return 0 if last_read < last_modified else 1
    elif split[0] == '-O':                                  # You are owner of file
        uid = os.stat(file).st_uid
        return 0 if uid == os.getuid() else 1
    elif split[0] == '-p':                                  # File is a pipe TODO: check logic
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISFIFO(mode) else 0
    elif split[0] == '-r':                                  # File has read permission (for the user running the test)
        return 0 if os.access(file, os.R_OK) else 1
    elif split[0] == '-s':                                  # File is not zero size
        return os.path.getsize(file)
    elif split[0] == '-S':                                  # File is a socket
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISSOCK(mode) else 1
    elif split[0] == '-t':                                  # TODO: File (descriptor) is associated with a terminal device
        sh.stdout.write(f"Unimplemented method\n")
        return 3
    elif split[0] == '-u':                                  # set-user-id (suid) flag set on file
        mode = os.stat(file).st_mode
        return 0 if stat.S_ISUID(mode) else 1
    elif split[0] == '-w':                                  # File has write permission (for the user running the test)
        return 0 if os.access(file, os.W_OK) else 1
    elif split[0] == '-x':                                  # File has execute permission (for the user running the test)
        return 0 if os.access(file, os.X_OK) else 1

    return 2


def string_logic(args: str):
    return 0


def replace_variables(args: str):
    expr = ""
    for thing in args.split(" "):
        if thing.startswith('$'):
            if not sh.variables[thing[1:]]:
                return 3
            else:
                expr += str(sh.variables[thing[1:]]) + " "
        else:
            expr += thing + " "

    return expr


def do_test(args: str):
    processed_line = replace_variables(args)

    if re.fullmatch("^" + regex_value + " -(eq|ne|le|lt|ge|gt) " + regex_value + "$", args):
        return arithmetic_logic(processed_line)
    elif re.fullmatch('^-([b-h]|G|k|L|O|p|[r-u]|S|w|x) ' + regex_path + '$', args):
        return file_logic(processed_line)
    elif re.fullmatch('^-(z|n) ' + regex_string + '$', args) or \
            re.fullmatch('^' + regex_string + ' ?!?= ?' + regex_string + '$', args):
        return string_logic(processed_line)
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
        return arithmetic_logic(reformat_test(args))

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
