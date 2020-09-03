from main import wShell as sh
import os

# TODO: options (L)
arg_parsing = {
    'c': 'count_bytes',
    'm': 'count_chars',
    'l': 'count_newline',
    'w': 'count_words'
}


def count_newline(args):
    if os.path.isfile(args):
        with open(args, 'r') as f:
            return len(f.readlines())
    else:
        return len(args.split("\n"))


def count_bytes(args):
    if os.path.isfile(args):
        return os.path.getsize(args)
    else:
        return len(args)


def count_chars(args):
    if os.path.isfile(args):
        count = 0
        with open(args, 'r') as f:
            for line in f.readlines():
                count += len(line)

            return count
    else:
        return len(args)


def count_words(args):
    if os.path.isfile(args):
        count = 0
        with open(args, 'r') as f:
            for line in f.readlines():
                count += len(line.split(" "))

            return count
    else:
        return len(args.split(" "))


def do_wc(args: str):
    args_split = args.split(" ")

    parameter = ""
    result = ""

    if args_split[0].startswith("-"):
        parameter = args_split[0][1:]
        args = " ".join(args_split[1:])

        if parameter not in arg_parsing:
            sh.print("wc: Unknown parameter '" + parameter + "'")
            return 2

    if parameter == "":
        result = "Newline\t\tWord\t\tByte\n"
        total = [0, 0, 0]
    else:
        total = 0

    # TODO: lazy way to differenciate if input is a list of files or coming from a pipe
    if sh.output is None:
        # TODO: support for paths surrounded by "
        files = [f for f in args_split if not f.startswith("-")]
        for file in files:
            if not os.path.exists(file):
                result += "wc: " + file + ": No such file or directory\n"
                continue

            # TODO: this is a lazy fix, eval is easily exploitable
            if parameter == "":
                # newline, word, and byte
                count = [count_newline(file),
                         count_words(file),
                         count_bytes(file)]

                total = [sum(i) for i in zip(count, total)]
                result += "\t\t".join([str(item) for item in count]) + "\t\t" + file + "\n"
            else:
                count = eval(arg_parsing[parameter] + "(" + file + ")")
                total += count
                result += str(count) + "\t\t" + file + "\n"

        if len(files) > 1:
            if parameter == "":
                result += "\t".join([str(item) for item in total]) + " total\n"
            else:
                result += str(total) + " total\n"
    else:
        if parameter == "":
            # newline, word, and byte
            count = [count_newline(args),
                     count_words(args),
                     count_bytes(args)]

            result += "\t\t".join([str(item) for item in count]) + "\n"
        else:
            count = eval(arg_parsing[parameter] + "('" + args + "')")
            result += str(count) + "\n"

    # TODO: output format, alignment is... ugh :(
    sh.print(result)


    return 0
