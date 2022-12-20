from ..rply import LexerGenerator
from .errors import LexingError



# We just want to recognize a number
def build_intermediate_lexer():
    lg = LexerGenerator()

    lg.add('EOC', r'\n')

    lg.add('SVAR', r'[sS]\d+')
    lg.add('AVAR', r'[aA]\d+')
    lg.add('FLOAT', r'\-?\d+\.\d+')
    lg.add('INT', r'\-?\d+')
    lg.add('CHAR', r"'(%[nt%\']|.)'")
    lg.add('TYPE_INT', r'\%')
    lg.add('TYPE_FLOAT', r'!')
    lg.add('TYPE_CHAR', r'\$')
    lg.add('TYPE_ADDR', r'@')


    kw = [r'VAL_COPY',
        r'ADD', r'SUB', r'MUL', r'DIV', r'IDIV', r'MOD', r'NOT',
        r'TEST_LESS', r'TEST_GTR', 'TEST_EQU', 'TEST_NEQU',
        r'JUMP_IF_0', r'JUMP_IF_NE0', r'JUMP', 
        #r'RANDOM', 
        r'OUT_INT', r'OUT_CHAR', r'OUT_FLOAT', r'IN_FLOAT', r'IN_CHAR', r'IN_INT',
        r'PUSH', r'POP',
        r'AR_GET_NDX', r'AR_SET_NDX', r'AR_GET_SZ', r'AR_SET_SZ',
        r'AR_COPY'
    ]
    for name in kw:
        lg.add(name, name)

    lg.add('LABEL_MARK', r'[_\-a-zA-Z\d]+:')
    lg.add('LABEL_USE', r'[_\-a-zA-Z\d]+')



    lg.ignore(r'#.*')     # Ignore comments
    lg.ignore(r'[\t ]')   # Ignore white space
    lg.add('ERROR', r'.')
    
    # Build our lexer generator
    lexer = lg.build()    

    possible_tokens = set()
    for rule in lg.rules:
        if rule.name not in ['LABEL_MARK', 'ERROR']:
            possible_tokens.add(rule.name)  #Store the token name in our possible_tokens

    return lexer, possible_tokens
