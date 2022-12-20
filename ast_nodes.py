''' RETURN ADDRESS PROBABLY GETTING OVERWRITTEN
AST node file

contaiins all ast node classes all stemming from the superclass ASTNode
'''

# MAYBE EVAL TYPE IS NOT NECESSARY IF THE TYPE FLAG [!, %, $] is included already

from symbol_table import SymbolTable

# ========== EXCEPTIONS =============

class TypeParseError(Exception): # raised when there are improper types for an operation etc.
    pass

class ImproperTypeError(Exception):
    pass

class ImproperUsageError(Exception):
    pass

class ImproperReturnError(Exception):
    pass 

# ============ ABSTRACT CLASSES

class ASTNode:
    def __init__(self, children):
        self.children = children
        self._pos = 0
        
    def compile(self, st, output):
        raise NotImplementedError('compile is not implemented')

    def push(self, new):
        self.children.append(new)

    def __iter__(self):
        self._pos = 0
        return self

    def __next__(self):
        if self._pos < len(self.children):
            x = self.children[len(self.children) - 1 - self._pos] # in reverse
            self._pos += 1
            return x
        raise StopIteration

    def __len__(self):
        return len(self.children)

    def __get__(self, index):
        return self.children[index]

class ExprNode(ASTNode):
    def eval_type(self, st):
        raise NotImplementedError('eval type not implemented')

class CmdNode(ASTNode):
    def eval_type(self, st):
        raise NotImplementedError('Eval Type called on command node')

# ============= STATEMENT/COMMAND CLASSES ============

class StatementListNode(CmdNode):
    def compile(self, st, output):
        st.push_scope() # push new scope as we enter a new block of code
        for i in range(len(self.children)): # goes in reverse
            self.children[len(self.children)-1-i].compile(st, output)
        st.pop_scope()


class CmdDeclare(CmdNode):
    def compile(self, st, output):
        st.declare(self.children[0].value, self.children[1].value) # declare on symbol table

class CmdPrint(CmdNode):
    def compile(self, st, output):
        for child in self.children:
            result = child.compile(st, output)
            typ = child.eval_type(st)
            sym = st.type_sym_map[typ]
            if result[0] == '@':
                size = st.declare_tmp()
                element = st.declare_tmp()
                end = st.declare_tmp()
                label_num = st.get_operation_label_num()
                output.append('AR_GET_SZ ' + result + ' %' + size)
                index = st.declare_tmp()
                output.append('VAL_COPY %0 %' + index)
                output.append('PRINT_OPERATION_' + label_num + ':')
                output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
                
                if typ == 'int' or typ == 'bool':
                    output.append('OUT_INT ' + sym + element)
                elif typ == 'char':
                    output.append('OUT_CHAR ' + sym + element)
                elif typ == 'float':
                    output.append('OUT_FLOAT ' + sym + element)

                output.append('ADD %1 %' + index + ' %' + index)
                output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
                output.append('JUMP_IF_NE0 %' + end + ' PRINT_OPERATION_' + label_num)


class CmdPrintln(CmdNode):
    def compile(self, st, output):
        for child in self.children:
            result = child.compile(st, output)
            typ = child.eval_type(st)
            sym = st.type_sym_map[typ]
            if result[0] == '@':
                size = st.declare_tmp()
                element = st.declare_tmp()
                end = st.declare_tmp()
                label_num = st.get_operation_label_num()
                output.append('AR_GET_SZ ' + result + ' %' + size)
                index = st.declare_tmp()
                output.append('VAL_COPY %0 %' + index)
                output.append('PRINT_OPERATION_' + label_num + ':')
                output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
                
                if typ == 'int' or typ == 'bool':
                    output.append('OUT_INT ' + sym + element)
                elif typ == 'char':
                    output.append('OUT_CHAR ' + sym + element)
                elif typ == 'float':
                    output.append('OUT_FLOAT ' + sym + element)

                output.append('ADD %1 %' + index + ' %' + index)
                output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
                output.append('JUMP_IF_NE0 %' + end + ' PRINT_OPERATION_' + label_num)
              
                
            elif typ == 'int' or typ == 'bool':
                output.append('OUT_INT ' + result)
            elif typ == 'char':
                output.append('OUT_CHAR ' + result)
            elif typ == 'float':
                output.append('OUT_FLOAT ' + result)
            
        output.append('OUT_CHAR ' + r"$'%n'")

class CmdInput(CmdNode):
    def compile(self, st, output):
        pass

    
