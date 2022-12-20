'''
CSE 450 - Project
Parser
Written by Aidan Erickson -- The cool dude with a cool attitude
'''

from ast_nodes import *
from rply import ParserGenerator

import re

'''
define exceptions for improper programs
'''
class ParsingException(Exception):
    pass

class MockToken():
    def __init__(self, name, value):
        self.name = name
        self.value = value
'''
Builds the parser with the possible tokens given by the lexer
param tokens: possible tokens
'''
def build_parser(tokens):

    precedence = [
        ('right', ['ASSIGN']),
        ('left', ['COMPARE_BINARY_OP']),
        ('left', ['MATH_PLUS', 'MATH_MINUS', 'LOGIC_BINARY_OP']),
        ('left', ['MATH_BINARY_OP']),
        ('right', ['MATH_NEGATION', 'LOGIC_UNARY_OP']),
    ]

    pg = ParserGenerator(tokens, precedence)

    #If we have an error, call this function
    @pg.error  # Note the lack of ()
    def error_handler(p):
        print(f'There was an error processing {p}')
        print(f'Source position {p.source_pos}')

    ### these following decorators and functions describe the formulation of all programs within our language
    
    @pg.production('statement_list : statement EOC statement_list')
    def statement_list_full(p):
        if p[0] != None:
            p[2].push(p[0])
        return p[2]
    
    @pg.production('statement_list : ')
    def statement_list_empty(p):
        return StatementListNode([])
    
    @pg.production("statement : SCALAR_TYPE IDENTIFIER")
    def declare_scalar_type(p):
        return CmdDeclare([p[1], p[0]])

    @pg.production('statement : SCALAR_TYPE IDENTIFIER ASSIGN expr')
    def initialize_scalar(p):
        return CmdInitialize([p[1], p[3], p[0]])

    @pg.production('statement : IF expr THEN statement_list END')
    def if_statement(p):
        return CmdIf([p[1], p[3]])

    @pg.production('statement : IF expr THEN statement_list ELSE statement_list END')
    def if_else_statement(p):
        return CmdIfElse([p[1], p[3], p[5]])

    @pg.production('statement : WHILE expr DO statement_list END')
    def while_statement(p):
        return CmdWhile([p[1], p[3]])

    @pg.production('statement : BREAK')
    def break_statement(p):
        # print('BROKEN')
        return CmdBreak([])

    @pg.production('statement : FOR IDENTIFIER IN arr_expr DO statement_list END')
    def for_statement(p):
        return CmdFor([p[1], p[3], p[5]])
    
    @pg.production('expr : IDENTIFIER ASSIGN expr')
    def assign(p):
        return ExprAssign([p[0], p[2]])

    @pg.production('expr : expr MATH_PLUS expr')
    def math_plus(p):
        return ExprMathBinary([p[0], p[1], p[2]])

    @pg.production('expr : expr MATH_MINUS expr')
    def math_minus(p):
        return ExprMathBinary([p[0], p[1], p[2]])
    
    @pg.production('expr : MATH_MINUS expr')
    def math_negate(p):
        return ExprMathNegate([p[1]])

    @pg.production('expr : INPUTTING')
    def inputting(p):
        return CmdInput()

    @pg.production('expr : IDENTIFIER DOT LENGTH')
    def eval_length(p):
        return ExprLength([p[0]])

    @pg.production('expr : PAREN_OPEN expr PAREN_CLOSE')
    def parenthesis(p):
        return p[1]

    @pg.production('expr : expr MATH_BINARY_OP expr')
    def process_math_bin_op(p):
        return ExprMathBinary([p[0], p[1], p[2]])

    @pg.production('expr : MATH_NARY_OP arr_expr')
    def process_nary_op(p):
        if p[0].value == 'sum_of':
            node = ExprMathSum([p[1]])
        elif p[0].value == 'product_of':
            node = ExprMathProd([p[1]])
        elif p[0].value == 'minimum_of':
            node = ExprMathMin([p[1]])
        elif p[0].value == 'maximum_of':
            node = ExprMathMax([p[1]])

        return node

    @pg.production('list : expr COMMA expr')
    def processs_list_new(p):
        return ArrExprVector([p[2], p[0]])
        
        
    @pg.production('list : expr COMMA list')
    def process_list_recur(p):
        p[2].push(p[0])
        return p[2]

    @pg.production('vector : BRACE_OPEN vector BRACE_CLOSE')
    @pg.production('vector : BRACE_OPEN list BRACE_CLOSE')
    def process_vector_list(p):
        return p[1]
    
    @pg.production('vector : BRACE_OPEN expr BRACE_CLOSE')
    def process_vector_expr(p):
        return ArrExprVector([p[1]])

    @pg.production('arr_expr : vector')
    def process_arr_expr(p):
        return p[0]

    @pg.production('arr_expr : IDENTIFIER DOT COPY')
    def process_arr_copy(p):
        return ArrCopy([p[0]])

    @pg.production('expr : expr LOGIC_BINARY_OP expr')
    def logic_binary_op(p):
        return ExprLogicBin([p[0], p[1], p[2]])

    @pg.production('expr : LOGIC_NARY_OP arr_expr')
    def logic_nary_op_array(p):
        if p[0].value == 'every_of':
            node = ExprLogicEvery([p[1]])
        else:
            node = ExprLogicAny([p[1]])
        return node

    @pg.production('expr : expr COMPARE_BINARY_OP expr')
    def compare_op(p):
        return ExprLogicComp([p[0], p[1], p[2]])

    @pg.production('statement : PRINTING BRACE_OPEN expr BRACE_CLOSE')
    def print_op(p):
        node = CmdPrint([]) if p[0].value == 'print' else CmdPrintln([])

        node.push(p[2])
        # internode = 
        return node

    @pg.production('statement : PRINTING BRACE_OPEN arr_expr BRACE_CLOSE')
    def print_op_arr(p):
        node = CmdPrint([]) if p[0].value == 'print' else CmdPrintln([])
                
        node.push(p[2])
        # internode = 
        return node

    @pg.production('statement : PRINTING vector')
    def print_op_vector(p):
        node = CmdPrint([]) if p[0].value == 'print' else CmdPrintln([])

        node.push(p[1])
        return node

    # ==== TYPE LITERALS ====
    @pg.production('expr : INT_LITERAL')
    def base_int(p):
        return ExprInt([p[0]])
    @pg.production('expr : FLOAT_LITERAL')
    def base_float(p):
        return ExprFloat([p[0]])
    @pg.production('expr : BOOL_LITERAL')
    def base_bool(p):
        return ExprBool([p[0]])
    @pg.production('expr : IDENTIFIER')
    def base_ident(p):
        return ExprID([p[0]])
    @pg.production('expr : CHAR_LITERAL')
    def base_char(p):
        return ExprChar([p[0]])
    @pg.production('arr_expr : IDENTIFIER')
    def base_arr_ident(p):
        return ExprIDArr([p[0]])
    @pg.production('arr_expr : expr SEMICOLON expr')
    def range_no_step(p):
        return ExprRange([p[0], p[2]])
    @pg.production('arr_expr : expr SEMICOLON expr SEMICOLON expr')
    def range_step(p):
        return ExprRange([p[0], p[2], p[4]])

    @pg.production('vector : STRING')
    def base_string(p):
        l = ArrExprVector([])
        i = 1
        raw_string = p[0].value[::-1]
        
        while i < len(raw_string) - 1:
            if raw_string[i+1] == '%':
                if i == len(raw_string) - 1:
                    raise ParsingException("Must have a character proceed '%'")
                l.push(ExprChar([MockToken('char', "'" + raw_string[i+1] + raw_string[i]+ "'")]))
                i += 1
            else:
                l.push(ExprChar([MockToken('char', "'" + raw_string[i] + "'")]))
            i += 1
            
        return l

    # ====== ARRAY DECLARATIONS and ASSIGNMENT ======
    @pg.production('statement : SCALAR_TYPE BRACKET_OPEN BRACKET_CLOSE IDENTIFIER')
    def declare_arr_unsized(p):
        return CmdDeclareArr([p[0], p[3]])

    @pg.production('statement : SCALAR_TYPE BRACKET_OPEN expr BRACKET_CLOSE IDENTIFIER')
    def declare_arr_sized(p):
        return CmdDeclareArr([p[0], p[4], p[2]])

    @pg.production('expr : LOGIC_UNARY_OP expr') # may pull two strings
    def logic_negate(p):
        return ExprLogicNegate([p[1]])

    @pg.production('statement : SCALAR_TYPE BRACKET_OPEN BRACKET_CLOSE IDENTIFIER ASSIGN arr_expr')
    def initialize_arr_unsized(p):
        return CmdInitializeArr([p[0], p[3], p[5]])

    @pg.production('statement : SCALAR_TYPE BRACKET_OPEN expr BRACKET_CLOSE IDENTIFIER ASSIGN arr_expr')
    def initialize_arr_sized(p):
        return CmdInitializeArr([p[0], p[4], p[6], p[2]])

    

    @pg.production('expr : IDENTIFIER BRACKET_OPEN expr BRACKET_CLOSE')
    def eval_arr_element(p):
        return ExprEvalArrElm([p[0], p[2]])

    @pg.production('expr : IDENTIFIER BRACKET_OPEN expr BRACKET_CLOSE ASSIGN expr')
    def assign_arr_element(p):
        return ExprAssignArrElm([p[0], p[2], p[5]])

    # ==== Function Stuff
    @pg.production('statement : DEFINE IDENTIFIER arg_list ARROW SCALAR_TYPE SEMICOLON statement_list END') 
    def define_scalar_ret_function(p):
        return CmdFunctionNode([p[1],p[2],p[4], p[6],False])

    @pg.production('statement : DEFINE IDENTIFIER arg_list ARROW SCALAR_TYPE BRACKET_OPEN BRACKET_CLOSE SEMICOLON statement_list END') 
    def define_vector_ret_function(p):
        return CmdFunctionNode([p[1],p[2],p[4],p[8],True])

    @pg.production('statement : RETURN expr')
    @pg.production('statement : RETURN arr_expr')
    def return_statement(p):
        return CmdReturn([p[1]])

    @pg.production('arg_list : PAREN_OPEN SCALAR_TYPE SEMICOLON IDENTIFIER arg_tail PAREN_CLOSE')
    def define_arg_list(p):
        p[4].push((p[1], p[3], False))
        return p[4]

    @pg.production('arg_list : PAREN_OPEN SCALAR_TYPE BRACKET_OPEN BRACKET_CLOSE SEMICOLON IDENTIFIER arg_tail PAREN_CLOSE')
    def define_arg_list_vector(p):
        p[6].push((p[1], p[5], True))
        return p[6]

    @pg.production('arg_list : PAREN_OPEN PAREN_CLOSE')
    def define_arg_list_empty(p):
        return CmdArgListNode([])

    @pg.production('arg_tail : COMMA SCALAR_TYPE SEMICOLON IDENTIFIER arg_tail')
    def arg_tail_scalar(p):
        p[4].push((p[1],p[3],False))
        return p[4]

    @pg.production('arg_tail : COMMA SCALAR_TYPE BRACKET_OPEN BRACKET_CLOSE SEMICOLON IDENTIFIER arg_tail')
    def arg_tail_vector(p):
        p[6].push((p[1],p[5],True))
        return p[6]

    @pg.production('arg_tail : ')
    def arg_tail_empty(p):
        return CmdArgListNode([])

    @pg.production('expr : IDENTIFIER PAREN_OPEN param_list PAREN_CLOSE')
    # @pg.production('arr_expr : IDENTIFIER PAREN_OPEN param_list PAREN_CLOSE')
    def function_call(p):
        return ExprFuncCall([p[0], p[2]])

    @pg.production('param_list : expr param_tail')
    def param_list(p):
        if p[0]:
            p[1].push(p[0])
        return p[1]

    @pg.production('param_tail : COMMA expr param_tail')
    def function_param(p):
        p[2].push(p[1])
        return p[2]

    @pg.production('param_list : ')
    @pg.production('param_tail : ')
    def function_param_empty(p):
        return CmdParamNode([])

    # ======= LANGUAGE STRUCTURE ENFORCERS ======
    @pg.production('statement : expr')
    def create_statement_from_expression(p):
        return p[0] # retruning right from expression without making new node

    @pg.production('statement : arr_expr')
    def create_statement_from_arr_expr(p):
        return p[0]
    
    @pg.production('statement : ')
    def create_statement(p):
        return None # return nothing
    
    return pg.build()
