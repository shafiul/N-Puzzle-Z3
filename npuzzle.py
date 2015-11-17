#!/usr/bin/env python

from z3 import *

OPT_DEBUG = True
NUM_BITS = 5

class Npuzzle_Tester(object):
    """docstring for Npuzzle_Tester"""
    def __init__(self,n, num_run, *args, **kwargs):
        super(Npuzzle_Tester, self).__init__(*args, **kwargs)
        self.n = n # Number of cells
        self.num_run = num_run  # Number of times loop will run

        self.ds = []
        self.solver = Solver()
        self.maxval = self.n * self.n   # This is the 'empty' cell

        self._p('MaxVal: {}'.format(self.maxval))

    def _create_ds(self):
        self.ds = [[self._get_unit_ds(row, col) for col in range(self.n)] for row in range(self.n)]
        # for row in self.n:
        #     row = [1,2,3]

    def _get_unit_ds(self, r, c):
        return Function('{0}_{1}'.format(r+1, c+1), BitVecSort(NUM_BITS), BitVecSort(NUM_BITS) )

    def _initialize(self):
        self._create_ds()

    def _common_constrains_each_step(self, it):

        for r, row in enumerate(self.ds):
            for c, item in enumerate(row):

                self.solver.add(item(it) > 0)
                self.solver.add(item(it) <= self.maxval)

                # Constraints for unique item in each cell

                for x in range(self.n):
                    for y in range(self.n):

                        if x == r and y == c:
                            pass
                        else:
                            other_item = self.ds[x][y]
                            self.solver.add(item(it) != other_item(it))

                # Add Transitions

                if it == self.num_run-1:
                    self._p('[LAST LOOP] No transitions applied!')
                else:
                    self._apply_transitions(item, r, c, it)

    def _apply_transitions(self, item, r, c,  i):

        self._p('[T] Applying transitions in iteration {0}...'.format(i))

        e = self.maxval
        n_m_1 = self.n-1

        ns = []     # Neighbors

        if r > 0:
            ns.append(self.ds[r-1][c])
        if r < n_m_1:
            ns.append(self.ds[r+1][c])
        if c < n_m_1:
            ns.append(self.ds[r][c+1])
        if c > 0:
            ns.append(self.ds[r][c-1])

        # it_n = (self.ds[r-1][c], (r > 0),)  # r-1 >= 0; r >= 1
        # it_s = (self.ds[r+1][c], (r < n_m_1),)  # r+1 < n; r < n-1
        # it_e = (self.ds[r][c+1], (c < n_m_1),)  # 
        # it_w = (self.ds[r][c-1], (c > 0),)  #

        def s1():
            """
                cur: Current Element
            """
            return [And(item(i+1) == x(i), x(i+1) == e) for x in ns]
            # return And(neigh[1], item(i+1) == neigh[0](i), neigh[0](i+1) == e)


        conds = s1()

        c_empty = And((item(i) == e), Or(*conds))
        # c_empty = And((item(i) == e), Or(s1(it_n), s1(it_s), s1(it_e), s1(it_w)))


        def s2():
            return [And(n(i) == e, n(i+1) == item(i), item(i+1) == e) for n in ns]
            # return And(neigh[1], neighbor[0](i+1) == e item(i+1) == neigh[0](i), neighbor[0](i+1) == e)

        conds = s2()

        conds.append(item(i+1) == item(i))

        c_nonempty = And((item(i) != e), Or(*conds))

        self.solver.add(Or(c_empty, c_nonempty))


    def _run(self):
        self._p('[i] Starting run. N: {0}; loop: {1}'.format(self.n, self.num_run))

        for i in range(self.num_run):
            self._p('--- LOOP {0} ---'.format(i))
            self._common_constrains_each_step(i)

        self._post_run()

    def _post_run(self):
        self._p('Post Run...')
        self.result = self.solver.check()
        print(self.result)

        if self.result == sat:
            self.model = self.solver.model()
            print(self.model)
        else:
            print('Not Sat!')



    def _p(self, str):
        if OPT_DEBUG:
            print(str)



        

    def generate_tests(self):
        self._initialize()
        self._run()
        # print('{}'.format(self.ds))
        self._p('-- DONE --')
        


if __name__ == '__main__':
    
    tester = Npuzzle_Tester(3, 5)
    tester.generate_tests()