class CmdIf(CmdNode):
    def compile(self, st, output):
        condition = self.children[0].compile(st, output) # condition code
        print('=== ' + self.children[0].eval_type(st))
        if self.children[0].eval_type(st) != 'bool':
            raise TypeParseError('If conditional must be bool!')
        sym = st.type_sym_map[self.children[0].eval_type(st)]
        label_num = st.get_if_label_num()
        intermediate = st.declare_tmp() # jump_if_0 requires a var, not a number.
        output.append('VAL_COPY ' + condition + ' ' + sym + intermediate) # so jump if always has a var
        output.append('JUMP_IF_0 ' + sym + intermediate + ' IF_END_' + label_num)
        self.children[1].compile(st, output) # code inside block
        output.append('IF_END_' + label_num + ':') # ending label to jump to

class CmdIfElse(CmdNode):
    def compile(self, st, output):
        condition = self.children[0].compile(st, output) # condition code
        if self.children[0].eval_type(st) != 'bool':
            raise TypeParseError('If conditional must be bool!')
        sym = st.type_sym_map[self.children[0].eval_type(st)]
        label_num = st.get_if_label_num()
        intermediate = st.declare_tmp() # jump_if_0 requires a var, not a number.
        
        # IF BLOCK
        output.append('VAL_COPY ' + condition + ' ' + sym + intermediate) # so jump if always has a var
        output.append('JUMP_IF_0 ' + sym + intermediate + ' IF_ELSE_' + label_num)
        self.children[1].compile(st, output) # code inside if block
        output.append('JUMP IF_END_' + label_num)
        
        # ELSE BLOCK
        output.append('IF_ELSE_' + label_num + ':')
        self.children[2].compile(st, output) # code inside else block
        output.append('IF_END_' + label_num + ':') # ending label to jump to

class CmdWhile(CmdNode):
    def compile(self, st, output):
        st.is_while = True
        if self.children[0].eval_type(st) != 'bool':
            raise TypeParseError('If conditional must be bool! :' + self.children[0].eval_type(st))
        sym = st.type_sym_map[self.children[0].eval_type(st)]
        label_num = st.get_new_while_label_num()
        intermediate = st.declare_tmp()

        output.append('WHILE_BEGIN_' + label_num + ':')
        condition = self.children[0].compile(st, output)
        output.append('VAL_COPY ' + condition + ' ' + sym + intermediate) # so jump if always has a var
        output.append('JUMP_IF_0 ' + sym + intermediate + ' WHILE_END_' + label_num)
        self.children[1].compile(st, output)
        output.append('JUMP WHILE_BEGIN_' + label_num)
        output.append('WHILE_END_' + label_num + ':')

class CmdFor(CmdNode):
    def compile(self, st, output):
        st.is_while = False
        st.push_scope()
        typ = self.children[1].eval_type(st)
        ident = st.declare(self.children[0].value, typ)
        sym = st.type_sym_map[typ]

        memloc = self.children[1].compile(st, output)
        
        size = st.declare_tmp()
        place = st.declare_tmp()
        label_num = st.get_new_for_label_num()
        bool_eval = st.declare_tmp()
        output.append('AR_GET_SZ ' + memloc + ' %' + size)
        output.append('VAL_COPY %0 %' + place)
        output.append('FOR_BEGIN_' + label_num + ':')
        output.append('TEST_EQU %' + place + ' %' + size + ' %' + bool_eval)
        output.append('JUMP_IF_NE0 %' + bool_eval + ' FOR_END_' + label_num)
        output.append('AR_GET_NDX ' + memloc + ' %' + place + ' ' + sym + ident)

        self.children[2].compile(st, output)

        output.append('ADD %1 %' + place + ' %' + place)
        output.append('JUMP FOR_BEGIN_' + label_num)
        output.append('FOR_END_' + label_num + ':')
        
        st.pop_scope()

class CmdBreak(CmdNode):
    def compile(self, st, output):
        if st.is_while:
            output.append('JUMP WHILE_END_' + st.get_current_while_label_num())
        else:
            output.append('JUMP FOR_END_' + st.get_current_for_label_num())

class CmdDeclareArr(CmdNode):
    def compile(self, st, output):
        memloc = st.declare(self.children[1].value, self.children[0].value, True) # declare var
        if len(self.children) == 3: # allocate new array
            size = self.children[2].compile(st, output)
            if self.children[2].eval_type(st) != 'int':
                raise ImproperTypeError('Array size not an integer')
            output.append('VAL_COPY @s0 @' + memloc)
            output.append('AR_SET_SZ @' + memloc + ' ' + size)
            output.append('ADD @S0 %1 @S0')
            output.append('ADD @S0 ' + size + ' @S0')

# ============= ASSIGNMENT AND INITIALIZATION ==============

