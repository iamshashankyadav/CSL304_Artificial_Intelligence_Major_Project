from 

def main():
    grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    # Example usage
    csp = SudokuCSP(grid)
    print("Initial domains for (0,2):", csp.domains[(0, 2)])

    # Solve with full features
    solved = csp.solve(
        forward_checking=True, heuristic_var="mrv", heuristic_val="lcv", use_ac3=True
    )
    if solved:
        print("Solved grid:")
        for row in csp.grid:
            print(row)
    else:
        print("No solution")