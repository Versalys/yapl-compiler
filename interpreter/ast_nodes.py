from .getch import getch
from random import randint
from .errors import *
import copy

class ASTNode():
    def __init__(self, children):
        self._returned = None
        self.children = children

    def compile(self, symbol_table, output=[]):
        raise NotImplementedError('ASTNode compile is not implemented')

    def interpret(self, symbol_table):
        raise NotImplementedError('ASTNode interpret is not implemented')


class CommandListNode(ASTNode):
    """
    children: a list of commands
    """
    def interpret(self, symbol_table):
        for child in self.children:
            child.interpret(symbol_table)



class ValCopyNode(ASTNode):
    """
    children[0] : number
    children[1] : svar | avar
    """
    def interpret(self, symbol_table):
        src = symbol_table.lookup(self.children[0], dequote=False)
        dst = self.children[1]
        symbol_table.val_copy(src, dst)
        symbol_table.next()



class MathBinaryOpNode(ASTNode):
    """
    children[0]: op
    children[1]: number
    children[2]: number
    children[3]: svar
    """
    def interpret(self, symbol_table):
        dtype_lhs = self.children[1][0]
        dtype_rhs = self.children[2][0]
        dtype_dst = self.children[3][0]
        assert(dtype_lhs in '!%@')
        assert(dtype_rhs in '!%@')
        assert(dtype_dst in '!%@')
        
        lhs = symbol_table.lookup(self.children[1])
        rhs = symbol_table.lookup(self.children[2])
        op = self.children[0]
        dst = self.children[3]
        
        if dtype_lhs == '!' or dtype_rhs == '!':
            assert(dtype_dst == '!')
        
        if dtype_lhs == '@' or dtype_rhs == '@':
            assert (dtype_dst == '@')

        if op == 'DIV':
            assert(dtype_dst == '!')

        
        if op == 'ADD':
            result = lhs + rhs
        elif op == 'SUB':
            result = lhs - rhs
        elif op == 'MUL':
            result = lhs * rhs
        elif op == 'DIV':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs / rhs
        elif op == 'IDIV':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs // rhs
        elif op == 'MOD':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs % rhs
        symbol_table.val_copy(result, dst)
        symbol_table.next()


class MathUnaryOpMode(ASTNode):
    """
    children[0]: op
    children[1]: number
    children[2]: svar
    """
    def interpret(self, symbol_table):
        assert(self.children[1][0] in '%!')
        assert(self.children[2][0] in '%!')
        assert(self.children[1][0] == self.children[2][0])
        op = self.children[0]
        expr = symbol_table.lookup(self.children[1])
        dst = self.children[2]
        if op == 'NOT':
            result = 0 if expr != 0 else 1
        symbol_table.val_copy(result, dst)
        symbol_table.next()


class CompareBinaryOpNode(ASTNode):
    """
    children[0]: op
    children[1]: number
    children[2]: number
    children[3]: svar
    """
    def interpret(self, symbol_table):
        lhs = symbol_table.lookup(self.children[1])
        rhs = symbol_table.lookup(self.children[2])
        op = self.children[0]
        dst = self.children[3]

        dtype_lhs = self.children[1][0]
        dtype_rhs = self.children[2][0]
        dtype_dst = self.children[3][0]

        assert(dtype_dst == '%')
        if dtype_lhs == '$' or dtype_rhs == '$':
            assert(dtype_lhs == dtype_rhs)

        if op == 'TEST_EQU':
            result = int(lhs == rhs)
        elif op == 'TEST_NEQU':
            result = int(lhs != rhs)
        elif op == 'TEST_GTR':
            result = int(lhs > rhs)
        elif op == 'TEST_LESS':
            result = int(lhs < rhs)
        symbol_table.val_copy(result, dst)
        symbol_table.next()


class JumpUncondNode(ASTNode):
    """
    children[0] = label loc
    """
    def interpret(self, symbol_table):
        symbol_table.set_ip(symbol_table.lookup(self.children[0]))



class JumpCondNode(ASTNode):
    """
    children[0] = cond_type
    children[1] = value
    children[2] = label loc
    """
    def interpret(self, symbol_table):
        cond_type = self.children[0]
        value = symbol_table.lookup(self.children[1])
        label = self.children[2]
        if cond_type == 'JUMP_IF_0':
            if value == 0:
                symbol_table.set_ip(symbol_table.lookup(label))
                return
        elif cond_type == 'JUMP_IF_NE0':
            if value != 0:
                symbol_table.set_ip(symbol_table.lookup(label))
                return
        symbol_table.next()