class CmdInitializeArr(CmdNode):
    def compile(self, st, output):
        memloc = st.declare(self.children[1].value, self.children[0].value, True)
        output.append('VAL_COPY ' + self.children[2].compile(st, output) + ' @' + memloc)

        if len(self.children) == 4:
            if self.children[3].eval_type(st) != 'int':
                raise ImproperTypeError('Array size not an integer')
            output.append('AR_SET_SZ @' + memloc + ' ' + self.children[3].compile(st, output))
        # memloc = st.declare(self.children[1].value, self.children[0].value, True) # declare var_type
        # if len(self.children) == 4:
        #     size = self.children[3].compile(st, output) # currently throwing away value, may not be the right idea
        #     if self.children[3].eval_type(st) != 'int':
        #         raise ImproperTypeError('Array size is not an integer on initialization.')
        # else:
        #     size = '@' + str(len(self.children[2]))
        # output.append('VAL_COPY @S0 @' + memloc)
        # output.append('AR_SET_SZ @' + memloc + ' ' + size)
        # output.append('ADD @S0 %1 @S0')
        # output.append('ADD @S0 ' + size + ' @S0')
        # tmp = st.declare_tmp()
        # output.append('VAL_COPY @0 @' + tmp)
        # for child in self.children[2]: # could overflow
        #     result = child.compile(st, output)
        #     output.append('AR_SET_NDX @' + memloc + ' @' + tmp + ' ' + result)
        #     output.append('ADD @1 @' + tmp + ' @' + tmp)

class CmdInitialize(CmdNode):
    def compile(self, st, output):
        val = self.children[1].compile(st, output)
        var = st.declare(self.children[0].value, self.children[2].value)
        dtype = self.eval_type(st)
        if dtype == 'int' or dtype == 'bool':
            output.append('VAL_COPY ' + val  + ' %' + var)
        elif dtype == 'float':
            output.append('VAL_COPY ' + val  + ' !' + var)
        elif dtype == 'char':
            output.append('VAL_COPY ' + val  + ' $' + var)
        else:
            raise ImproperTypeError('Initialize typing returned an inproper result :' + dtype) 
        return val  # returning the value, not the assignee's value/var name

    def eval_type(self, st):
        type0 = self.children[2].value
        type1 = self.children[1].eval_type(st)
        if type0 != type1:
            raise TypeParseError('Initialization value does not match type of var')
        return type0

class ExprRange(ExprNode):
    def compile(self, st, output):
        start = self.children[0].compile(st, output)
        if len(self.children) == 3:
            end = self.children[2].compile(st, output)
            step = self.children[1].compile(st, output)
        else:
            end = self.children[1].compile(st, output)
            step = '%1'
        tmp = st.declare_tmp()
        tmp2 = st.declare_tmp() 
        mod = st.declare_tmp()
        output.append('SUB ' + end + ' ' + start + ' %' + tmp)
        output.append('IDIV %' + tmp + ' ' + step + ' %' + tmp2)
        output.append('MOD %' + tmp + ' ' + step + ' %' + tmp) # detect remainder and add 1 if case
        output.append('TEST_NEQU %0 %' + tmp + ' %' + tmp)
        output.append('ADD %' + tmp + ' %' + tmp2 + ' %' + tmp)

        memloc = st.declare_tmp(True)
        place = st.declare_tmp()
        output.append('VAL_COPY ' + start + ' %' + place)
        output.append('VAL_COPY @S0 @' + memloc)
        output.append('VAL_COPY %0 %' + tmp2)
        output.append('ADD @S0 %' + tmp + ' @S0')
        output.append('ADD @S0 %1 @S0')
        output.append('AR_SET_SZ @' + memloc + ' %' + tmp)
        label_num = st.get_misc_jump_num()
        output.append('RANGE_JUMP_' + label_num + ':')
        output.append('AR_SET_NDX @' + memloc + ' %' + tmp2 + ' %' + place)
        output.append('ADD ' + step + ' %' + place + ' %' + place)
        output.append('ADD %1 %' + tmp2  + ' %' + tmp2)
        output.append('TEST_LESS %' + place + ' ' + end + ' %' + tmp)
        output.append('JUMP_IF_NE0 %' + tmp + ' RANGE_JUMP_' + label_num)

        return '@' + memloc
    def eval_type(self, st):
        return 'int'
    
class ExprAssign(ExprNode):
    def compile(self, st, output):
        val = self.children[1].compile(st, output)
        dtype = self.eval_type(st)
        if dtype == 'int' or dtype == 'bool':
            output.append('VAL_COPY ' + val  + ' %' + st.get_inter_name(self.children[0].value))
        elif dtype == 'float':
            output.append('VAL_COPY ' + val  + ' !' + st.get_inter_name(self.children[0].value))
        elif dtype == 'char':
            output.append('VAL_COPY ' + val  + ' $' + st.get_inter_name(self.children[0].value))
        else:
            raise ImproperTypeError('Assignment typing returned an inproper result :' + dtype)
        return val  # returning the value, not the assignee's value/var name

    def eval_type(self, st):
        type0 = st.get_type(self.children[0].value)
        type1 = self.children[1].eval_type(st)
        if type0 != type1:
            raise TypeParseError('ExprAssign was given two different data types')
        return type0

