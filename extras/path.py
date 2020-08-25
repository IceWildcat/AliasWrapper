import os
from main import wShell as sh


def command_in_path(exe: str):
    """Checks in every address in the system PATH enviroment variable whether the command exists or not. If it does,
    it executes it. Otherwise, returns False"""

    for path in os.environ['PATH'].split(";"):  # For each value in the PATH
        if not os.path.isdir(path):  # If the PATH address is not valid, move on
            continue

        if exe + '.exe' in os.listdir(
                path):  # However, if an executable file with the given name exists, return True
            return True

    return False  # Otherwise, return False (the command is not in PATH)
