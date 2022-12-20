'''
CSE 450 - project 2
Written by Aidan Erickson
'''

from rply import LexerGenerator

import re

'''
define exceptions for improper programs
'''
class LexingException(Exception):
    pass


'''
builds a lexer and lexes source code
param src: source code to lex
'''
def lex_source(src):
    """
    Write your solution here or call another function / module
    to complete the task of lexing the source language code.

    Arguments:
        src     source code in source language

    Returns:
        list of tokens lexed using RPLYs lexer
    """
    lg = LexerGenerator() # used to create lexer

    #these define the all the possible tokens creatd by the lexer, for use in the parser initialization
    possible_tokens = ['SCALAR_TYPE','FLOAT_LITERAL','INT_LITERAL','BOOL_LITERAL','MATH_MINUS',
                       'MATH_PLUS','MATH_BINARY_OP','MATH_NARY_OP','COMPARE_BINARY_OP','ARROW','DEFINE',
                       'RETURN','LOGIC_UNARY_OP','LOGIC_BINARY_OP','LOGIC_NARY_OP','ASSIGN','PRINTING',
                       'INPUTTING','COMMENT_SINGLE','DOT','LENGTH', 'STRING', 'COPY','SEMICOLON',
                       'COMMENT_MULTI','CHAR_LITERAL','PAREN_OPEN','PAREN_CLOSE','BRACE_OPEN',
                       'BRACE_CLOSE','BRACKET_OPEN','BRACKET_CLOSE','COMMA','EOC','IDENTIFIER',
                       'ERROR','IF','THEN','ELSE','WHILE','DO','END','BREAK', 'FOR', 'IN']
    
    # Rules
    lg.add('SCALAR_TYPE', r'\bint\b|\bfloat\b|\bbool\b|\bchar\b')
    lg.add('FLOAT_LITERAL', r'[0-9]+\.[0-9]+')
    lg.add('INT_LITERAL', r'[0-9]+')
    lg.add('BOOL_LITERAL', r'\bTrue\b|\bFalse\b')
    lg.add('ARROW', r'->')
    lg.add('MATH_MINUS', r'-')
    lg.add('MATH_PLUS', r'\+')
    lg.add('MATH_BINARY_OP', r'\*|/|%')
    lg.add('MATH_NARY_OP', r'\bsum_of\b|\bproduct_of\b|\bminimum_of\b|\bmaximum_of\b')
    lg.add('LOGIC_BINARY_OP', r'\band\b|\bor\b|\bxor\b')
    lg.add('LOGIC_NARY_OP', r'\bevery_of\b|\bany_of\b')
    lg.add('COMPARE_BINARY_OP', r'==|~=|<=|>=|<|>')
    lg.add('LOGIC_UNARY_OP', r'~')
    lg.add('ASSIGN', r'=')
    lg.add('PRINTING', r'\bprintln\b|\bprint\b')
    lg.add('INPUTTING', r'\binput_bool\b|\binput_char\b|\binput_float\b|\binput_int\b')
    lg.add('IF', r'\bif\b')
    lg.add('THEN', r'\bthen\b')
    lg.add('ELSE', r'\belse\b')
    lg.add('WHILE', r'\bwhile\b')
    lg.add('FOR', r'\bfor\b')
    lg.add('IN', r'\bin\b')
    lg.add('DEFINE', r'\bdef\b')
    lg.add('RETURN', r'\breturn\b')
    lg.add('DO', r'\bdo\b')
    lg.add('END', r'\bend\b')
    lg.add('BREAK', r'\bbreak\b')
    lg.add('COMMENT_SINGLE', r'#.*')
    lg.add('COMMENT_MULTI', r"'''.*'''", re.M | re.S)
    lg.add('CHAR_LITERAL', r"'%.'|'.'")
    lg.add('PAREN_OPEN', r'\(')
    lg.add('PAREN_CLOSE', r'\)')
    lg.add('BRACE_OPEN', r'\{')
    lg.add('BRACE_CLOSE', r'\}')
    lg.add('LENGTH', r'\blength\b')
    lg.add('DOT', r'\.')
    lg.add('SEMICOLON', r':')
    lg.add('COPY', r'\bcopy\b')
    lg.add('STRING', r'".*"')
    lg.add('BRACKET_OPEN', r'\[')
    lg.add('BRACKET_CLOSE', r'\]')
    lg.add('COMMA', r',')
    lg.add('EOC', r'\n', re.M)
    lg.add('IDENTIFIER', r'\w[\w_]*')
    lg.add('WHITESPACE', r'[ \t]')
    lg.add('ERROR', r'.')

    # lg.ignore(r"[\t\n ]")

    lexer = lg.build()
    lexed_src = list(lexer.lex(src))

    ret = []
    for i in lexed_src:
        if i.name == 'ERROR':
            raise LexingException("Error token found! : " + str(i))
        if i.name != 'COMMENT_MULTI' and i.name != 'COMMENT_SINGLE' and i.name != 'WHITESPACE':
            ret.append(i)
    return ret, possible_tokens
