#!/usr/bin/env python

from z3 import *

OPT_DEBUG = True
NUM_BITS = 5

class Npuzzle_Tester(object):
    """docstring for Npuzzle_Tester"""
    def __init__(self,n, *args, **kwargs):
        super(Npuzzle_Tester, self).__init__(*args, **kwargs)
        self.n = n # Number of cells

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

                for x in range(self.n):
                    for y in range(self.n):

                        if x == r and y == c:
                            pass
                        else:
                            other_item = self.ds[x][y]
                            self.solver.add(item(it) != other_item(it))


    def _run(self):
        self._p('Running...')
        self._common_constrains_each_step(0)

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
    
    tester = Npuzzle_Tester(3)
    tester.generate_tests()