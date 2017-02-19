###########################################################
# Globlas
###########################################################
# Define rows and columns
rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

###########################################################
# Functions
###########################################################
def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Boxes with only two digits
    box2digits = [b for b in boxes if len(values[b]) == 2]
    # Find all instances of naked twins
    candidates = [(c, p) for c in box2digits for p in box2digits if (p in peers[c]) and (values[c] == values[p])]
    # Remove permutations from candidates list, example: above list has ('H4', 'H6') and ('H6', 'H4'),
    # so, remove the second, since it's a permutation of the first.
    naked_twins = sorted(list(set([ (min(x), max(x)) for x in candidates ])))
    # Eliminate the naked twins as possibilities for their peers
    for (a, b) in naked_twins:
        # Get common peers for each pair of naked_twins
        common_peers = sorted([c for c in peers[a] if c in peers[b]])
        # for each digit in naked_twins, scan common_peers and remove it if it appears
        for digit in values[a]:
            for peer in common_peers:
                if digit in values[peer]:
                    values[peer] = values[peer].replace(digit, "")

    return values

def cross(A, B):
    """
    Cross('abc', 'def') will return ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']
    """
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    first = dict(zip(boxes, grid))
    sec = {'.': '123456789'}

    return {k: sec.get(v, v) for k, v in first.items()}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF':
            print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    """
    
    # Using Udacity's version...it seems more elegant.
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    digits = '123456789'
    for unit in unitlist:
        for digit in digits:
            # Get the boxes where a given digit appears on the unit
            digitPlaces = [box for box in unit if digit in values[box]]
            if len(digitPlaces) == 1:
                values = assign_value(values, digitPlaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        # What if we insert naked_twins here... would improve solver speed? Comment line below and test it. ;)
        values = naked_twins(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    """
    values = reduce_puzzle(values)
    if values == False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    a, b = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for v in values[b]:
        n_sudoku = values.copy()
        n_sudoku[b] = v
        n_solution = search(n_sudoku)
        if n_solution:
            return n_solution

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert to Dictionary
    values = grid_values(grid)
    # Doubt: What if search returns False, can display() handle it?
    return search(values)

###########################################################
# Problem Representation
###########################################################
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# To be able to solve a diagonal sudoku we have to update the units...
# First, build the diagonals: 
# d1 = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'] and d2 = ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']
diagonals = [[a+b, a+c] for a, b, c in zip(('ABCDEFGHI'), ('123456789'), ('987654321'))]
d1, d2 = [item[0] for item in diagonals] , [item[1] for item in diagonals]
# Now, for each box into diagonals, go to units[box] and append diagonal
for d in (d1, d2):
    for b in d:
        units[b].append(d)

# Now we can build peers for each box
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

###########################################################
# Run Script
###########################################################
if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
