#!/usr/bin/env python
import sys
from functools import partial
from helper import *

BITS = 16
num_elements = 6

s = Solver()

# arr = Function('arr', BitVecSort(BITS), BitVecSort(BITS), BitVecSort(BITS))
arr = encode_array('arr', BITS,
    solver=s, num_elements=num_elements
)

top = encode_int('top', BITS, solver=s, init_val=-1)
topped = encode_int('topped', BITS, solver=s)
temp = SSA(Function('temp', BitVecSort(BITS), BitVecSort(BITS)), solver=s)

# s.add(top.c == 0)
# top.assign(-1, current=True)
top.plusplus()

# arr[top++] = 1;

s.add(arr.c(top.c) == 1)
top.plusplus()

# arr[top++] = 4;

arr.u(top.c, 4)                                 # arr[top] = 4;
    
top.plusplus()                                  # top++

# Encode: arr[top++] = 3;

arr.u(top.c, 3)                                 # arr[top] = 3;

top.plusplus()                                  # top++

# swap pos0 () and pos2

pos0 = temp.assign(0, current=True)
pos2 = temp.assign(2)

arr.swap(pos0, pos2)

while True:
    top.minusminus()                                # [[E]] top--
    if s.check() == sat:

        top_value = int(str(s.model().evaluate(top.c)))

        topped.assign(arr.c(top.c))                     # [[E]] topped = arr[top]

        if top_value == 0:
            print('top value == zero, breaking: {0}'.format(top_value))
            break
    else:
        print('unsat!')
        sys.exit(0)


### old ###

# # Encode: topped = arr[--top];

# top.minusminus()                                # [[E]] top--
# topped.assign(arr.c(top.c), current=True)       # [[E]] topped = arr[top];

# # Encode: topped = arr[--top];
# top.minusminus()                                # [[E]] top--
# topped.assign(arr.c(top.c))                     # [[E]] topped = arr[top]



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

    for i in range(1, topped.len):
        print('topped({0}) -> {1}'.format(i, m.evaluate(topped.v(i))))

    print('--- top: {0} ---'.format(m.evaluate(top.c)))
else:
    print('Unsat Core: {}'.format(s.unsat_core()))

print 'DONE'


sys.exit(0)