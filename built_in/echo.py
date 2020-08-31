from main import wShell as sh


def do_echo(args: str):  # TODO: options
    """Writes its arguments to standard output.
    Usage: echo [option(s)] [string(s)]"""

    args_processed = args.replace("\"", "")
    sh.print(f"{args_processed}\n")

    return 0
