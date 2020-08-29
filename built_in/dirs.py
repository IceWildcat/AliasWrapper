from main import wShell as sh
import os


def do_pushd(args: str):  # TODO: arguments  [-n] [+N | -N | dir]
    """Save the current directory into a stack and move to a new directory.
    Usage: pushd [-n] [+N | -N | dir]"""
    if not os.path.isdir(args):
        return 1  # TODO: Error message

    sh.remembered_dirs.append(args)
    sh.cmdqueue.append("dirs")
    sh.cmdqueue.append("cd " + args)


def do_popd(args: str):  # TODO: arguments [-n] [+N | -N]
    """popd can be used to return back to the previous directory that is on top of the stack.
    Usage: popd [-n] [+N | -N]"""
    if len(sh.remembered_dirs) == 0:
        return 1  # TODO: Error message

    dir_pop = sh.remembered_dirs.pop()
    sh.stdout.write(f'{dir_pop}\n')
    sh.cmdqueue.append("cd " + dir_pop)


def do_dirs(args: str):  # TODO: arguments: [-clpv] [+N] [-N]
    """Display the list of currently remembered directories. By default, it includes the directory you are currently in. A directory can get into the list via pushd command followed by the dir name and can be removed via popd command.
    Usage: dirs  [-clpv] [+N] [-N]"""
    if len(args) == 1:
        args_list = [arg for arg in args if not arg == '-']

        if 'c' in args_list:
            sh.remembered_dirs = [os.getcwd()]
            return 0

    dir_output = "\t".join(sh.remembered_dirs) + "\t" + os.getcwd()
    sh.stdout.write(f'{dir_output}\n')
