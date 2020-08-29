from main import wShell as sh


def do_echo(args: str):  # TODO: options
    """Writes its arguments to standard output.
    Usage: echo [option(s)] [string(s)]"""

    args_processed, exit_status = sh.replace_variables(args)
    args_processed = args_processed.replace("\"", "")

    sh.stdout.write(f"{args_processed}\n")

    return exit_status
