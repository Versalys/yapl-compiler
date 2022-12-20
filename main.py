#!/usr/bin/python3.8

'''
Solution test module for the mimir handins for CSE450
Written by Aidan Erickson
'''

from sys import argv, stderr
from parser import build_parser
from lexer import lex_source
from symbol_table import SymbolTable
from rply.token import Token

'''
Helper for printing tree at a particular node
:param node: node to print from
:param offset: tab offset for organizing code. Increments with child called.
'''
def print_tree(node, offset=0):
    print('\t'*offset, type(node) if type(node) is not Token else '{' + node.name + ' ' + node.value + '}')
    try:
        for child in node.children:
            print_tree(child, offset+1)
    except:
        return
    
'''
test function for project 3 & 4
param src: source code for the project
'''
def compile_source_intermediate(src):
    # print('ttttt')
    tokens = lex_source(src)
    pg = build_parser(tokens[1])
    root = pg.parse(iter(tokens[0]))
    # for token in tokens[0]:
        # print(token.name, token.value)
    output_statements = [] # to be passed into the nodes
    sym_table = SymbolTable()

    # print_tree(root)
    output_statements.append('VAL_COPY @1000 @S0') # set initial heap mem index
    root.compile(sym_table, output_statements)

    print('SOURCE CODE:\n' + '\n'.join(output_statements))
    
    return '\n'.join(output_statements)

def main():
    if len(argv) == 3:
        output_filename = argv[2]
        filename = argv[1]
    elif len(argv) == 2:
        filename = argv[1]
        output_filename = 'outfile.yail'
    elif len(argv) == 1:
        filename = input("Input filename:")
        output_filename = 'outfile.yail'
    else:
        print("Wrong number of arguments given. Exiting...", file=stderr)
        exit(1)

    src = ''
    with open(filename, 'r') as f:
        src = ''.join(f)

    print(src)

    tokens = lex_source(src)
    pg = build_parser(tokens[1])
    root = pg.parse(iter(tokens[0]))
    # for token in tokens[0]:
        # print(token.name, token.value)
    output_statements = [] # to be passed into the nodes
    sym_table = SymbolTable()

    # print_tree(root)
    output_statements.append('VAL_COPY @1000 @S0') # set initial heap mem index
    root.compile(sym_table, output_statements)
    with open(output_filename, 'w') as f:
        print('SOURCE CODE:\n' + '\n'.join(output_statements), file=f)

if __name__ == "__main__":
    main()
