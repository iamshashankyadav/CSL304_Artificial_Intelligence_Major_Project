import time
from typing import List, Tuple, Optional, Set
from copy import deepcopy

class SudokuCSPSolver:
    def __init__(self, grid: List[List[int]]):
        self.initial_grid = [row[:] for row in grid]
        self.grid = [row[:] for row in grid]
        self.size = 9
        self.box_size = 3
        self.nodes_explored = 0
        self.backtracks = 0

    def reset(self):
        self.grid = [row[:] for row in self.initial_grid]
        self.nodes_explored = 0
        self.backtracks = 0

    def is_valid(self, row: int, col: int, num: int) -> bool:
        if num in self.grid[row]:
            return False

        for i in range(self.size):
            if self.grid[i][col] == num:
                return False

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i][j] == num:
                    return False

        return True

    def get_domain(self, row: int, col: int) -> List[int]:
        if self.grid[row][col] != 0:
            return []

        domain = []
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                domain.append(num)
        return domain

    def get_all_domains(self) -> List[List[List[int]]]:
        domains = [[[] for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    domains[i][j] = self.get_domain(i, j)
        return domains

    def find_empty(self) -> Optional[Tuple[int, int]]:
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def find_empty_mrv(self, domains: List[List[List[int]]]) -> Optional[Tuple[int, int]]:
        min_domain_size = float('inf')
        best_cell = None

        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    domain_size = len(domains[i][j])
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        best_cell = (i, j)

        return best_cell

    def get_degree(self, row: int, col: int) -> int:
        degree = 0

        for j in range(self.size):
            if j != col and self.grid[row][j] == 0:
                degree += 1

        for i in range(self.size):
            if i != row and self.grid[i][col] == 0:
                degree += 1

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.grid[i][j] == 0:
                    degree += 1

        return degree

    def find_empty_mrv_degree(self, domains: List[List[List[int]]]) -> Optional[Tuple[int, int]]:
        min_domain_size = float('inf')
        max_degree = -1
        best_cell = None

        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    domain_size = len(domains[i][j])
                    degree = self.get_degree(i, j)

                    if (domain_size < min_domain_size or
                        (domain_size == min_domain_size and degree > max_degree)):
                        min_domain_size = domain_size
                        max_degree = degree
                        best_cell = (i, j)

        return best_cell

    def order_by_lcv(self, row: int, col: int, domain: List[int]) -> List[int]:
        def count_constraints(num: int) -> int:
            count = 0

            for j in range(self.size):
                if j != col and self.grid[row][j] == 0:
                    if self.is_valid(row, j, num):
                        count += 1

            for i in range(self.size):
                if i != row and self.grid[i][col] == 0:
                    if self.is_valid(i, col, num):
                        count += 1

            box_row, box_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
                    if (i != row or j != col) and self.grid[i][j] == 0:
                        if self.is_valid(i, j, num):
                            count += 1

            return count

        return sorted(domain, key=lambda x: count_constraints(x))

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        neighbors = []

        for j in range(self.size):
            if j != col:
                neighbors.append((row, j))

        for i in range(self.size):
            if i != row:
                neighbors.append((i, col))

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != (row, col) and (i, j) not in neighbors:
                    neighbors.append((i, j))

        return neighbors

    def revise(self, domains, xi, xj) -> bool:
        revised = False
        xi_row, xi_col = xi
        xj_row, xj_col = xj

        new_domain = []
        for val in domains[xi_row][xi_col]:
            has_support = False
            for other_val in domains[xj_row][xj_col]:
                if val != other_val:
                    has_support = True
                    break

            if has_support:
                new_domain.append(val)
            else:
                revised = True

        domains[xi_row][xi_col] = new_domain
        return revised

    def ac3(self, domains) -> bool:
        queue = []

        for i in range(self.size):
            for j in range(self.size):
                if domains[i][j]:
                    neighbors = self.get_neighbors(i, j)
                    for ni, nj in neighbors:
                        if domains[ni][nj]:
                            queue.append(((i, j), (ni, nj)))

        while queue:
            xi, xj = queue.pop(0)
            if self.revise(domains, xi, xj):
                xi_row, xi_col = xi
                if not domains[xi_row][xi_col]:
                    return False

                neighbors = self.get_neighbors(xi_row, xi_col)
                for ni, nj in neighbors:
                    if (ni, nj) != xj and domains[ni][nj]:
                        queue.append(((ni, nj), xi))

        return True

    def update_domains(self, domains, row, col, num) -> bool:
        for j in range(self.size):
            if j != col and self.grid[row][j] == 0:
                if num in domains[row][j]:
                    domains[row][j].remove(num)
                    if not domains[row][j]:
                        return False

        for i in range(self.size):
            if i != row and self.grid[i][col] == 0:
                if num in domains[i][col]:
                    domains[i][col].remove(num)
                    if not domains[i][col]:
                        return False

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.grid[i][j] == 0:
                    if num in domains[i][j]:
                        domains[i][j].remove(num)
                        if not domains[i][j]:
                            return False

        return True

    def solve_backtracking(self) -> bool:
        empty = self.find_empty()
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num

                if self.solve_backtracking():
                    return True

                self.grid[row][col] = 0
                self.backtracks += 1

        return False

    def solve_forward_checking(self, domains) -> bool:
        empty = self.find_empty()
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        domain = domains[row][col][:]

        for num in domain:
            self.grid[row][col] = num

            old_domains = deepcopy(domains)
            domains[row][col] = [num]

            if self.update_domains(domains, row, col, num):
                if self.solve_forward_checking(domains):
                    return True

            self.grid[row][col] = 0
            for i in range(self.size):
                for j in range(self.size):
                    domains[i][j] = old_domains[i][j]
            self.backtracks += 1

        return False

    def solve_mrv(self, domains) -> bool:
        empty = self.find_empty_mrv(domains)
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        domain = domains[row][col][:]

        for num in domain:
            if self.is_valid(row, col, num):
                self.grid[row][col] = num

                old_domains = deepcopy(domains)
                domains[row][col] = [num]

                if self.update_domains(domains, row, col, num):
                    if self.solve_mrv(domains):
                        return True

                self.grid[row][col] = 0
                for i in range(self.size):
                    for j in range(self.size):
                        domains[i][j] = old_domains[i][j]
                self.backtracks += 1

        return False

    def solve_mrv_degree(self, domains) -> bool:
        empty = self.find_empty_mrv_degree(domains)
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        domain = domains[row][col][:]

        for num in domain:
            if self.is_valid(row, col, num):
                self.grid[row][col] = num

                old_domains = deepcopy(domains)
                domains[row][col] = [num]

                if self.update_domains(domains, row, col, num):
                    if self.solve_mrv_degree(domains):
                        return True

                self.grid[row][col] = 0
                for i in range(self.size):
                    for j in range(self.size):
                        domains[i][j] = old_domains[i][j]
                self.backtracks += 1

        return False

    def solve_full_heuristics(self, domains) -> bool:
        empty = self.find_empty_mrv_degree(domains)
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        domain = self.order_by_lcv(row, col, domains[row][col])

        for num in domain:
            if self.is_valid(row, col, num):
                self.grid[row][col] = num

                old_domains = deepcopy(domains)
                domains[row][col] = [num]

                if self.update_domains(domains, row, col, num):
                    if self.solve_full_heuristics(domains):
                        return True

                self.grid[row][col] = 0
                for i in range(self.size):
                    for j in range(self.size):
                        domains[i][j] = old_domains[i][j]
                self.backtracks += 1

        return False

    def solve_ac3(self, domains) -> bool:
        if not self.ac3(domains):
            return False

        empty = self.find_empty_mrv_degree(domains)
        if not empty:
            return True

        row, col = empty
        self.nodes_explored += 1

        domain = domains[row][col][:]

        for num in domain:
            self.grid[row][col] = num

            old_domains = deepcopy(domains)
            domains[row][col] = [num]

            if self.solve_ac3(domains):
                return True

            self.grid[row][col] = 0
            for i in range(self.size):
                for j in range(self.size):
                    domains[i][j] = old_domains[i][j]
            self.backtracks += 1

        return False

    def solve(self, algorithm: str = 'backtracking') -> Tuple[bool, float]:
        self.reset()
        start_time = time.time()

        success = False
        if algorithm == 'backtracking':
            success = self.solve_backtracking()
        elif algorithm == 'forward_checking':
            domains = self.get_all_domains()
            success = self.solve_forward_checking(domains)
        elif algorithm == 'mrv':
            domains = self.get_all_domains()
            success = self.solve_mrv(domains)
        elif algorithm == 'mrv_degree':
            domains = self.get_all_domains()
            success = self.solve_mrv_degree(domains)
        elif algorithm == 'full_heuristics':
            domains = self.get_all_domains()
            success = self.solve_full_heuristics(domains)
        elif algorithm == 'ac3':
            domains = self.get_all_domains()
            success = self.solve_ac3(domains)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        time_taken = time.time() - start_time
        return success, time_taken

    def print_grid(self):
        for i in range(self.size):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            for j in range(self.size):
                if j % 3 == 0 and j != 0:
                    print("|", end=" ")
                print(self.grid[i][j] if self.grid[i][j] != 0 else ".", end=" ")
            print()

    def print_stats(self):
        print(f"\nStatistics:")
        print(f"  Nodes explored: {self.nodes_explored}")
        print(f"  Backtracks: {self.backtracks}")

if __name__ == "__main__":
    main()
