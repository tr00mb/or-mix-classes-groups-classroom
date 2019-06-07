"""Code sample that encodes the product of two Boolean variables."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.sat.python import cp_model

class PartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, groups, rooms, all_eleves, all_groups, all_rooms,sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._groups = groups
        self._rooms = rooms
        self._all_eleves = all_eleves
        self._all_groups = all_groups
        self._all_rooms = all_rooms
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        self._solution_count += 1
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for r in self._all_rooms:
                print('Room %i' % r)
                for g in self._all_groups:
                    if self.Value(self._rooms[(g, r)]):
                      print('Group %i' % g)
                      for e in self._all_eleves:
                        if self.Value(self._groups[(e, g)]):
                          print(e)
            print()

    def solution_count(self):
        return self._solution_count

def main():
  """Encoding of the product of two Boolean variables.

  p == x * y, which is the same as p <=> x and y
  """
  all_eleves=[('eleve1',0,''),('eleve2',0,''),('eleve3',1,'*'),('eleve4',1,'')]
  all_groups=range(2)
  all_rooms=range(2)

  model = cp_model.CpModel()

  groups={}
  for e in all_eleves:
    for g in all_groups:
      groups[(e,g)] = model.NewBoolVar('%s in group %i' % (e[0],g))

  rooms={}
  for g in all_groups:
    for r in all_rooms:
      rooms[(g,r)] = model.NewBoolVar('%i in room %i' % (g,r))
  
  p={}
  for g in all_groups:
    for r in all_rooms:
      for e in all_eleves:
        p[(g,r,e)] = model.NewBoolVar('p')

  for e in all_eleves:
        model.Add(sum(groups[(e,g)] for g in all_groups) == 1)

  for c in all_rooms:
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[1] == c ) <= 1)

  for g in all_groups:
    model.Add(sum(groups[(e,g)] for e in all_eleves) == 2)

  for r in all_rooms:
        model.Add(sum(rooms[(g,r)] for g in all_groups) == 1)
  
  for g in all_groups:
    model.Add(sum(rooms[(g,r)] for r in all_rooms) == 1)

  for r in all_rooms:
    for e in all_eleves:
      if e[2]=='*':
        # x and y implies p, rewrite as not(x and y) or p
        model.AddBoolOr([groups[(e,g)].Not(), rooms[(g,r)].Not(), p[(g,r,e)]])
        # p implies x and y, expanded into two implication
        model.AddImplication(p[(g,r,e)], groups[(e,g)])
        model.AddImplication(p[(g,r,e)], rooms[(g,r)])

  # Create a solver and solve.
  solver = cp_model.CpSolver()
  status = solver.Solve(model)
  solver.parameters.linearization_level = 0
    # Display the first five solutions.
  few_sols=range(5)
  solution_printer = PartialSolutionPrinter(
        groups, rooms, all_eleves, all_groups, all_rooms, few_sols)
  solver.SearchForAllSolutions(model, solution_printer)
