from logging import _srcfile
import re
from .errors import *

class InterpreterST():

    class MemData:
        def __init__(self, dtype, data, atype=None):
            self.dtype = dtype
            self.data = data

        def as_string(self):
            return f'{self.dtype}{self.data}' if self.dtype != '$' else f"$'{self.data}'"

        def is_int(self):
            return self.dtype == '%'
        
        def is_float(self):
            return self.dtype == '!'
        
        def is_char(self):
            return self.dtype == '$'

        def is_numeric(self):
            return self.is_float() or self.is_int()
            
            
    

    def __init__(self):
        self.labels = {}
        self.memory = {}
        self.ip = 0
        self.nextHeapLoc = 10000
        self.stack = []


    def push_stack(self, value):
        dtype = value[0]
        to_store = self.lookup(value, allow_default_value=True)
        if dtype == '$':
            to_store = f"'{to_store}'"
        self.stack.append(f'{dtype}{to_store}')


    def pop_stack(self):
        return self.stack.pop()


    def instantiate(self, dtype, data):
        if dtype == '%':
            return int(data)
        elif dtype == '!':
            return float(data)
        elif dtype == '$':
            return data[1:-1]
        elif dtype == '@':
            retval = int(data)
            assert(retval >= 0)
            return retval
        else:
            return data

    
    def sanity_check(self, val, expected_dtype):
        if isinstance(val, int) and expected_dtype == '%':
            return
        elif isinstance(val, float) and expected_dtype == '!':
            return
        elif isinstance(val, str):
            if val in ['!', '%', '@', '$']:
                return
            if expected_dtype == '$':
                return
        elif isinstance(val, int) and expected_dtype == '@' and val >= 0:
            return
        elif isinstance(val, str) and expected_dtype == '@':
            return
        raise TypeError(f'Sanity check: {expected_dtype} expected for {val} got instance of {type(val)}.')



    def var2loc(self, var):
        if not self.is_var(var):
            raise Exception(f'Expected var; got {var}')
        return int(var[2:])


    def val_copy(self, src, dst):
        loc_dst = self.var2loc(dst)
        dtype_dst = dst[0]
        src = self.lookup(src, dequote=False)
        self.sanity_check(src, dtype_dst)
        self.memory[loc_dst] = self.MemData(dtype_dst, src)


    def is_var(self, symb):
        if not isinstance(symb, str):
            return False
        return self.is_svar(symb) or self.is_avar(symb)


    def is_svar(self, symb):
        symb = symb[1:]
        if not isinstance(symb, str):
            return False
        return re.match(r'^[Ss]\d+', symb) != None


    def is_avar(self, symb):
        symb = symb[1:]
        if not isinstance(symb, str):
            return False
        return re.match(r'^[Aa]\d+', symb) != None


    def lookup(self, symb, dequote=True, allow_default_value=False):

        if not isinstance(symb, str):  # It's an interpreted value 
            return symb
        
        # It's either a variable name of the string representation of something
        if self.is_var(symb): #It's a variable
            dtype_src = symb[0]
            loc = self.var2loc(symb)
            if loc not in self.memory:
                if not allow_default_value:
                    raise UninitializedMemoryRequestError(symb)
                else:
                    if dtype_src == '$':
                        return '?'
                    else:
                        return 0
            to_return = self.memory[loc].data
            self.sanity_check(to_return, dtype_src)
            return to_return
        else:
            if len(symb) == 0:
                raise Exception('Unable to lookup an empty string')
            if symb in ['%n', '%t', '%%', "%'"]:
                return symb
            dtype = symb[0]
            if dtype not in ['%', '$', '!', '@']:
                return symb
            symb = symb[1:]  # Remove type information for now
            return self.instantiate(dtype, symb)
    

    def set_ip(self, loc):
        self.ip = loc


    def next(self):
        self.ip += 1


    def get_label(self, label):
        if label in self.labels:
           return f'@{self.labels[label]}'
        else:
            raise LabelNotFoundError(f'Unable to find label {label}')

    
    def add_label(self, label, line):
        self.labels[label] = line

