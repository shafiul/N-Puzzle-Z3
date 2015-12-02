#!/usr/bin/env python
import sys
from functools import partial
from helper import *

BITS = 16
num_elements = 6

s = Solver()

# arr = Function('arr', BitVecSort(BITS), BitVecSort(BITS), BitVecSort(BITS))
arr = SSA_Arr(
    Function('arr', BitVecSort(BITS), BitVecSort(BITS), BitVecSort(BITS)),
    solver=s, num_elements=num_elements
)

top = SSA(Function('top', BitVecSort(BITS), BitVecSort(BITS)), solver=s)
topped = SSA(Function('topped', BitVecSort(BITS), BitVecSort(BITS)), solver=s)

# s.add(top.c == 0)
top.assign(0, current=True)

# arr[top++] = 1;

# s.add(arr(c, top.c) == 1)
s.add(arr.c(top.c) == 1)
top.plusplus()

# arr[top++] = 4;

# arr.inc()

# for i in range(num_elements):

#     s.add(Or(
#         And(top.c == i, arr.c(i) == 4),
#         And(top.c != i, arr.c(i) == arr.p(i))
#     ))

arr.u(top.c, 4)
    
top.plusplus() # top++

# Encode: arr[top++] = 3;

# arr.inc()

# for i in range(num_elements):
#     s.add(Or(
#         And(top.c == i, arr.c(i) == 3),
#         And(top.c != i, arr.c(i) == arr.p(i))
#     ))

arr.u(top.c, 3)

top.plusplus() # top++

# Encode: topped = arr[--top];

top.minusminus() # [[E]] top--
# s.add(topped.c == arr.c(top.c)) # [[E]] topped = arr[top]
topped.assign(arr.c(top.c), current=True)

# Encode: topped = arr[--top];
top.minusminus() # [[E]] top--
# s.add(topped.n == arr.c(top.c)) # [[E]] topped = arr[top]
topped.assign(arr.c(top.c)) # [[E]] topped = arr[top]



####################### Check SAT #######################

print('Encoding: \n {}'.format(s))

print('--------- Result: {} ---------'.format(s.check()))

if s.check() == sat:
    m = s.model()
    print ('    Model: \n{}'.format(m))

    print('--- arr dump, arr len: {} ---'.format(arr.len))

    for i in range(arr.len):
        print('------------- {} -------------'.format(i))
        for j in range(num_elements):
            print('arr[{0}] -> {1}'.format(j, m.evaluate(arr.v(i, j))))

    print('--- topped dump ---')

    for i in range(topped.len):
        print('topped({0}) -> {1}'.format(i, m.evaluate(topped.v(i))))

    print('--- top: {0} ---'.format(m.evaluate(top.c)))
else:
    print('Unsat Core: {}'.format(s.unsat_core()))

print 'DONE'


sys.exit(0)