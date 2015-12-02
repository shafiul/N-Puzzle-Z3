#!/usr/bin/env python
import operator
from helper import *

NUMBITS = 16
NEGATIVE_ONE = int(str(BitVecVal(-1, NUMBITS)))
ZERO_BITVECVAL = BitVecVal(0, NUMBITS)

DEBUG = True


def quicksort_sa(data):

    stack_capacity = len(data)

    s = Solver()

    arr = encode_array('arr', NUMBITS, solver=s, num_elements=stack_capacity, init_val=data)      # [e] arr

    h = encode_int('h', NUMBITS, solver=s, init_val=(len(data) - 1))           # [e] h = len(data) - 1

    l = encode_int('l', NUMBITS, solver=s, init_val=0)                         # [e] l = 0

    stack = encode_array('stack', NUMBITS, solver=s, num_elements=stack_capacity)      # [e] stack

    top = encode_int('top', NUMBITS, solver=s, init_val=-1)                     # [e] top = -1
    x = encode_int('x', NUMBITS, solver=s)                                      # [e] int x;
    p = encode_int('p', NUMBITS, solver=s)                                      # [e] int p;
    jj = encode_int('j', NUMBITS, solver=s)                                     # [e] int j;

    # [e] // push initial values of l and h to stack
    # [e] stack[ ++top ] = l;
    # [e] stack[ ++top ] = h;

    top.plusplus()
    stack.u(top.c, l.c)                                                         # [e] stack[ top ] = l;  

    top.plusplus()
    stack.u(top.c, h.c)                                                         # [e] stack[ top ] = h;  

    # // Keep popping from stack while is not empty
    # while ( top >= 0 )

    ow = 1

    while True:

        print('[WHILE {0}]'.format(ow))
        ow += 1

        if s.check() == unsat:
            print('[FATAL] unsat in the outer while loop.')
            return

        val_of_top = int(str(s.model().evaluate(top.c)))
        print('val of top: {}'.format(val_of_top))

        # comp_result = simplify(BitVecVal(val_of_top, NUMBITS) < ZERO_BITVECVAL)

        if comp_bvv(BitVecVal(val_of_top, NUMBITS), operator.lt, ZERO_BITVECVAL):
            print('Breaking since stack top is < 0') 
            break

        # [back to encoding]
        # [e] // Pop h and l
        # [e] h = stack[ top-- ];
        # [e] l = stack[ top-- ];

        h.assign(stack.c(top.c))                                                # [e] h = stack[ top ];
        top.minusminus()

        l.assign(stack.c(top.c))                                                # [e] l = stack[ top ];
        top.minusminus()


        # [e]  // Set pivot element at its correct position in sorted array
        # [e]  // int p = partition( arr, l, h );
        # [e]  x = arr[h];
        # [e]  p = (l - 1);

        x.assign(arr.c(h.c), current=False)                                      # [e]  x = arr[h];
        p.assign((l.c - 1), current=False)                                       # [e]  p = (l - 1);


        # [e]   for (int j = l; j <= h- 1; j++)
        # [e]   {
        # [e]       if (arr[j] <= x)
        # [e]      {
        # [e]          p++;
        # [e]           swap (&arr[p], &arr[j]);
        # [e]       }
        # [e]   }


        jj.assign(l.c, current=False)

        wc = 1

        while True:

            if s.check() == unsat:
                print('[FATAL] unsat in the inner while loop. Encoding failed.')

                print('unsat core: {}'.format(s.unsat_core()))
                print('encoding: \n{0}'.format(s))
                return

            if DEBUG:
                e = s.model().evaluate
                print('[FOR {0}] top: {1}; h: {2}; l:{3}; x: {4}; p: {5}; j: {6}'.format(
                    wc, e(top.c), e(h.c), e(l.c), e(x.c), e(p.c), e(jj.c)))
                print('          array: [{}, {}, {}]'.format(  e(arr.c(0)), e(arr.c(1)), e(arr.c(2))  ))

            wc += 1


            val_of_j = int(str(s.model().evaluate(jj.c)))
            val_of_h_minus_1 = int(str(s.model().evaluate(h.c - 1)))

            if comp_conv_bvv(val_of_j, operator.gt, val_of_h_minus_1, NUMBITS):
                print('[FOR-break] j is > h-1; v: {}, h-1: {}'.format(val_of_j, val_of_h_minus_1))
                break

            print('[FOR-normal] j is <= h-1; v: {}, h-1: {}'.format(val_of_j, val_of_h_minus_1))

            # s.add(Implies(
            #     (arr.c(jj.c) <= x.c),
            #     And(
            #         p.plusplus(add_to_solver=False),
            #         arr.swap(p.c, jj.c, add_to_solver=False)
            #     )
            # ))

            if_then_condition = (arr.c(jj.c) <= x.c)
            if_else_condition = (arr.c(jj.c) > x.c)

            p_plus_plus = p.plusplus(add_to_solver=False, gen_else=True)
            arr_swap = arr.swap(p.c, jj.c, add_to_solver=False, gen_else=True)

            if val_of_j == 1:
                print('<<>> B4 Implies, model: \n{0}\n<<<<<<<>>>>>>>>'.format(s))

            s.add(Or(
                And(
                    if_then_condition, p_plus_plus[0], *arr_swap[0]
                ),
                And(
                    if_else_condition, p_plus_plus[1], *arr_swap[1]
                )
            ))

            # [e] j++
            jj.plusplus()                                                      # [e] j++

            ## end of inner while loop encoding (the for loop from the C code) ##

        print('[w] Exited inner while.')


        # [e]  p = (p + 1);
        # [e]  swap (&arr[p], &arr[h]);

        if DEBUG:
            s.check()
            e = s.model().evaluate

            print('>> arr b4 SWAP << : [{}, {}, {}]'.format(e(arr.c(0)), e(arr.c(1)), e(arr.c(2)) ))
            print('>><< x: {}, h: {}'.format(e(x.c), e(h.c)))

        p.plusplus()                                                          # [e]  p = (p + 1);
        arr.swap(p.c, h.c)                                                    # [e]  swap (&arr[p], &arr[h]);

        if DEBUG:
            s.check()
            e = s.model().evaluate

            print('>> arr after SWAP << : [{}, {}, {}]'.format(e(arr.c(0)), e(arr.c(1)), e(arr.c(2)) ))
            print('>><< x: {}, h: {}'.format(e(x.c), e(h.c)))


        # [e] // If there are elements on left side of pivot, then push left
        # [e] // side to stack
        # [e] if ( p-1 > l )
        # [e] {
        # [e]     stack[ ++top ] = l;
        # [e]     stack[ ++top ] = p - 1;
        # [e] }

        # s.add(Implies(
        #     ((p.c - 1) > l.c),
        #     And(
        #         top.plusplus(add_to_solver=False),
        #         stack.u(add_to_solver=False)
        #     )
        # ))

        top_plus_plus = top.plusplus(add_to_solver=False, gen_else=True)
        stack_u = stack.u(top.c, l.c, add_to_solver=False, gen_else=True)

        top_plus_plus_2 = top.plusplus(add_to_solver=False, gen_else=True)
        stack_u_2 = stack.u(top.c, (p.c - 1), add_to_solver=False, gen_else=True)

        stack_u[0].extend(stack_u_2[0])
        stack_u[1].extend(stack_u_2[1])


        s.add(Or(
            And(
                ((p.c - 1) > l.c), top_plus_plus[0], top_plus_plus_2[0], *stack_u[0]
            ),
            And(
                ((p.c - 1) <= l.c), top_plus_plus[1], top_plus_plus_2[1], *stack_u[1]
            )            
        ))

        # [e]  // If there are elements on right side of pivot, then push right
        # [e]  // side to stack
        # [e]  if ( p+1 < h )
        # [e]  {
        # [e]      stack[ ++top ] = p + 1;
        # [e]      stack[ ++top ] = h;
        # [e]  }


        top_plus_plus = top.plusplus(add_to_solver=False, gen_else=True)
        stack_u = stack.u(top.c, (p.c + 1), add_to_solver=False, gen_else=True)

        top_plus_plus_2 = top.plusplus(add_to_solver=False, gen_else=True)
        stack_u_2 = stack.u(top.c, h.c, add_to_solver=False, gen_else=True)

        stack_u[0].extend(stack_u_2[0])
        stack_u[1].extend(stack_u_2[1])

        s.add(Or(
            And(
                ((p.c + 1) < h.c), top_plus_plus[0], top_plus_plus_2[0], *stack_u[0]
            ),
            And(
                ((p.c + 1) >= h.c), top_plus_plus[1], top_plus_plus_2[1], *stack_u[1]
            )            
        ))



        # [END OF OUTER WHILE] Add the breaking condition at val_of_top == 0
        if val_of_top is 0:
            print('Stack top reached zero; breaking from the outer loop...')
            break




    ####################### Check SAT #######################

    print('Encoding: \n {}'.format(s))

    print('--------- Result: {} ---------'.format(s.check()))

    if s.check() == sat:
        m = s.model()
        print ('    Model: \n{}'.format(m))

        print('--- stack dump, stack len: {} ---'.format(stack.len))

        for i in range(stack.len):
            print('------------- stack @ {} -------------'.format(i))
            for j in range(stack_capacity):
                print('stack[{0}] -> {1}'.format(j, m.evaluate(stack.v(i, j))))

        print('--- arr dump, arr len: {} ---'.format(arr.len))

        for i in range(arr.len):
            print('------------- arr @ {} -------------'.format(i))
            for j in range(stack_capacity):
                print('arr[{0}] -> {1}'.format(j, m.evaluate(arr.v(i, j))))

        # print('--- topped dump ---')

        # for i in range(1, topped.len):
        #     print('topped({0}) -> {1}'.format(i, m.evaluate(topped.v(i))))

        print('--- top: {0} ---'.format(m.evaluate(top.c)))
    else:
        print('Unsat Core: {}'.format(s.unsat_core()))



if __name__ == '__main__':
    # quicksort_sa((3, 0))
    # quicksort_sa((2, 4, 3, 5))
    quicksort_sa((2, 0, 3, -1))
    # quicksort_sa((4, 2, 3))
    # quicksort_sa((4, 3, 5, 2, 1, 3, 2, 3))
    print('--- DONE ---')