class PrintIntNode(ASTNode):
    """
    children[0] : number
    """
    def interpret(self, symbol_table):
        assert(self.children[0][0] == '%')
        lhs = symbol_table.lookup(self.children[0])
        print(symbol_table.lookup(lhs), end='')
        symbol_table.next()


class PrintFloatNode(ASTNode):
    """
    children[0] : number
    """
    def interpret(self, symbol_table):
        assert(self.children[0][0] == '!')
        lhs = symbol_table.lookup(self.children[0])
        print(symbol_table.lookup(lhs), end='')
        symbol_table.next()


class PrintCharNode(ASTNode):
    """
    children[0] : char
    """
    def interpret(self, symbol_table):
        assert(self.children[0][0] == '$')
        lhs = symbol_table.lookup(self.children[0], dequote=True)
        if lhs == r'%n':
            lhs = '\n'
        elif lhs == r'%%':
            lhs = '%'
        elif lhs == r'%t':
            lhs = '\t'
        elif lhs == '%\'':
            lhs = '\''
        print(lhs, end='')
        symbol_table.next()



class InputCharNode(ASTNode):
    """
    children[0]: svar to store the data
    """
    def interpret(self, symbol_table):
        raise NotImplemented()
        ch = getch()
        if ch == '\t':
            ch = '%t'
        elif ch == '\n':
            ch = '%n'
        elif ch == "'":
            ch = "%'"
        dst = self.children[0]
        to_store = f"$'{ch}'"
        symbol_table.val_copy(to_store, dst)
        symbol_table.next()


class InputIntNode(ASTNode):
    """
    children[0]: svar to store the data
    """
    def interpret(self, symbol_table):
        raise NotImplemented()


class InputFloatNode(ASTNode):
    """
    children[0]: svar to store the data
    """
    def interpret(self, symbol_table):
        raise NotImplemented()


# class InputMysteryNode(ASTNode):
#     """
#     children[0]: svar to store the data
#     """
#     def interpret(self, symbol_table):
#         val = randint(-100,100)
#         dst = self.children[0]
#         symbol_table.val_copy(val, dst)
#         symbol_table.next()



class ArrayGetSize(ASTNode):
    """
    children[0] : avar
    children[1] : svar
    """
    def interpret(self, symbol_table):
        avar, svar = self.children
        loc = symbol_table.lookup(avar)
        sz = symbol_table.lookup(f'%s{loc}')
        symbol_table.val_copy(sz, svar)
        symbol_table.next()



class ArraySetSize(ASTNode):
    """
    children[0] : avar
    children[1] : number
    """
    def interpret(self, symbol_table):
        avar, num = self.children
        loc = symbol_table.lookup(avar)
        sz = symbol_table.lookup(num)
        symbol_table.val_copy(f'%{sz}', f'%s{loc}')
        symbol_table.next()





class ArrayGetNdx(ASTNode):
    """
    children[0] : avar
    children[1] : number ndx
    children[1] : svar dst
    """
    def interpret(self, symbol_table):
        avar, ndx, dst = self.children
        loc = symbol_table.lookup(avar)
        loc += symbol_table.lookup(ndx)
        loc += 1
        symbol_table.val_copy(symbol_table.memory[loc].as_string(), dst)
        symbol_table.next()



class ArraySetNdx(ASTNode):
    """
    children[0] : avar
    children[1] : number
    children[2] : number
    """
    def interpret(self, symbol_table):
        avar, svar, val = self.children
        loc = symbol_table.lookup(avar)
        loc += symbol_table.lookup(svar)
        loc += 1
        dtype = val[0]
        symbol_table.val_copy(f'{val}', f'{dtype}s{loc}')
        symbol_table.next()



class ArrayCopy(ASTNode):
    """
    children[0] : avar src
    children[1] : avar dst
    """
    def interpret(self, symbol_table):
        src, dst = self.children
        loc_src = symbol_table.lookup(src)
        loc_dst = symbol_table.lookup(dst)
        sz = symbol_table.lookup(f'%s{loc_src}')
        for k in range(0,sz+1):
            symbol_table.memory[loc_dst+k] = copy.copy(symbol_table.memory[loc_src+k])
        symbol_table.next()
        

class StackPush(ASTNode):
    '''
    children[0] : value to push
    '''
    def interpret(self, symbol_table):
        val = self.children[0]
        symbol_table.push_stack(val)
        symbol_table.next()



class StackPop(ASTNode):
    '''
    children[0] : destination to pop value to
    '''
    def interpret(self, symbol_table):
        dst = self.children[0]
        val = symbol_table.pop_stack()
        symbol_table.val_copy(f'{val}', dst)
        symbol_table.next()
