#!/usr/bin/env python
from z3 import *


def sa_lottery(num_bits):
    """
        This solution goes through all the 2^3 paths and checks for answer.
    """

    length = 4
    prize = 0

    param_num_bits = 3  # Number of bits for a,b,c vars below

    a = BitVec('a', param_num_bits)
    b = BitVec('b', param_num_bits)
    c = BitVec('c', param_num_bits)

    p = Function('position', BitVecSort(num_bits), BitVecSort(num_bits))    # Position Variable

    s = Solver()

    s.add(a > -1, a < 2)  # {0, 1}
    s.add(b > -1, b < 2)  # {0, 1}
    s.add(c > -1, c < 2)  # {0, 1}

    s.add(p(0) == 0)    #  position=0;

    s.add(Or(
        And(a == 1, p(1) == ((p(0) + length - 2)% length)),
        And(a == 0, p(1) == ((p(0) + 1)% length))
        ))

    s.add(Or(
            And(b == 1, p(2) == ((p(1) + 1)% length)),
            And(b == 0, p(2) == ((p(1) + length - 2)% length))
            ))

    s.add(Or(
            And(c == 1, p(3) == ((p(2) + length - 2)% length)),
            And(c == 0, p(3) == ((p(2) + 1)% length))
            ))


    s.add(p(3) == prize)

    # Sat Check

    while True:

        if s.check() == sat:
            m = s.model()
            print('sat: a,b,c = {},{},{}'.format(m.evaluate(a), m.evaluate(b), m.evaluate(c)))
            s.add(Or(
                    a != m.evaluate(a), b != m.evaluate(b), c != m.evaluate(c)
                ))
        else:
            print('UNSAT: no more models found.')
            break


    

def sa_lottery_individual_encoding(num_bits):
    """
        This was my first attempt to encode only two paths, as asked in the question.
    """

    length = 4
    prize = 2

    param_num_bits = 3  # Number of bits for a,b,c vars below

    a = BitVec('a', param_num_bits)
    b = BitVec('b', param_num_bits)
    c = BitVec('c', param_num_bits)

    p = Function('position', BitVecSort(num_bits), BitVecSort(num_bits))    # Position Variable

    s = Solver()

    s.add(p(0) == 0)    #  position=0;

    # Path: Then, Else, Then

    s.push()

    # s.add(a == BitVecVal(1, param_num_bits))
    s.add(a == 1)
    s.add(p(1) == ((p(0) + length - 2)% length))

    s.add(b == 0)
    s.add(p(2) == ((p(1) + length - 2)% length))

    s.add(c == 1)
    s.add(p(3) == ((p(2) + length - 2)% length))

    s.add(p(3) == prize)

    if s.check() == sat:
        m = s.model()
        print('Sat in 1st Path. a,b,c = {},{},{}'.format(m.evaluate(a), m.evaluate(b), m.evaluate(c)))
    else:
        print('Unsat in first path')

    s.pop()

    # Path: Else, Then, Else

    s.push()

    s.add(a == 0)
    s.add(p(1) == ((p(0) + 1)% length))

    s.add(b == 1)
    s.add(p(2) == ((p(1) + 1)% length))

    s.add(c == 0)
    s.add(p(3) == ((p(2) + 1)% length))


    s.add(p(3) == prize)

    if s.check() == sat:
        m = s.model()
        print('Sat in 2nd Path. a,b,c = {},{},{}'.format(m.evaluate(a), m.evaluate(b), m.evaluate(c)))
    else:
        print('Unsat in second path')

    s.pop()


if __name__ == '__main__':
    sa_lottery(8)