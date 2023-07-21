'''
Impedance Match Script
Version: 1.0.0
MIT Electric Vehicle Team
Adi Mehrotra, Miguel Talamantez

DEPENDENCIES:
Numpy (np)

NOTE:
The following script takes an arbitrary battery back of (n) series and (m) parallel cells,
and a list of (q) cell resistances, and returns the cell configuration that results in adequate
parallel resistance matching.
'''

#note that you must install NUMPY
import numpy as np

#parameters
verbose = False

#INPUTS—ASSUMES n*m <= q
n = 12 #enter the number of series cells
m = 2 #enter the number of parallel cells 
q = 36 #enter the total number of cells measured

#a 1xq dictionary of resistances cell label: cell resistance
r = {1: 12.96,
    2: 22.84,
    3: 11.79,
    4: 10.15,
    5: 11.69,
    6: 10.18,
    7: 12.45,
    8: 8.44,
    9: 9.18,
    10: 17.82,
    11: 11.44,
    12: 9.20,
    13: 3.94,
    14: 7.47,
    15: 15.71,
    16: 17.08,
    17: 16.74,
    18: 6.14,
    19: 12.54,
    20: 21.41,
    21: 2.80,
    22: 3.50,
    23: 12.50,
    24: 17.14,
    25: 5.04,
    26: 2.94,
    27: 10.77,
    28: 13.78,
    29: 2.10,
    30: 4.54,
    31: 14.21,
    32: 4.30,
    33: 3.17,
    34: 3.10,
    35: 3.17,
    36: 3.84}





#FUNCTIONS
'''
test_incompatibility(group1, group2)

RETURNS TRUE IF GROUPS ARE COMPATIBLE

Tests two cell groups for shared cells and returns true if no cells are shared between the groups.
NOTE: an incompatable set of cell groups are cell groups which share a cell number (a cell is used more than once)    

source: https://stackoverflow.com/questions/3170055/test-if-lists-share-any-items-in-python
'''
def test_incompatibility(group1, group2):
    return set(group1).isdisjoint(group2)

'''
print_solution(final_solution) - prints the solution so it's easy to view in terminal
'''
def print_solution(final_solution):
    print("-----Final Cell Groups-----")
    for cell_groups in final_solution:
        print("Cells in Group: " + str(cell_groups))

'''
group_resistance(group) - calcualtes the parallel resistance of a group of cells (for any number of cells)
'''
def group_resistance(group, resistances):
    #build up the resistances to combine in parallel
    cell_rs = []
    n = len(group)
    for cell in group:
        cell_rs.append(resistances[cell])
    inverted_rs = [1.0/x for x in cell_rs]
    return 1.0/sum(inverted_rs)





#MAIN LOOP BEGINS HERE
sorted_r = sorted(r.items(), key=lambda x:x[1]) #outputs a list of tuples (cell #, resistance) sorted in ascending order

#now optimize resistances
r_optimized = []
final_cell_groups = []

#if you have exactly the number of cells required, there is one unique solution
if (m==1):
    print("\n\nSingle solution possible... generating")
    if verbose: print(sorted_r)
    r_optimized = sorted_r[:n]
    final_cell_groups = [[x[0]] for x in r_optimized]
elif (n*m == q):
    print("\n\nSingle solution possible... generating")
    #create the cell groupings
    if verbose: print(sorted_r)
    for i in range(0,q,m):
        cell_numbers = []
        number_resistance_pairs = sorted_r[i:i+m]
        for resistance_number_pair in number_resistance_pairs:
            cell_numbers.append(resistance_number_pair[0])
        r_optimized.append(cell_numbers)
    #create the cell groupings
    final_cell_groups = r_optimized
else:
    print("\n\nMultiple solutions possible... generating groups")
    #else we use an algorithm to optimize the resistances as best we can
    cell_groups_stdev = []
    #calculate all possible cell groups and the standard deviation of their resistances
    for i in range(q-m+1):
        start_index, end_index = i, i+m
        number_resistance_group = sorted_r[start_index: end_index]
        cells_in_group = [x[0] for x in number_resistance_group]
        resistances_in_group = [x[1] for x in number_resistance_group]
        st_dev = np.std(resistances_in_group)
        cell_groups_stdev.append([cells_in_group, st_dev])
    #sort the groups
    print("sorting groups...")
    sorted_groups = sorted(cell_groups_stdev, key=lambda x:x[1])
    #now attempt to minimize overall pack deviation by using the lowest deviations in the sorted groups
    #NOTE: WE KNOW THIS METHOD IS NOT STRICTLY OPTIMAL, AND HOPE TO UPDATE IT LATER
    r_optimized.append(sorted_groups[0])
    print("iterating through groups to find a solution...")
    for i in range(1,q):
        group = sorted_groups[i]
        if verbose: print("\n\nchecking cell group: " + str(group))
        #check compatibility against ALL groups
        broken = False
        for cell_group in r_optimized:
            if verbose: print("checking against group: " + str(cell_group))
            if not test_incompatibility(group[0], cell_group[0]):
                if verbose: print(str(group) + " is an incompatible group, moving to next group...")
                broken = True
                break
        #if ALL groups are compatible
        if not broken:
            if verbose: print(str(group) + " is COMAPTIBLE... adding to list!")
            r_optimized.append(group)
        #terminate when we reach the correct number of series cells
        if len(r_optimized)==n:
            break
    #create the cell groupings
    final_cell_groups = [x[0] for x in r_optimized]





#print the final values
print("\n\nSolution found! Printing...]\n")

#print the final cell pairs
print_solution(final_cell_groups)

#calculate the final pack resistance
total_resistance = 0.0
cell_group_resistances = []
for cell_group in final_cell_groups:
    total_resistance += group_resistance(cell_group, r)
    cell_group_resistances.append([cell_group, total_resistance])

print("\n\n-----Pack Specifications-----")
print("Total Calculated Pack Resistance: " + str(total_resistance))
print("\nResistances by Group: " + str(cell_group_resistances))
print("\n\n")