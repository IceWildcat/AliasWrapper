from main import wShell as sh
import os


def do_cat(args: str):
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
                sh.stdout.write(f'{str(n) + ") " + line}')
            else:
                sh.stdout.write(f'{line}')

        file.close()
        sh.stdout.write('\n\n')
