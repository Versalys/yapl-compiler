from .lexer import build_intermediate_lexer
from .parser import parse_intermediate
from .errors import debug_code
from .symbol_table import InterpreterST


def interpret_intermediate(in_str, debug=False):
    import sys
    code_lines = list(map(lambda x: f'{x}\n', in_str.splitlines()))
    lexer, possible_tokens = build_intermediate_lexer()
    symbol_table = InterpreterST()

    # Identify our labels
    for ndx, line in enumerate(code_lines):
        try:
            tokens = list(lexer.lex(code_lines[ndx]))
            if len(tokens) == 2 and tokens[0].name == 'LABEL_MARK':
                symbol_table.add_label(tokens[0].value[0:-1], ndx)
        except Exception as e:
            if debug:
                print('Lexing error.', file=sys.stderr)
                debug_code(ndx, in_str)
            raise e
    
    # Interpret our program
    while symbol_table.ip < len(code_lines):

        ip = symbol_table.ip
        line = code_lines[ip]

        try:
            tokens = list(lexer.lex(line))
            if len(tokens) < 3:   # Empty line or label
                symbol_table.next()
                continue
        except Exception as e:
            if debug:
                print('Lexing error.', file=sys.stderr)
                debug_code(symbol_table.ip, in_str)
            raise e


        try:
             parser = parse_intermediate(possible_tokens)
             tree = parser.parse(iter(tokens), state=symbol_table)
        except Exception as e:
            if debug:
                print('Parsing error.', file=sys.stderr)
                debug_code(symbol_table.ip, in_str)
            raise e

        try:
            tree.interpret(symbol_table)
        except Exception as e:
            if debug:
                print('Interpreter error.', file=sys.stderr)
                debug_code(symbol_table.ip, in_str)
            raise e

    return symbol_table