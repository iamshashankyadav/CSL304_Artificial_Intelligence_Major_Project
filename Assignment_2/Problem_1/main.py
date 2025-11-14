from Problem_1.solution import SudokuCSPSolver


def main():
    puzzle = [
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

    algorithms = [
        "backtracking",
        "forward_checking",
        "mrv",
        "mrv_degree",
        "full_heuristics",
        "ac3",
    ]

    print("=" * 60)
    print("SUDOKU CSP SOLVER - COMPARING ALGORITHMS")
    print("=" * 60)

    print("\nInitial Puzzle:")
    solver = SudokuCSPSolver(puzzle)
    solver.print_grid()

    print("\n" + "=" * 60)
    print("SOLVING WITH DIFFERENT ALGORITHMS")
    print("=" * 60)

    results = []

    for algo in algorithms:
        print(f"\n{'=' * 60}")
        print(f"Algorithm: {algo.upper().replace('_', ' ')}")
        print("=" * 60)

        solver = SudokuCSPSolver(puzzle)
        success, time_taken = solver.solve(algo)

        if success:
            print("\n✓ Solution found!")
            solver.print_grid()
            solver.print_stats()
            print(f"  Time taken: {time_taken:.4f} seconds")

            results.append(
                {
                    "algorithm": algo,
                    "nodes": solver.nodes_explored,
                    "backtracks": solver.backtracks,
                    "time": time_taken,
                }
            )
        else:
            print("\n✗ No solution found!")

    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"{'Algorithm':<20} {'Nodes':<12} {'Backtracks':<12} {'Time (s)':<10}")
    print("-" * 60)

    for result in results:
        print(
            f"{result['algorithm']:<20} {result['nodes']:<12} "
            f"{result['backtracks']:<12} {result['time']:<10.4f}"
        )

    print("=" * 60)
