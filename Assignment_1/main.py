from Problem_1.taxi_routing import TaxiRouting
from Problem_2.reservoir import Reservoir
from Problem_3.tic_tac_toe import TicTacToe
from Problem_4.chip_replacement import ChipPlacement, ChipVisualizationTool
import math


def main():
    # Problem 1 Example
    NUM_NODES = 8
    EDGES = [
        (1, 2, 30),
        (2, 3, 50),
        (2, 4, 60),
        (3, 5, 40),
        (4, 6, 70),
        (5, 7, 20),
        (6, 7, 30),
        (7, 8, 50),
        (3, 6, 90),
    ]
    TRIPS = [(2, 7), (1, 8), (3, 4)]
    WAIT_PENALTY, SPEED_KMH = 30.0, 40.0
    tr = TaxiRouting(NUM_NODES, EDGES, TRIPS, WAIT_PENALTY, SPEED_KMH)
    tr.run_taxi_routing(NUM_NODES, EDGES, TRIPS, WAIT_PENALTY, SPEED_KMH)

    # Problem 2 Example
    try:
        print("Enter capacities (C1 C2 C3):")
        cap_line = input().strip()
        print("Enter initial amounts (I1 I2 I3):")
        init_line = input().strip()
        print("Enter target amounts (T1 T2 T3):")
        target_line = input().strip()
    except Exception:
        print("Failed to read input. Using example input.")
        cap_line, init_line, target_line = "8.0 5.0 3.0", "8.0 0.0 0.0", "2.4 5.0 0.6"
    solver = Reservoir()
    capacities = solver.parse_line_of_numbers(cap_line)
    initial = tuple(solver.parse_line_of_numbers(init_line))
    target = tuple(solver.parse_line_of_numbers(target_line))
    if len(capacities) != 3 or len(initial) != 3 or len(target) != 3:
        raise ValueError("Each line must contain exactly 3 numbers.")
    if sum(initial) != sum(target):
        raise ValueError("Total water not conserved.")
    solver.run_all_methods(capacities, initial, target)

    # Problem 3 Example


# Test both the versions
solver_3 = TicTacToe()
board = [
    [solver_3.E, solver_3.X, solver_3.E],
    [solver_3.O, solver_3.E, solver_3.E],
    [solver_3.X, solver_3.E, solver_3.O],
]
print("Initial Board:")
solver_3.print_board(board)
score_plain, move_plain = solver_3.minimax_plain(board, depth=9, maximizing=True)
print("Plain Minimax -> Best Move:", move_plain, "Score:", score_plain)
score_ab, move_ab = solver_3.minimax_ab(
    board, depth=9, alpha=-math.inf, beta=math.inf, maximizing=True
)
print("Alpha-Beta -> Best Move:", move_ab, "Score:", score_ab)
if move_ab:
    board[move_ab[0]][move_ab[1]] = solver_3.X
    print("Board After Alpha-Beta Move:")
    solver_3.print_board(board)

    # Problem 4 Example
    print("Welcome to the Chip Placement Optimization System!")
    print("=" * 60)
    BOARD_WIDTH, BOARD_HEIGHT = 10, 10
    chip_specifications = {
        1: {"w": 2, "h": 4, "y": 0, "x": 0},
        2: {"w": 2, "h": 5, "y": 1, "x": 1},
        3: {"w": 1, "h": 3, "y": 0, "x": 1},
        4: {"w": 2, "h": 5, "y": 4, "x": 2},
        5: {"w": 2, "h": 4, "y": 3, "x": 3},
        6: {"w": 1, "h": 4, "y": 2, "x": 2},
        7: {"w": 2, "h": 5, "y": 5, "x": 0},
        8: {"w": 1, "h": 3, "y": 6, "x": 4},
    }
    required_connections = {
        (1, 2),
        (2, 6),
        (2, 3),
        (3, 5),
        (4, 5),
        (5, 6),
        (1, 6),
        (7, 4),
        (7, 2),
        (8, 5),
    }
    print(f"Circuit Board: {BOARD_WIDTH} x {BOARD_HEIGHT} grid")
    print(f"Number of chips: {len(chip_specifications)}")
    print(f"Number of connections: {len(required_connections)}")
    solver_4 = ChipPlacement(
        BOARD_WIDTH, BOARD_HEIGHT, chip_specifications, required_connections
    )
    optimizer = solver_4.ChipPlacementOptimizer(
        BOARD_WIDTH, BOARD_HEIGHT, chip_specifications, required_connections
    )
    initial_positions = {
        chip_id: specs["x"] for chip_id, specs in chip_specifications.items()
    }
    initial_score = optimizer.evaluate_placement_quality(initial_positions)[0]
    print(f"Initial conflict score: {initial_score}")
    visualizer = ChipVisualizationTool(optimizer)
    visualizer.display_grid_layout(initial_positions, "Initial Chip Arrangement")
    optimized_positions, final_score = optimizer.optimize_placement(initial_positions)
    visualizer.display_grid_layout(optimized_positions, "Optimized Chip Arrangement")
    visualizer.print_detailed_summary(
        initial_positions, optimized_positions, initial_score, final_score
    )
    visualizer.create_progress_charts(
        initial_positions, optimized_positions, initial_score, final_score
    )
    print(f"\nOptimization Complete!")
    print(f"Algorithm used: Greedy Hill Climbing with local search")
    print(f"Strategy: Iteratively move chips left/right to minimize conflicts")
    print(f"Termination: Stops when no beneficial moves remain")
