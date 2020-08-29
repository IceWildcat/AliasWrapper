from main import wShell as sh
import os


def ls_logic(filename, args_list):  # TODO: flags dFil[a,h,s]rRsStX
    """Given a file name and the argument list, determines if it sould be shown or not.
    :param filename: Name of the file being evaluated
    :param args_list: List of arguments
    :return: True (show file) | False (don't show file)
    """
    return 'a' in args_list or not filename.startswith('.')  # If not flag 'a', show only not hidden files


def do_ls(args: str):
    """List files and directories.
    Usage: ls [options] [directory]"""
    ls_dir = os.getcwd()
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
    files = sorted([f for f in os.listdir(ls_dir) if ls_logic(f, args_list)], key=lambda f: f.lower())
    # print(*files, sep='\t\t')  # TODO: Wrap the lines

    files_output = "\t\t".join(files)
    sh.stdout.write(f'{files_output}\n')

    return 0  # Success
