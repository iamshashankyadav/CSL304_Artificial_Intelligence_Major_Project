from Problem_1.taxi_routing import TaxiRouting
from Problem_2.reservoir import Reservoir
from Problem_3.tic_tac_toe import TicTacToe
from Problem_4.chip_replacement import ChipPlacement


def main():
    # Problem 1 Example
    coords = [
        (0, 0),
        (30, 0),
        (80, 0),
        (30, 60),
        (120, 0),
        (30, 120),
        (60, 120),
        (110, 120),
    ]
    edges = [
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
    trips = [(2, 7), (1, 8), (3, 4)]
    tr = TaxiRouting(8, 9, 3, 30, 40, coords, edges, trips)
    tr.solve()

    # Problem 2 Example
    caps = [8.0, 5.0, 3.0]
    init = [8.0, 0.0, 0.0]
    target = [2.4, 5.0, 0.6]
    r = Reservoir(caps, init, target)
    r.solve()

    # Problem 3 Example
    board = "_X__0X__0".replace("0", "O")
    ttt = TicTacToe(board)
    ttt.solve()

    # Problem 4 Example
    chips = {
        1: (2, 4, 0, 0),
        2: (2, 5, 1, 1),
        3: (1, 3, 0, 1),
        4: (2, 5, 4, 2),
        5: (2, 4, 3, 3),
        6: (1, 4, 2, 2),
        7: (2, 5, 5, 0),
        8: (1, 3, 6, 4),
    }
    connections = [
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
    ]
    cp = ChipPlacement(chips, connections)
    cp.solve()