# =========== BASE NODES ================
    
class ExprID(ExprNode):
    def compile(self, st, output):
        dtype = self.eval_type(st)
        if st.is_arr(self.children[0].value):
            # raise Exception('Array called exprID')
            return '@' + st.get_inter_name(self.children[0].value)
        if dtype == 'int' or dtype == 'bool':
            return '%' + str(st.get_inter_name(self.children[0].value))
        if dtype == 'char':
            return '$' + str(st.get_inter_name(self.children[0].value))
        if dtype == 'float':
            return '!' + str(st.get_inter_name(self.children[0].value))
        raise ImproperTypeError('ID evaluation returned an inproper result :' + dtype)
    def eval_type(self, st):
        return st.get_type(self.children[0].value)

class ExprIDArr(ExprNode):
    def compile(self, st, output):
        if not st.is_arr(self.children[0].value):
            raise Exception('scalar called ExprIdArr')
        return '@' + st.get_inter_name(self.children[0].value)
    def eval_type(self, st):
        return st.get_type(self.children[0].value)
    
class ExprEvalArrElm(ExprNode):
    def compile(self, st, output):
        dtype = st.get_type(self.children[0].value)
        sym = st.type_sym_map[dtype]
        if not st.is_arr(self.children[0].value):
            raise TypeParseError('Not array type indexed')
        inter_name = st.get_inter_name(self.children[0].value)
        result = self.children[1].compile(st, output)
        if self.children[1].eval_type(st) != 'int':
            raise ImproperTypeError('Non int used to index array')
        tmp = st.declare_tmp()
        output.append('AR_GET_NDX @' + inter_name + ' ' + result + ' ' + sym + tmp)
        return sym + tmp
    def eval_type(self, st):
        return st.get_type(self.children[0].value)

class ExprAssignArrElm(ExprNode):
    def compile(self, st, output):
        dtype_arr = st.get_type(self.children[0].value)
        memloc = st.get_inter_name(self.children[0].value)
        index = self.children[1].compile(st, output)
        if self.children[1].eval_type(st) != 'int':
            raise ImproperTypeError('Non int used to index array')
        sym = st.type_sym_map[dtype_arr]
        value = self.children[2].compile(st, output)
        dtype_val = self.children[2].eval_type(st)

        if dtype_arr != dtype_val:
            raise TypeParseError('Index assignment recieved two different types')
        
        output.append('AR_SET_NDX @' + memloc + ' ' + index + ' ' + value)
        return value

    def eval_type(self, st):
        return self.children[1].eval_type(st)

class ExprInt(ExprNode):
    def compile(self, st, output):
        return '%' + self.children[0].value
    def eval_type(self, st):
        return 'int'

class ExprBool(ExprNode):
    def compile(self, st, output):
        return '%0' if self.children[0].value == 'False' else '%1'
    def eval_type(self, st):
        return 'bool'

class ExprFloat(ExprNode):
    def compile(self, st, output):
        return '!' + self.children[0].value
    def eval_type(self, st):
        return 'float'

class ExprChar(ExprNode):
    def compile(self, st, output):
        if len(self.children[0].value) == 4:
            return '$\'' + st.escaped_char_map[self.children[0].value[2]] + '\''
        return '$' + self.children[0].value
    def eval_type(self, st):
        return 'char'

# ========== NON ASSIGNMENT OPERATIONS ====================

