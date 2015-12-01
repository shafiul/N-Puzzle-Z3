from z3 import *

class SSA():

    def __init__(self, creator, var_name=None, shadow_data=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        self.s = shadow_data

    @property
    def n(self):
        self.i += 1
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i)

    @property
    def c(self):
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i)

    @property
    def nn(self):
        return self.inst(self.i + 1)

    def inc(self):
        self.i += 1

    @property
    def v(self):
        return self.inst

    @property
    def len(self):
        return (self.i + 1)


class SSA_Arr():

    def __init__(self, creator, var_name=None, shadow_data=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        self.s = shadow_data

    def n(self, index):
        self.i += 1
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i, index)

    def c(self, index):
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i, index)

    def nn(self, index):
        return self.inst(self.i + 1, index)

    def inc(self):
        self.i += 1

    @property
    def v(self):
        return self.inst

    @property
    def len(self):
        return (self.i + 1)

    
class SSA_Vect():

    def __init__(self, creator, var_name=None):
        self.var_name = var_name
        self.creator = creator

        self.inst = [creator(),]

        self.i = 0

    @property
    def n(self):
        self.i += 1
        self._create_next(self.i)
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst[self.i]

    @property
    def c(self):
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst[self.i]

    @property
    def nn(self):
        self._create_next(self.i + 1)
        return self.inst[self.i + 1]

    def inc(self):
        self.i += 1
        self._create_next(self.i)


    @property
    def v(self):
        return self.inst

    def _create_next(self, iter):
        self.inst.append(self.creator(iter=iter))

    def get(self, index):
        return self.inst[index]
    

def BitVecVector(prefix, sz, N, iter=0):
    """Create a vector with N Bit-Vectors of size sz"""
    return [ BitVec('%s[%s]__%s' % (prefix, i, iter), sz) for i in range(N) ]


def get_BitInt_SSA(varname, numbits):
    return Function(varname, BitVecSort(numbits), BitVecSort(numbits))