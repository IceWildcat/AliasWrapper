from built_in.logic import replace_variables
from main import wShell as sh, add_method


@add_method(sh)
def do_echo(args: str):  # TODO: options
    """Writes its arguments to standard output.
    Usage: echo [option(s)] [string(s)]"""
    args_processed = replace_variables(args)
    sh.stdout.write(f"{args_processed}\n")