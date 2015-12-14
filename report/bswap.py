def swap(self, pos1, pos2, add_to_solver=True, gen_else=False):
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
            else_conds.append(self.c(i) == self.p(i)) 

    if add_to_solver:
        self.s.add(And(*conds))
    else:
        return (conds, else_conds,)