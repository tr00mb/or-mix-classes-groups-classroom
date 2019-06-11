from __future__ import division
from __future__ import print_function
from random import randint
from ortools.sat.python import cp_model
import csv
import glob
import os
import xlsxwriter

class ElevesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    def __init__(self, groups,rooms,all_classes, _all_eleves, num_groups, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._groups = groups
        self._rooms = rooms
        self._all_classes = all_classes
        self._all_eleves = _all_eleves
        self._num_groups=num_groups
        self._solutions = set(sols)
        self._solution_count = 0
        self.colors= {
            1: 32, # vert
            2: 36, # turquoise
            3: 31 # rouge
        }


    def on_solution_callback(self):
        self._solution_count += 1

        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            workbook = xlsxwriter.Workbook('Solution%i.xlsx' % self._solution_count)
            worksheet = workbook.add_worksheet()
            group_format = workbook.add_format({'bold': True})

            row=0
            col=0
            g_num=1

            for r in self._all_classes:
                col=self._all_classes.index(r)*4
                row=0
                print('Salle %s' % r)
                worksheet.write(row, col,"Salle %s" % r,group_format )
                for g in range(self._num_groups):
                    if self.Value(self._rooms[(r,g)]):
                        row+=1
                        print('Group %i' % g)
                        worksheet.write(row, col,"Group %i" % g_num,group_format )
                        g_num+=1
                        for e in self._all_eleves:
                            if self.Value(self._groups[(e, g)]):
                                row+=1
                                print("\033[%im%s (niv %i, %s) %s\033[0m" % (self.colors.get(e[2]),e[0],e[2],self._all_classes[e[1]].replace('classe',''),e[3]))
                                worksheet.write(row, col,e[0])
                                worksheet.write(row, col +1,e[2])
                                worksheet.write(row, col +2,self._all_classes[e[1]].replace('classe',''))
                                worksheet.write(row, col +3,e[3])


            print()
            format1 = workbook.add_format({'font_color': 'green'})
            format2 = workbook.add_format({'font_color': 'blue'})
            format3 = workbook.add_format({'font_color': 'red'})

            worksheet.conditional_format('A1:D50', {'type':     'formula',
                                       'criteria': '=$B1=3',
                                       'format':   format3})
            worksheet.conditional_format('A1:D50', {'type':     'formula',
                                       'criteria': '=$B1=2',
                                       'format':   format2})
            worksheet.conditional_format('A1:D50', {'type':     'formula',
                                       'criteria': '=$B1=1',
                                       'format':   format1})

            worksheet.conditional_format('E1:H50', {'type':     'formula',
                                       'criteria': '=$F1=3',
                                       'format':   format3})
            worksheet.conditional_format('E1:H50', {'type':     'formula',
                                       'criteria': '=$F1=2',
                                       'format':   format2})
            worksheet.conditional_format('E1:H50', {'type':     'formula',
                                       'criteria': '=$F1=1',
                                       'format':   format1})

            worksheet.conditional_format('I1:L50', {'type':     'formula',
                                       'criteria': '=$J1=3',
                                       'format':   format3})
            worksheet.conditional_format('I1:L50', {'type':     'formula',
                                       'criteria': '=$J1=2',
                                       'format':   format2})
            worksheet.conditional_format('I1:L50', {'type':     'formula',
                                       'criteria': '=$J1=1',
                                       'format':   format1})

            worksheet.conditional_format('M1:P50', {'type':     'formula',
                                       'criteria': '=$N1=3',
                                       'format':   format3})
            worksheet.conditional_format('M1:P50', {'type':     'formula',
                                       'criteria': '=$N1=2',
                                       'format':   format2})
            worksheet.conditional_format('M1:P50', {'type':     'formula',
                                       'criteria': '=$N1=1',
                                       'format':   format1})

            worksheet.conditional_format('Q1:T50', {'type':     'formula',
                                       'criteria': '=$R1=3',
                                       'format':   format3})
            worksheet.conditional_format('Q1:T50', {'type':     'formula',
                                       'criteria': '=$R1=2',
                                       'format':   format2})
            worksheet.conditional_format('Q1:T50', {'type':     'formula',
                                       'criteria': '=$R1=1',
                                       'format':   format1})

            worksheet.conditional_format('U1:X50', {'type':     'formula',
                                       'criteria': '=$V1=3',
                                       'format':   format3})
            worksheet.conditional_format('U1:X50', {'type':     'formula',
                                       'criteria': '=$V1=2',
                                       'format':   format2})
            worksheet.conditional_format('U1:X50', {'type':     'formula',
                                       'criteria': '=$V1=1',
                                       'format':   format1})

            workbook.close()

    def solution_count(self):
        return self._solution_count




def main():
    # Lets have different classes (CM1A, CM1B, CM2A, CM2B et..)
    # Each class has its classtrooms and some pupils. The grade of the class is part of its name (1 for CM1A and 2 for CM2A)
    # Eleves are pupils. They have skill level (1 is the best).
    # The problem is to recompose the pupils in groups very mixed: in one group, not the same class, not the same levels
    # Then each group will seat in one classroom


    # Data.
    # num eleves per group is not exact. If it is 3 groups will be either groups of 3 or 4 peoples (depending of num_eleves % 3)
    num_eleves_per_group = 3
# initial test data
# all_eleves=[(i*100+j,i,randint(1,3)) for j in range(randint(24,30)) for i in range(num_classes)]

    all_eleves=[]
    all_classes=[]
    classe=0
    for fname in glob.glob("*.csv"):
        file=open(fname,"r")
        #all_classes will be composed of strings such as CM2A if the source file is CM2A.csv
        all_classes.append(os.path.splitext(fname)[0])
        try:
          reader=csv.reader(file,delimiter=',')
          first_row = next(reader)
          for row in reader:
            #all_eleves is composed of tuples with ('Firstname, classe number 0,1,2..., skill level, nothing or * if the pupil is marked (which means must be in his rooms, must be under his teacher surveillance)')
            all_eleves.append((row[1],classe,int(row[2]),row[3]))
          classe+=1
        finally:
          file.close()


    num_classes = classe
    #print(len(all_eleves))
    num_groups=len(all_eleves)//num_eleves_per_group

    #print(num_groups)
    all_groups=range(num_groups)
    #print (sum(1 for e in all_eleves if e[2] == 3 ))
    #print (sum (1 for e in all_eleves if e[2] == 2 ))
    #print (sum (1 for e in all_eleves if e[2] == 1 ))

    # Creates the model.
    model = cp_model.CpModel()
    groups = {}

    for e in all_eleves:
        for g in all_groups:
            groups[(e,g)] = model.NewBoolVar('group_e%sg%i' % (e[0],g))

    for g in all_groups:
        # number of pupils per group between num_eleves_per_group and num_eleves_per_group +1
        model.Add(sum(groups[(e,g)] for e in all_eleves ) >= num_eleves_per_group)
        model.Add(sum(groups[(e,g)] for e in all_eleves ) <= num_eleves_per_group+1)
        # only one marked (*) pupil per group
        model.Add(sum(groups[(e,g)] for e in all_eleves if e[3] == '*' ) <= 1)
        # max 2 pupils of the same skill level per group
        model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 3 ) <= 2)
        model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 1 ) <= 2)
        model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 2 ) <= 2)
        # max one level 1 (skill) CM2 (latest grade) per group
        model.Add(sum(groups[(e,g)] for e in all_eleves if (e[2] == 1) and ('2' in all_classes[e[1]])) <= 1)
        # distribute grade (CM1 and CM2) among the groups (max 2 pupils of the same grade per group)
        model.Add(sum(groups[(e,g)] for e in all_eleves if ('2' in all_classes[e[1]])) <= 2)
        model.Add(sum(groups[(e,g)] for e in all_eleves if ('1' in all_classes[e[1]])) <= 2)


    #if possible only one level 3 per group
    if sum(e[2]==3 for e in all_eleves) <= num_groups:
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 3 ) <= 1)
    else:
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 3 ) >=1 )

    # if possible only one level 1 per group
    if sum(e[2]==1 for e in all_eleves) <= num_groups:
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 1 ) <= 1)
    else:
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[2] == 1 ) >=1 )

    # only one pupil per class in each group
    for c in range(num_classes):
        for g in all_groups:
            model.Add(sum(groups[(e,g)] for e in all_eleves if e[1] == c ) <= 1)

    # each pupils is in one and only one group
    for e in all_eleves:
        model.Add(sum(groups[(e,g)] for g in all_groups) == 1)

    rooms={}
    for r in all_classes:
        for g in all_groups:
            rooms[(r,g)] = model.NewBoolVar('room_r%sg%i' % (r,g))

    # each group is in one and only one room
    for g in all_groups:
        model.Add(sum(rooms[(r,g)] for r in all_classes) == 1)

    num_groups_per_room={}
    #for r in all_classes:
    #    num_groups_per_room[r]=max(8,sum(1 for e in all_eleves if e[1] == all_classes.index(r) ) // num_eleves_per_group + 1)
    #    print('%s %i' % (r,num_groups_per_room[r]))

    # number of group per classes (either a calculation or fix a number if known)
    for r in all_classes:
    #    model.Add(sum(rooms[(r,g)] for g in all_groups) <= num_groups_per_room[r])
    #    model.Add(sum(rooms[(r,g)] for g in all_groups) >= num_groups_per_room[r] - 1)
        model.Add(sum(rooms[(r,g)] for g in all_groups) == 8)

    # link the pupils, the groups and the room (groups[(e,g)] and rooms[(r,g)] <=> same_room[(e,r,g)])
    same_room={}
    for r in all_classes:
        for g in all_groups:
            for e in all_eleves:
                same_room[(e, r, g)] = model.NewBoolVar(
                    "eleve %s is in group %i in classroom %s" % (e[0], g, r))

    for e in all_eleves:
        for g in all_groups:
            for r in all_classes:
                model.AddBoolOr([groups[(e,g)].Not(),rooms[(r,g)].Not(),same_room[(e,r,g)]])
                model.AddImplication(same_room[(e,r,g)],groups[(e,g)])
                model.AddImplication(same_room[(e,r,g)],rooms[(r,g)])

    # pupils marked with a * seat in their classroom
    for r in all_classes:
        model.Add(sum(same_room[(e,r,g)] for g in all_groups
            for e in all_eleves if (e[1] != all_classes.index(r)) and (e[3] == '*')) == 0)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    solver.parameters.max_time_in_seconds = 60.0
    # Display the first five solutions.
    a_few_solutions = range(5)
    solution_printer = ElevesPartialSolutionPrinter(
        groups, rooms, all_classes, all_eleves, num_groups, a_few_solutions)
    solver.SearchForAllSolutions(model, solution_printer)

    # Statistics.
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())

if __name__ == '__main__':
    main()
