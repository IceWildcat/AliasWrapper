from main import wShell as sh
import os
import re


def ls_logic(filename, args_list):  # TODO: flags dFil[a,h,s]rRsStX
    """Given a file name and the argument list, determines if it sould be shown or not.
    :param filename: Name of the file being evaluated
    :param args_list: List of arguments
    :return: True (show file) | False (don't show file)
    """

    if 'a' in args_list:
        return True

    return not filename.startswith('.')


def do_ls(args: str):
    """List files and directories.
    Usage: ls [options] [directory]"""

    if args == "":
        # TODO: no arguments given (do ls on cwd)
        ls_dir = os.getcwd()
        files = sorted([f for f in os.listdir(ls_dir) if not f.startswith(".")], key=lambda f: f.lower())
        # print(*files, sep='\t\t')  # TODO: Wrap the lines

        files_output = "\t\t".join(files)
        sh.stdout.write(f'{files_output}\n')
        return 0
    elif re.fullmatch(r"^" + sh.regex_folder + "$", args):
        # TODO: no operators given (do ls on given dir)
        files = sorted([f for f in os.listdir(args) if not f.startswith(".")], key=lambda f: f.lower())
        # print(*files, sep='\t\t')  # TODO: Wrap the lines

        files_output = "\t\t".join(files)
        sh.stdout.write(f'{files_output}\n')
        return 0
    else:
        # TODO: operator logic
        # TODO: optimize
        operator_list = []
        path = ""
        switch = False
        for c in args:
            if c == '-':
                continue

            if c == ' ':
                switch = True
                continue

            if switch:
                path += c
            else:
                operator_list.append(c)

        if path == '':
            path = os.getcwd()

        if not os.path.isdir(path):
            sh.stdout.write(f'Invalid path!\n')
            return 3

        files = sorted([f for f in os.listdir(path) if ls_logic(f, operator_list)], key=lambda f: f.lower())
        # print(*files, sep='\t\t')  # TODO: Wrap the lines

        files_output = "\t\t".join(files)
        sh.stdout.write(f'{files_output}\n')
        return 0