class ExprMathBinary(ExprNode):
    def compile(self, st, output):
        # will have to do ifs for all math statements. Store them in a variable temp or S# or something
        last = st.declare_tmp()
        typ = self.eval_type(st)
        sym = st.type_sym_map[typ]
        if self.children[1].value == '+':
            output.append('ADD ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' ' + sym + last)

        elif self.children[1].value == '-':
            output.append('SUB ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' ' + sym + last)

        elif self.children[1].value == '*':
            output.append('MUL ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' ' + sym + last)

        elif self.children[1].value == '/':
            if sym == '!': # use float circuits
                output.append('DIV ' + self.children[0].compile(st, output) + ' ' +
                              self.children[2].compile(st, output) + ' ' + sym + last)
            else: # use integer circuits
                output.append('IDIV ' + self.children[0].compile(st, output) + ' ' +
                              self.children[2].compile(st, output) + ' ' + sym + last)
                

        elif self.children[1].value == '%':
            if sym != '%': # may have to edit depending on where floats are allowed and where they aren't
                raise TypeParseError('Non-integer fed to modulus operation')
            output.append('MOD ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' ' + sym + last)

        return sym + last

    def eval_type(self, st):
        type0 = self.children[0].eval_type(st)
        type1 = self.children[2].eval_type(st)
        if type0 != 'int' and type0 != 'float':
            raise TypeParseError('LAS of binary operator is not a float or int: ' + type0)
        if type1 != 'int' and type1 != 'float':
            raise TypeParseError('RAS of binary operator is not a float or int: ' + type1)
        return type0 if type0 == type1 else 'float'

class ExprMathNegate(ExprNode):
    def compile(self, st, output):
        last = st.declare_tmp()
        typ = self.eval_type(st)
        sym = st.type_sym_map[typ]
        output.append('MUL ' + self.children[0].compile(st, output) + ' %-1 ' + sym + last)
        return sym + last

    def eval_type(self, st):
        return self.children[0].eval_type(st)

class ExprLogicNegate(ExprNode):
    def compile(self, st, output):
        last = st.declare_tmp()
        output.append('TEST_EQU ' + self.children[0].compile(st, output) + ' %0 ' + '%' + last)
        return '%' + last
    def eval_type(self, st):
        typ = self.children[0].eval_type(st)
        if typ != 'bool':
            raise TypeParseError('Tried to negate a non-bool type ' + typ)
        return 'bool'

class ExprLogicBin(ExprNode):
    def compile(self, st, output):
        if self.children[1].value == 'and':
            tmp = st.declare_tmp()
            output.append('MUL ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' %' + tmp)

            output.append('TEST_NEQU ' + '%' + tmp + ' %0 %' + tmp)

            return '%' + tmp

        elif self.children[1].value == 'or':
            tmp = st.declare_tmp()
            output.append('ADD ' + self.children[0].compile(st, output) + ' ' +
                          self.children[2].compile(st, output) + ' %' + tmp)

            output.append('TEST_NEQU ' + '%' + tmp + ' %0 %' + tmp)

            return '%' + tmp
            
        elif self.children[1].value == 'xor':
            tmp = st.declare_tmp()
            tmp2 = st.declare_tmp()
            output.append('TEST_EQU ' + self.children[0].compile(st, output) + '%0 %' + tmp)
            output.append('TEST_EQU ' + self.children[2].compile(st, output) + '%0 %' + tmp2)

            output.append('TEST_NEQU %' + tmp + ' %' + tmp2 + ' %' + tmp)
            return '%' + tmp

        raise NotImplementedError('Nah man')

    def eval_type(self, st):
        type0 = self.children[0].eval_type(st)
        type1 = self.children[2].eval_type(st)
        if type0 != 'bool' or type1 != 'bool':
            raise TypeParseError('Improper types for logic binary op')
        return 'bool'

class ExprLogicComp(ExprNode):
    def compile(self, st, output):
        self.eval_type(st)
        lhs = st.type_sym_map[self.children[0].eval_type(st)] + st.declare_tmp()
        output.append('VAL_COPY ' + self.children[0].compile(st, output) + ' ' + lhs)
        rhs = st.type_sym_map[self.children[2].eval_type(st)] + st.declare_tmp()
        output.append('VAL_COPY ' + self.children[2].compile(st, output) + ' ' + rhs)
        if self.children[1].value == '==':
            last = st.declare_tmp()
            output.append('TEST_EQU ' + lhs + ' ' +
                          rhs + ' %' + last)
            return '%' + last
        
        elif self.children[1].value == '~=':
            last = st.declare_tmp()
            output.append('TEST_NEQU ' + lhs + ' ' +
                          rhs + ' %' + last)
            return '%' + last
        
        elif self.children[1].value == '<=':
            last = st.declare_tmp()
            last2 = st.declare_tmp()
            
            output.append('TEST_LESS ' + lhs + ' ' +
                          rhs + ' %' + last)

            output.append('TEST_EQU ' + lhs + ' ' +
                      rhs + ' %' + str(last2))

            output.append('ADD ' + ' %' + last + ' %' + str(last2) + ' %' + last)
            
            return '%' + last
        
        elif self.children[1].value == '>=':
            last = st.declare_tmp()
            last2 = st.declare_tmp()
            
            output.append('TEST_GTR ' + lhs + ' ' +
                          rhs + ' %' + last)

            output.append('TEST_EQU ' + lhs + ' ' +
                      rhs + ' %' + str(last2))

            output.append('ADD ' + ' %' + last + ' %' + str(last2) + ' %' + last)

            return '%' + last
        
        elif self.children[1].value == '<':
            last = st.declare_tmp()
            output.append('TEST_LESS ' + lhs + ' ' +
                          rhs + ' %' + last)
            return '%' + last
        
        elif self.children[1].value == '>':
            last = st.declare_tmp()
            output.append('TEST_GTR ' + lhs + ' ' +
                          rhs + ' %' + last)
            return '%' + last

        raise NotImplementedError('Nah man') # very necessary
    
    def eval_type(self, st):
        type0 = self.children[0].eval_type(st)
        type1 = self.children[2].eval_type(st)
        if (type0 == 'int' or type0 == 'float') and (type1 == 'int' or type1 == 'float'):
            return 'bool'

        if type0 == 'char' and type1 == 'char':
            return 'bool'

        if type0 == 'bool' and type1 == 'bool':
            return 'bool'

        raise TypeParseError('Improper types for lofic binary comp op ' + type0 + ' ' + type1)



class ExprMathSum(ExprNode):
    def compile(self, st, output):
        tmp = st.declare_tmp()
        sym = st.type_sym_map[self.children[0].eval_type(st)]
        output.append('VAL_COPY ' + sym + '0 '+ sym + tmp)
        for i in self.children:
            result = i.compile(st, output)
            typ = i.eval_type(st)
            sym = st.type_sym_map[typ]
            if result[0] == '@':
                size = st.declare_tmp()
                element = st.declare_tmp()
                end = st.declare_tmp()
                label_num = st.get_operation_label_num()
                output.append('AR_GET_SZ ' + result + ' %' + size)
                index = st.declare_tmp()
                output.append('VAL_COPY %0 %' + index)
                output.append('SUM_OPERATION_' + label_num + ':')
                output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
                output.append('ADD ' + sym + tmp + ' ' + sym + element + ' '  +sym + tmp)
                output.append('ADD %1 %' + index + ' %' + index)
                output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
                output.append('JUMP_IF_NE0 %' + end + ' SUM_OPERATION_' + label_num)
            else:
                output.append('ADD ' + result + ' '+ sym + tmp + ' '+ sym + tmp)

        return sym + tmp

    def eval_type(self, st): # may augment if there are floats and for type checking
        return self.children[0].eval_type(st)

class ExprMathProd(ExprNode):
    def compile(self, st, output):
        tmp = st.declare_tmp()
        sym = st.type_sym_map[self.children[0].eval_type(st)]
        output.append('VAL_COPY ' + sym + '1 '+ sym + tmp)
        for i in self.children:
            result = i.compile(st, output)
            typ = i.eval_type(st)
            sym = st.type_sym_map[typ]
            if result[0] == '@':
                size = st.declare_tmp()
                element = st.declare_tmp()
                end = st.declare_tmp()
                label_num = st.get_operation_label_num()
                output.append('AR_GET_SZ ' + result + ' %' + size)
                index = st.declare_tmp()
                output.append('VAL_COPY %0 %' + index)
                output.append('SUM_OPERATION_' + label_num + ':')
                output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
                output.append('MUL ' + sym + tmp + ' ' + sym + element + ' '  +sym + tmp)
                output.append('ADD %1 %' + index + ' %' + index)
                output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
                output.append('JUMP_IF_NE0 %' + end + ' SUM_OPERATION_' + label_num)
            else:
                output.append('ADD ' + result + ' '+ sym + tmp + ' '+ sym + tmp)

        return sym + tmp

    def eval_type(self, st): # may augment if there are floats and for type checking
        return self.children[0].eval_type(st)

class ArrExprVector(ExprNode):
    def compile(self, st, output):
        if len(self.children) == 1:
            first = self.children[0].compile(st, output)
            if first[0] == '@':
                return first
            num_elements = len(self.children)
            memloc = st.declare_tmp(True)
            output.append('VAL_COPY @S0 @' + memloc)
            output.append('ADD @S0 %' + str(num_elements+1) + ' @S0')
            output.append('AR_SET_SZ @' + memloc + ' %'+ str(num_elements))
            output.append('AR_SET_NDX @' + memloc + ' %0 ' + first)
            return '@' + memloc

            
        num_elements = len(self.children)
        memloc = st.declare_tmp(True)
        output.append('VAL_COPY @S0 @' + memloc)
        output.append('ADD @S0 %' + str(num_elements+1) + ' @S0')
        output.append('AR_SET_SZ @' + memloc + ' %'+ str(num_elements))

        for c in range(len(self.children)):
            output.append('AR_SET_NDX @' + memloc + ' %' + str(c) + ' ' +
                          self.children[len(self.children)-c-1].compile(st, output))
        return '@' + memloc
        
    def eval_type(self, st):
        return self.children[0].eval_type(st)

class ArrCopy(ExprNode):
    def compile(self, st, output):
        other = st.get_inter_name(self.children[0].value)
        memloc = st.declare_tmp(True)
        size = st.declare_tmp()
        output.append('AR_GET_SZ @' + other + ' %' + size)
        output.append('VAL_COPY @S0 @' + memloc)
        output.append('AR_SET_SZ @' + memloc + ' %' + size)
        output.append('ADD @S0 %1 @S0')
        output.append('ADD @S0 %' + size + ' @S0')
        output.append('AR_COPY @' + other + ' @' + memloc)
        return '@' + memloc
    def eval_type(self, st):
        return st.get_type(self.children[0].value) # return copied arr type


class ExprLength(ExprNode):
    def compile(self, st, output):
        if not st.is_arr(self.children[0].value):
            raise TypeParseError('.length called on a non array type.')

        memloc = st.get_inter_name(self.children[0].value)
        result = st.declare_tmp()
        output.append('AR_GET_SZ @' + memloc + ' @' + result)
        return '%' + result
    def eval_type(self, st):
        return 'int'

class ExprMathMin(ExprNode):
    def compile(self, st, output):
        sym = st.type_sym_map[self.eval_type(st)]
        tmp = st.declare_tmp()
        minimum = st.declare_tmp()
        result = self.children[0].compile(st, output)
        if result[0] == '@':
            size = st.declare_tmp()
            element = st.declare_tmp()
            end = st.declare_tmp()
            label_num = st.get_operation_label_num()
            min_num = st.get_misc_jump_num()
            output.append('VAL_COPY ' + sym + '1000000 ' + sym + minimum)  # very jank
            output.append('AR_GET_SZ ' + result + ' %' + size)
            index = st.declare_tmp()
            output.append('VAL_COPY %0 %' + index)
            output.append('MIN_OPERATION_' + label_num + ':')
            output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
            output.append('TEST_LESS ' + sym + element + ' ' + sym + minimum + ' %' + tmp)
            output.append('JUMP_IF_0 %' + tmp + 'MIN_VECTOR_JUMP_' + min_num)
            output.append('VAL_COPY ' + sym + element + ' ' + sym + minimum)
            output.append('MIN_VECTOR_JUMP_' + min_num + ':')
            output.append('ADD %1 %' + index + ' %' + index)
            output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
            output.append('JUMP_IF_NE0 %' + end + ' MIN_OPERATION_' + label_num)
        else:
            raise ImproperTypeError('minimum_of called on scalar')
        return sym + minimum

    def eval_type(self, st):
        if not self.children:
            raise ImproperTypeError('minimum_of has no arguments')
        datatype = self.children[0].eval_type(st)
        for i in self.children:
            if self.children[0].eval_type(st) != datatype:
                raise TypeParseError('Data types of minimum_of arguments must be the same!')
        return datatype

class ExprMathMax(ExprNode):
    def compile(self, st, output):
        sym = st.type_sym_map[self.eval_type(st)]
        tmp = st.declare_tmp()
        minimum = st.declare_tmp()
        result = self.children[0].compile(st, output)
        if result[0] == '@':
            size = st.declare_tmp()
            element = st.declare_tmp()
            end = st.declare_tmp()
            label_num = st.get_operation_label_num()
            min_num = st.get_misc_jump_num()
            output.append('VAL_COPY ' + sym + '-1000000 ' + sym + minimum)  # very jank
            output.append('AR_GET_SZ ' + result + ' %' + size)
            index = st.declare_tmp()
            output.append('VAL_COPY %0 %' + index)
            output.append('MIN_OPERATION_' + label_num + ':')
            output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
            output.append('TEST_GTR ' + sym + element + ' ' + sym + minimum + ' %' + tmp)
            output.append('JUMP_IF_0 %' + tmp + 'MIN_VECTOR_JUMP_' + min_num)
            output.append('VAL_COPY ' + sym + element + ' ' + sym + minimum)
            output.append('MIN_VECTOR_JUMP_' + min_num + ':')
            output.append('ADD %1 %' + index + ' %' + index)
            output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
            output.append('JUMP_IF_NE0 %' + end + ' MIN_OPERATION_' + label_num)
        else:
            raise ImproperTypeError('maximum_of called on scalar')
        return sym + minimum

    def eval_type(self, st):
        if not self.children:
            raise ImproperTypeError('minimum_of has no arguments')
        datatype = self.children[0].eval_type(st)
        for i in self.children:
            if self.children[0].eval_type(st) != datatype:
                raise TypeParseError('Data types of minimum_of arguments must be the same!')
        return datatype

class ExprLogicAny(ExprNode):
    def compile(self, st, output):
        
        tmp = st.declare_tmp()

        output.append('VAL_COPY %0 %' + tmp)
        result = self.children[0].compile(st, output)
        if result[0] == '@':
            size = st.declare_tmp()
            element = st.declare_tmp()
            end = st.declare_tmp()
            label_num = st.get_operation_label_num()
            sym = st.type_sym_map[self.children[0].eval_type(st)]
            output.append('AR_GET_SZ ' + result + ' %' + size)
            index = st.declare_tmp()
            output.append('VAL_COPY %0 %' + index)
            output.append('ANY_OPERATION_' + label_num + ':')
            output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
            output.append('ADD ' + sym + tmp + ' ' + sym + element + ' ' + sym + tmp)
            output.append('ADD %1 %' + index + ' %' + index)
            output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
            output.append('JUMP_IF_NE0 %' + end + ' ANY_OPERATION_' + label_num)
        else:
            for c, i in enumerate(self.children):
                output.append('ADD ' + i.compile(st, output) + ' %' + tmp + ' %' + tmp)

        output.append('TEST_NEQU %0 %' + tmp + ' %' + tmp)

        return '%' + tmp

    def eval_type(self, st):
        for i in self.children:
            if i.eval_type(st) != 'bool':
                raise TypeParseError('any_of input type is not bool')
        return 'bool'

class ExprLogicEvery(ExprNode):
    def compile(self, st, output):
        tmp = st.declare_tmp()

        output.append('VAL_COPY %1 %' + tmp)
        result = self.children[0].compile(st, output)
        if result[0] == '@':
            size = st.declare_tmp()
            element = st.declare_tmp()
            end = st.declare_tmp()
            label_num = st.get_operation_label_num()
            sym = st.type_sym_map[self.children[0].eval_type(st)]
            output.append('AR_GET_SZ ' + result + ' %' + size)
            index = st.declare_tmp()
            output.append('VAL_COPY %0 %' + index)
            output.append('ANY_OPERATION_' + label_num + ':')
            output.append('AR_GET_NDX ' + result + ' %' + index + ' ' + sym + element)
            output.append('MUL ' + sym + tmp + ' ' + sym + element + ' ' + sym + tmp)
            output.append('ADD %1 %' + index + ' %' + index)
            output.append('TEST_LESS %' + index + ' %' + size + ' %' + end)
            output.append('JUMP_IF_NE0 %' + end + ' ANY_OPERATION_' + label_num)
        else:
            for c, i in enumerate(self.children):
                output.append('MUL ' + i.compile(st, output) + ' %' + tmp + ' %' + tmp)

        output.append('TEST_NEQU %0 %' + tmp + ' %' + tmp)

        return '%' + tmp

    def eval_type(self, st):
        for i in self.children:
            if i.eval_type(st) != 'bool':
                raise TypeParseError('every_of input type is not bool')
        return 'bool'

# ======== FUNCTION SHIT ========
class CmdFunctionNode(CmdNode):
    def compile(self, st, output):
        st.declare_function(self.children[2].value, self.children[0].value, self.children[4], self.children[1])
        output.append('JUMP function-end-' + self.children[0].value)
        output.append('function-start-' + self.children[0].value + ':')
        st.push_scope()

        ret_addr = st.declare_tmp()
        output.append('POP @' + ret_addr) # get return addr
        st.current_return_label = ret_addr # store return addr in sym table for return statements
        for argument in self.children[1]: # for each argument, declare and pop off value from stack
            var = st.declare(argument[1].value, argument[0].value, argument[2])
            sym = st.type_sym_map[argument[0].value] if not argument[2] else '@'
            output.append('POP ' + sym + var)

        self.children[3].compile(st, output) # define function body
        output.append('function-end-' + self.children[0].value + ':')
        st.pop_scope()
        st.current_return_label = '' # clear return label

class CmdArgListNode(CmdNode):
    def compile(self, st, output):
        raise NotImplementedError('Arg list was compiled')

class CmdParamNode(CmdNode):
    def compile(self, st, output):
        raise NotImplementedError('Param List was compiled')

class ExprFuncCall(ExprNode):
    def compile(self, st, output):
        st.check_parameters(self.children[0].value, self.children[1])

        # push variables onto stack
        state = st.get_function_state()
        for var in state:
            output.append('PUSH ' + var)

        # push parameters onto stack.
        for param in self.children[1].children:
            ret = param.compile(st, output)
            output.append('PUSH ' + ret)

        ret_label = st.get_function_return()
        output.append('PUSH ' + ret_label) # push return label onto stack
        output.append('JUMP function-start-' + self.children[0].value)
        output.append(ret_label + ':') # return label

        ret_val = ''
        if st.is_arr_func(self.children[0].value): # see if it is an array ret_valurn
            sym = '@' # isarr
            ret_val = st.declare_tmp(True)
        else:
            sym = st.type_sym_map[self.eval_type(st)] # is not arr
            ret_val = st.declare_tmp(False)
        output.append('POP ' + sym + ret_val) # get ret value

        # restore function state
        for var in reversed(state):
            output.append('POP ' + var)
        return sym + ret_val # return value

    def eval_type(self, st):
        return st.function_table[self.children[0].value][0] # use symbol_table

class CmdReturn(CmdNode):
    def compile(self, st, output):
        typ = self.children[0].eval_type(st)
        # sym = st.type_sym_map[typ]
        val = self.children[0].compile(st, output)
        output.append('PUSH ' + val)
        if st.current_return_label:
            output.append('JUMP @' + st.current_return_label)
        else:
            raise ImproperReturnError('Return statement not in a function.') # uses different functions setting this
