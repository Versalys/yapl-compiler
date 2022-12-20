'''
class that implements the sumbol table and associated exceptions

written by Aidan Erickson
'''

class RedeclaredException(Exception):
    pass

class UndeclaredException(Exception):
    pass

class SymbolTable():
    def __init__(self):
        # ids stores variable identifiers -> S# names map
        # self.ids = {} # contains a mapping of variable names to S# values (S#, type)
        self.scopes = []
        self.type_sym_map = {'int':'%', 'bool':'%', 'float':'!', 'char':'$'}
        self.escaped_char_map = {'n' : '%n', '\'' : '%\'', 't' : '%t', '%' : '%%', '"' : '"'}
        self.tmp_var_num = 1
        self.if_label_num = 0
        self.while_label_num = 0
        self.jump_label_num = 0 # for misc jumps for functions like min/max_of
        self.for_label_num = 0
        self.operation_label_num = 0
        self.is_while = True
        self.function_table = {}
        self.current_return_label = ''
        self.func_return_num = 0

    def get_function_return(self):
        self.func_return_num += 1
        return 'function-return-' + str(self.func_return_num-1)

    def declare_function(self, typ, identifier, is_arr, arguments):
        self.function_table[identifier] = typ, is_arr, [(t.value, a) for t,i,a in arguments]

    def check_parameters(self, identifier, arguments):
        if len(arguments) - 1 == len(self.function_table[identifier][2]):
            return True
        return False
        
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def get_if_label_num(self):
        self.if_label_num += 1
        return str(self.if_label_num - 1)

    def get_new_while_label_num(self):
        self.while_label_num += 1
        return str(self.while_label_num - 1)

    def get_current_while_label_num(self):
        return str(self.while_label_num - 1)

    def get_new_for_label_num(self):
        self.for_label_num += 1
        return str(self.for_label_num-1)

    def get_current_for_label_num(self):
        return str(self.for_label_num-1)

    def get_operation_label_num(self):
        self.operation_label_num += 1
        return str(self.operation_label_num - 1)

    def get_misc_jump_num(self):
        self.jump_label_num += 1
        return str(self.jump_label_num - 1)
        
    def get_inter_name(self, ident):
        for i in range(len(self.scopes)-1, -1, -1):
            if ident in self.scopes[i]:
                return ('S' if not self.scopes[i][ident][2] else 'A')+ str(self.scopes[i][ident][0])
        raise UndeclaredException('Variable not found in any scope. : ' + ident)
        
    def is_declared(self, ident):
        return ident in self.scopes[-1]

    def get_type(self, ident):
        for i in range(len(self.scopes)-1, -1, -1):
            if ident in self.scopes[i]:
                return self.scopes[i][ident][1]
        raise UndeclaredException('Variable not defined in any scope. : ' + ident)

    def declare_tmp(self, is_scalar=False):
        tmp = self.tmp_var_num
        self.tmp_var_num += 1
        return ('S' if not is_scalar else 'A') + str(tmp)

    def declare(self, ident, var_type, is_arr=False): # using the same declare method for arrays
        assert self.scopes # scopes must not be empty
            
        if not self.is_declared(ident):
            self.scopes[-1][ident] = self.tmp_var_num, var_type, is_arr
            self.tmp_var_num += 1
        else:
            raise RedeclaredException(f'{ident} is already declared')
        return ('S' if not is_arr else 'A')+ str(self.tmp_var_num - 1)

    def get_function_state(self):
        assert self.scopes # scopes cannot be empty

        ret = []
        for var in self.scopes[-1].values():
            ret.append(('@A' if var[2] else (self.type_sym_map[var[1]] + 'S')) + str(var[0]))
        return ret

    def is_arr(self, ident):
        for i in range(len(self.scopes)-1, -1, -1):
            if ident in self.scopes[i]:
                return self.scopes[i][ident][2] # return bool representing is_arr
        raise UndeclaredException('Variable not found in any scope.')

    def is_arr_func(self, ident):
        return self.function_table[ident][1]
