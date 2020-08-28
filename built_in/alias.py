import json
from main import wShell as sh, add_method


@add_method(sh)
def do_alias(args: str):  # TODO: clean this shit
    """Register or check a command alias. It autosaves it to the alias file.
  Usage: alias <alias> [command] [args...]"""
    args_list = args.split(' ')
    # print(l)
    if args == '':
        sh.stdout.write(sh.do_alias.__doc__)
        sh.stdout.write(f"\nAliases: {str(sh.aliases)}\n")
    else:
        cmd, arg, lin = sh.parseline(args)
        if sh.aliases.get(args_list[0], None):
            if len(args_list) < 2:
                sh.stdout.write(f'{args_list[0]}: {str(sh.aliases.get(args_list[0], "You fucked up"))}')
            else:
                sh.stdout.write(
                    f'MODIFYING {args_list[0]}: {str(sh.aliases.get(args_list[0], "?¿?¿Data race?"))} -> {str(arg)}')
                sh.aliases[args_list[0]] = arg
        else:
            print(arg)
            sh.aliases[args_list[0]] = arg
        with open(sh.aliasfile, 'w') as a:  # TODO (1): handle exceptions
            a.write(json.dumps(sh.aliases))
            sh.stdout.write("Aliases saved.\n")

    sh.stdout.write("\n")

    return


@add_method(sh)
def do_reloadalias(line: str):  # TODO (1): handle exceptions
    """Reloads the alias file and parses it into internal memory."""
    with open(sh.aliasfile, 'r') as a:
        sh.aliases = json.loads(a.read())
        sh.stdout.write("Aliases reloaded. Running `alias`...\n")
        sh.onecmd("alias")
    return 0


@add_method(sh)
def do_unalias(args: str):
    """Unregister a command alias. It autosaves it to the alias file.
  Usage: unalias <alias>"""
    args_list = args.split(' ')
    # print(l)
    if args == '':
        sh.stdout.write(sh.do_alias.__doc__)
    else:
        cmd, arg, lin = sh.parseline(args)
        if sh.aliases.pop(args_list[0], None):
            sh.stdout.write(f'"{args_list[0]}" removed.\n')
        else:
            sh.stdout.write(f'{args_list[0]} was not an alias.\n')
        with open(sh.aliasfile, 'w') as a:  # TODO (1): handle exceptions
            a.write(json.dumps(sh.aliases))
            sh.stdout.write("Aliases saved.\n")

    sh.stdout.write("\n")

    return
