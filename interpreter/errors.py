def debug_code(line, code):
    import sys
    code_lines = code.splitlines()
    num_lines = len(code_lines)
    start_line = line - 5 if line - 5 >= 0 else 0
    end_line = line + 5 if line + 5 < num_lines else num_lines-1
    for ndx in range(start_line, end_line+1):
        if ndx == line:
            print('->'.rjust(2), end='', file=sys.stderr)
        else:
            print(' '.rjust(2), end ='', file=sys.stderr)
        cline = code_lines[ndx].strip()
        print(f'{ndx:>5} {cline}', file=sys.stderr)

    

class ParsingError(Exception):
    def __init__(self, msg):
        pass


class IdentifierNotDefinedError(Exception):
    def __init__(self, ident):
        self.message = f'Undefined identifier {ident}'


class LexingError(Exception):
    pass

class LabelNotFoundError(Exception):
    pass

class UninitializedMemoryRequestError(Exception):
    def __init__(self, var):
        self.message = f"Requesting {var} before initialization."

class InvalidDestinationError(Exception):
    pass

class VariableTypeMismatchError(Exception):
    pass

class DivisionByZeroError(Exception):
    pass