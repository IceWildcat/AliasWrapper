from main import wShell as sh


def reformat_test(test: str):
    # -eq, -ne, -lt, -le, -gt, or -ge

    if '-ne' in test.split(" "):
        test = "not " + test.replace("-ne", "==")

    test = test.replace("-eq", "==")
    test = test.replace("-lt", "<")
    test = test.replace("-le", "<=")
    test = test.replace("-gt", ">")
    test = test.replace("-ge", ">=")
    test = test.replace("-o", " or ")
    test = test.replace("-a", " and ")
    test = test.replace("!", "not ")

    return test


def arithmetic_test(test: str):
    return 0 if eval(sh.reformat_test(test)) else 1


def do_test(args: str):
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
        return sh.arithmetic_test(args)

    return 3


def is_assignment(line: str):
    if re.match("^[A-Za-z]+[A-Za-z0-9]*[=][\"][A-Za-z0-9]+[\"]$", line):
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
