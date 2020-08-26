from main import wShell as sh
import re
import os

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
    file = split[0]

    if split[0] == '-e':
        return 0 if os.path.isfile(file) or os.path.isdir(file) else 1

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
