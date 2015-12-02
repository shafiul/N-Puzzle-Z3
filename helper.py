from z3 import *

class SSA():

    def __init__(self, creator, var_name=None, shadow_data=None, solver=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        # self.s = shadow_data
        self.solver=solver

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

    def plusplus(self):
        self.solver.add((1 + self.c) == self.n)

    def minusminus(self):
        self.solver.add((self.c - 1) == self.n)

    def assign(self, elem, current=False):
        target = self.c if current else self.n
        self.solver.add(target == elem)
        return target



class SSA_Arr():

    def __init__(self, creator, var_name=None, solver=None, num_elements=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        self.s = solver
        self.num_elements = num_elements

    # def n(self, index):
    #     self.i += 1
    #     # print('Returning {} th version of {} '.format(self.i, self.var_name))
    #     return self.inst(self.i, index)

    def c(self, index):
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i, index)

    def nn(self, index):
        return self.inst(self.i + 1, index)

    def p(self, index):
        return self.inst(self.i - 1, index)    

    def inc(self):
        self.i += 1

    def u(self, position, elem):
        """
            Creates a new version of this array (updates self.i)
            In the new version, all elements are copied from the previous version, except
            the element at `position`, which has new element `elem`
        """

        self.inc()

        for i in range(self.num_elements):
            self.s.add(Or(
                And(position == i, self.c(i) == elem),
                And(position != i, self.c(i) == self.p(i))
            ))

    def swap(self, pos1, pos2):

        # pos1_value = self.c(pos1)

        self.inc()

        for i in range(self.num_elements):
            self.s.add(Or(
                And(pos1 == i, self.c(i) == self.p(pos2)),
                And(pos2 == i, self.c(i) == self.p(pos1)),
                And(pos1 != i, self.c(i) == self.p(i))
            ))


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