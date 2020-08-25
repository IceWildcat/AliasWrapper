from main import wShell as sh


def do_cd(args: str):  # TODO: options
    """Changes the current working directory.
    Usage: cd [option] [directory]"""
    n = -1
    try:
        os.chdir(args)
        n = 0
    except OSError as e:
        n = e.errno
        sh.stdout.write(f"cd: {e.strerror}\n\n")
    finally:
        return n
