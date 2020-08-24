def replace_vars(string, vars):
    for var in vars:
        string = string.replace("${}".format(var), vars[var])
    return string
