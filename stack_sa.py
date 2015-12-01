#!/usr/bin/env python
import sys
from functools import partial
# from z3 import *
from helper import *

BITS = 16
num_elements = 6

s = Solver()

arr = Function('arr', BitVecSort(BITS), BitVecSort(BITS), BitVecSort(BITS))
c = 0

top = SSA(Function('top', BitVecSort(BITS), BitVecSort(BITS)))
topped = SSA(Function('topped', BitVecSort(BITS), BitVecSort(BITS)))
x = SSA(Function('x', BitVecSort(BITS), BitVecSort(BITS)))

s.add(top.c == 0)

# arr[top++] = 1;

s.add(arr(c, top.c) == 1)
s.add((1 + top.c) == top.n)

# arr[top++] = 4;

p = c
c += 1

for i in range(num_elements):

    s.add(Or(
        And(top.c == i, arr(c, i) == 4),
        And(top.c != i, arr(c, i) == arr(p, i))
    ))
    
s.add((1 + top.c) == top.n) # top++

# Encode: arr[top++] = 3;

p = c
c += 1

for i in range(num_elements):
    s.add(Or(
        And(top.c == i, arr(c, i) == 3),
        And(top.c != i, arr(c, i) == arr(p, i))
    ))

s.add((1 + top.c) == top.n) # top++

# Encode: topped = arr[--top];

s.add((top.c - 1) == top.n) # [[E]] top--
# s.add((top.c - 1) == top.n) # [[E]] top--
s.add(topped.c == arr(c, top.c)) # [[E]] topped = arr[top]

# Encode: topped = arr[--top];
s.add((top.c - 1) == top.n) # [[E]] top--
s.add(topped.n == arr(c, top.c)) # [[E]] topped = arr[top]



####################### Check SAT #######################

print('Encoding: \n {}'.format(s))

print('--------- Result: {} ---------'.format(s.check()))

if s.check() == sat:
    m = s.model()
    print ('    Model: \n{}'.format(m))

    print('--- arr dump, c: {} ---'.format(c))

    for i in range(c + 1):
        print('------------- {} -------------'.format(i))
        for j in range(num_elements):
            print('arr[{0}] -> {1}'.format(j, m.evaluate(arr(i, j))))

    print('--- topped dump ---')

    for i in range(topped.len):
        print('topped({0}) -> {1}'.format(i, m.evaluate(topped.v(i))))

    print('--- top: {0} ---'.format(m.evaluate(top.c)))
else:
    print('Unsat Core: {}'.format(s.unsat_core()))

print 'DONE'


sys.exit(0)