from main import wShell as sh


def do_echo(args: str):  # TODO: options
    """Writes its arguments to standard output.
    Usage: echo [option(s)] [string(s)]"""

    args_split = args.split(" ")
    args_processed = args

    for arg in args_split:
        if '$' in arg and arg[1:] in sh.variables:
            args_processed = args_processed.replace(arg, str(sh.variables[arg[1:]]))

    sh.stdout.write(f"{args_processed}\n")