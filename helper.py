from z3 import *

class SSA():

    def __init__(self, creator, var_name=None, shadow_data=None, solver=None, init_val=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        # self.s = shadow_data
        self.solver=solver

        if init_val is not None:
            self.assign(init_val, current=True)

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

    def plusplus(self, add_to_solver=True,  gen_else=False):

        c = self.c
        n = self.n

        conds = ((1 + c) == n)
        else_conds = None

        if gen_else:
            else_conds = (c == n)

        if add_to_solver:
            self.solver.add(conds)
        else:
            return (conds, else_conds)

    def minusminus(self):
        self.solver.add((self.c - 1) == self.n)

    def assign(self, elem, current=False):
        target = self.c if current else self.n
        self.solver.add(target == elem)
        return target



class SSA_Arr():

    def __init__(self, creator, var_name=None, solver=None, num_elements=None, init_val=None):
        self.var_name = var_name
        self.inst = creator

        self.i = 0
        self.s = solver
        self.num_elements = num_elements

        if init_val is not None:
            self.initialize_array(init_val)

    # def n(self, index):
    #     self.i += 1
    #     # print('Returning {} th version of {} '.format(self.i, self.var_name))
    #     return self.inst(self.i, index)

    def initialize_array(self, init_val):
        for i in range(self.num_elements):
            self.s.add(self.c(i) == init_val[i])

    def c(self, index):
        # print('Returning {} th version of {} '.format(self.i, self.var_name))
        return self.inst(self.i, index)

    def nn(self, index):
        return self.inst(self.i + 1, index)

    def p(self, index):
        return self.inst(self.i - 1, index)    

    def inc(self):
        self.i += 1

    def u(self, position, elem, add_to_solver=True, gen_else=False):
        """
            Creates a new version of this array (updates self.i)
            In the new version, all elements are copied from the previous version, except
            the element at `position`, which has new element `elem`
        """

        self.inc()
        conds = []
        else_conds = []

        for i in range(self.num_elements):
            conds.append(Or(
                And(position == i, self.c(i) == elem),
                And(position != i, self.c(i) == self.p(i))
            ))

            if gen_else:
                else_conds.append(self.c(i) == self.p(i))

        if add_to_solver:
            self.s.add(*conds)
        else:
            return (conds, else_conds,)

    def swap(self, pos1, pos2, add_to_solver=True, gen_else=False):

        # pos1_value = self.c(pos1)

        self.inc()
        conds = []
        else_conds = []

        for i in range(self.num_elements):
            conds.append(Or(
                And(pos1 == i, self.c(i) == self.p(pos2)),
                And(pos2 == i, self.c(i) == self.p(pos1)),
                And(pos1 != i, pos2 != i, self.c(i) == self.p(i))
            ))

            if gen_else:
                else_conds.append(self.c(i) == self.p(i))     # Each element in the new version is same as old

        if add_to_solver:
            self.s.add(And(*conds))
        else:
            return (conds, else_conds,)


    @property
    def v(self):
        return self.inst

    @property
    def len(self):
        return (self.i + 1)

    
# class SSA_Vect():

#     def __init__(self, creator, var_name=None):
#         self.var_name = var_name
#         self.creator = creator

#         self.inst = [creator(),]

#         self.i = 0

#     @property
#     def n(self):
#         self.i += 1
#         self._create_next(self.i)
#         # print('Returning {} th version of {} '.format(self.i, self.var_name))
#         return self.inst[self.i]

#     @property
#     def c(self):
#         # print('Returning {} th version of {} '.format(self.i, self.var_name))
#         return self.inst[self.i]

#     @property
#     def nn(self):
#         self._create_next(self.i + 1)
#         return self.inst[self.i + 1]

#     def inc(self):
#         self.i += 1
#         self._create_next(self.i)


#     @property
#     def v(self):
#         return self.inst

#     def _create_next(self, iter):
#         self.inst.append(self.creator(iter=iter))

#     def get(self, index):
#         return self.inst[index]
    

def BitVecVector(prefix, sz, N, iter=0):
    """Create a vector with N Bit-Vectors of size sz"""
    return [ BitVec('%s[%s]__%s' % (prefix, i, iter), sz) for i in range(N) ]


def get_BitInt_SSA(varname, numbits):
    return Function(varname, BitVecSort(numbits), BitVecSort(numbits))

def get_ArrOfArrOfBitVec(varname, num_bits):
    return Function(varname, BitVecSort(num_bits), BitVecSort(num_bits), BitVecSort(num_bits))

def encode_int(varname, numbits, **kwargs):
    kwargs['var_name'] = varname
    return SSA(get_BitInt_SSA(varname, numbits), **kwargs)

def encode_array(varname, numbits, **kwargs):
    kwargs['var_name'] = varname
    return SSA_Arr(get_ArrOfArrOfBitVec(varname, numbits), **kwargs)

def comp_conv_bvv(val1, relate, val2, numbits):
    """
        Conversts val1 and val2 to BitVecVal and than compares them applying the relate operator
    """
    return comp_bvv(BitVecVal(val1, numbits), relate, BitVecVal(val2, numbits))

def comp_bvv(val1, relate, val2):
    """
        Compares them applying the relate operator
    """
    return str(simplify(relate(val1, val2))) == 'True'