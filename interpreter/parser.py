from .errors import ParsingError
from .ast_nodes import *
from ..rply import ParserGenerator
from ..rply import Token



def parse_intermediate(possible_tokens, code=None, debug=False):
    """
    Here we're going to take our input token stream and try to parse it:
    that is to say we're going to try to build a tree from the bottom
    up from our input token stream using (behind the scenes) a pushdown
    automata.
    """

    pg = ParserGenerator(possible_tokens)


    def _t(t, s):
        return f'{t}{s}'


    # If there is an error parsing, this function gets executed
    @pg.error
    def error_handler(p, stable):
        raise ParsingError(f'There was a problem parsing {p}')


   
    @pg.production('start : command_list')
    def start(p, stable):
        children = p[0]
        return CommandListNode(children)


    
    @pg.production('command_list : command EOC command_list')
    def commands_many_one_or_more(p, stable):
        to_return = p[0] + p[2]
        return to_return


    @pg.production('command_list : ')
    def commands_many_none(p, stable):
        return []


    @pg.production('command : statement')
    @pg.production('command : ')
    def command(p, stable):
            return [p[0]] if len(p) > 0 else []



    @pg.production('svar : TYPE_INT SVAR')
    @pg.production('svar : TYPE_FLOAT SVAR')
    @pg.production('svar : TYPE_CHAR SVAR')
    @pg.production('svar : TYPE_ADDR SVAR')
    def svar(p, stable):
        return _t(p[0].value, p[1].value)


    @pg.production('avar : TYPE_INT AVAR')
    @pg.production('avar : TYPE_ADDR AVAR')
    def avar(p, stable):
        return _t(p[0].value, p[1].value) 


    @pg.production('literal_int : TYPE_INT INT')
    def literal_int(p, stable):
        return _t(p[0].value, p[1].value)


    @pg.production('literal_float : TYPE_FLOAT FLOAT')
    @pg.production('literal_float : TYPE_FLOAT INT')
    def literal_int(p, stable):
        return _t(p[0].value, p[1].value)


    @pg.production('literal_char : TYPE_CHAR CHAR')
    def literal_int(p, stable):
        return _t(p[0].value, p[1].value)


    @pg.production('literal_addr : TYPE_ADDR INT')
    def literal_int(p, stable):
        return _t(p[0].value, p[1].value)
       

        
    @pg.production('number : literal_int')
    @pg.production('number : literal_float')
    @pg.production('number : literal_addr')
    @pg.production('number : svar')
    def number(p, stable):
        return p[0]


    @pg.production('scalar : number')
    @pg.production('scalar : literal_char')
    def value_or_svar(p, stable):
        return p[0]



    @pg.production('statement : VAL_COPY scalar svar')
    @pg.production('statement : VAL_COPY scalar avar')
    @pg.production('statement : VAL_COPY avar avar')
    def val_copy(p, stable):
        children = [p[1], p[2]]
        return ValCopyNode(children)


    @pg.production('statement : OUT_INT literal_int')
    @pg.production('statement : OUT_INT svar')
    def print_num(p, stable):
        children = [p[1]]
        return PrintIntNode(children)


    @pg.production('statement : OUT_FLOAT literal_float')
    @pg.production('statement : OUT_FLOAT svar')
    def print_num(p, stable):
        children = [p[1]]
        return PrintFloatNode(children)


    @pg.production('statement : OUT_CHAR literal_char')
    @pg.production('statement : OUT_CHAR svar')
    def print_char(p, stable):
        children = [p[1]]
        return PrintCharNode(children)


    @pg.production('statement : IN_CHAR svar')
    def in_char(p, stable):
        children = [p[1]]
        return InputCharNode(children)


    @pg.production('statement : IN_INT svar')
    def in_char(p, stable):
        children = [p[1]]
        return InputIntNode(children)


    @pg.production('statement : IN_FLOAT svar')
    def in_char(p, stable):
        children = [p[1]]
        return InputFloatNode(children)


    @pg.production('statement : ADD number number svar')
    @pg.production('statement : SUB number number svar')
    @pg.production('statement : MUL number number svar')
    @pg.production('statement : DIV number number svar')
    @pg.production('statement : IDIV number number svar')
    @pg.production('statement : MOD number number svar')
    def binary_expr(p, stable):
        children = [p[0].value, p[1], p[2], p[3]]
        return MathBinaryOpNode(children)

    @pg.production('statement : NOT number svar')
    def unary_expr(p, stable):
        children = [p[0].value, p[1], p[2]]
        return MathUnaryOpMode(children)


    @pg.production('statement : TEST_LESS scalar scalar svar')
    @pg.production('statement : TEST_GTR scalar scalar svar')
    @pg.production('statement : TEST_EQU scalar scalar svar')
    @pg.production('statement : TEST_NEQU scalar scalar svar')
    def bin_compare(p, stable):
        children = [p[0].value, p[1], p[2], p[3]]
        return CompareBinaryOpNode(children)

    
    @pg.production('statement : JUMP LABEL_USE')
    def uncond_jump(p, stable):
        jump_to_line = stable.get_label(p[1].value)
        children = [jump_to_line]
        return JumpUncondNode(children)


    @pg.production('statement : JUMP svar')
    def unc_jump_by_var(p, stable):
        jump_to_line = p[1]
        children = [jump_to_line]
        return JumpUncondNode(children)


    @pg.production('statement : JUMP_IF_0 svar svar')
    @pg.production('statement : JUMP_IF_NE0 svar svar')
    def cond_jump_by_var(p, stable):
        expr = p[1]
        label = p[2]
        return JumpCondNode([p[0].value, expr, label])


    @pg.production('statement : JUMP_IF_0 svar LABEL_USE')
    @pg.production('statement : JUMP_IF_NE0 svar LABEL_USE')
    def cond_jump(p, stable):
        expr = p[1]
        label = stable.get_label(p[2].value)
        children = [p[0].value, expr, label]
        return JumpCondNode(children)


    # @pg.production('statement : RANDOM SVAR')
    # def random(p, stable):
    #     children = [p[1].value]
    #     return InputMysteryNode(children)


    @pg.production('statement : PUSH scalar')
    @pg.production('statement : PUSH avar')
    def push_nonlabel(p, stable):
        value = p[1]
        return StackPush([value])


    @pg.production('statement : PUSH LABEL_USE')
    def push_nonlabel(p, stable):
        value = stable.get_label(p[1].value)
        return StackPush([value])


    @pg.production('statement : POP svar')
    @pg.production('statement : POP avar')
    def pop(p, stable):
        return StackPop([p[1]])


    @pg.production('statement : AR_GET_NDX avar literal_int svar')
    @pg.production('statement : AR_GET_NDX avar svar svar')
    def get_array_ndx(p, stable):
        children = [p[1], p[2], p[3]]
        return ArrayGetNdx(children)


    @pg.production('statement : AR_SET_NDX avar literal_int scalar')
    @pg.production('statement : AR_SET_NDX avar svar scalar')
    def set_array_ndx(p, stable):
        children = [p[1], p[2], p[3]]
        return ArraySetNdx(children)


    @pg.production('statement : AR_GET_SZ avar svar')
    def get_array_size(p, stable):
        children = [p[1], p[2]]
        return ArrayGetSize(children)


    @pg.production('statement : AR_SET_SZ avar number')
    def set_array_size(p, stable):
        children = [p[1], p[2]]
        return ArraySetSize(children)


    @pg.production('statement : AR_COPY avar avar')
    def array_copy(p, stable):
        children = [p[1], p[2]]
        return ArrayCopy(children)



    parser = pg.build()     # Build the parser from the ParserGenerator
    return parser  #Actually do the parse