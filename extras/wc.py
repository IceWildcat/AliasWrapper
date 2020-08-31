from main import wShell as sh
import os


arg_parsing = {
    'c': 'count_bytes',
    'm': 'count_chars',
    'l': 'count_newline',
    'w': 'count_words'
}


def count_newline(file):
    with open(file, 'r') as f:
        return len(f.readlines())


def count_bytes(file):
    return os.path.getsize(file)


def count_chars(file):
    count = 0
    with open(file, 'r') as f:
        for line in f.readlines():
            count += len(line)

        return count


def count_words(file):
    count = 0
    with open(file, 'r') as f:
        for line in f.readlines():
            count += len(line.split(" "))

        return count


def do_wc(args: str):
    # TODO: options (L)

    result = ""
    total = 0

    parameter = ""
    files = []
    buffer = "'"
    for arg in args.split(" "):
        if arg.startswith("-"):
            parameter = arg[1:]
            continue

        if '"' in arg or "'" in arg:
            buffer += arg.replace('"', '').replace("'", "")
            continue

        if not buffer == "'":
            files.append(buffer + "'")
            buffer = "'"

        files.append(arg)

    # TODO: support for stdin if FILE is -
    for file in files:
        if not os.path.exists(file):
            result += "wc: " + file + ": No such file or directory\n"
            continue

        if parameter not in arg_parsing:
            sh.print("wc: Unknown parameter '" + parameter + "'")
            return 2

        # TODO: this is a lazy fix, eval is easily exploitable
        count = eval(arg_parsing[parameter] + "(" + file + ")")
        total += count
        result += str(count) + " " + file + "\n"

    if len(files) > 1:
        result += str(count) + " total"

    sh.print(result)


    return 0
