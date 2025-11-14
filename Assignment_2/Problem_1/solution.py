import copy
from typing import List, Set, Tuple, Optional
import itertools


class SudokuCSP:
    def __init__(self, grid: List[List[int]]):
        self.grid = [row[:] for row in grid]  # 9x9 grid, 0 for empty
        self.n = 9
        self.sqrt_n = 3
        self.variables = [
            (i, j) for i in range(self.n) for j in range(self.n) if self.grid[i][j] == 0
        ]
        self.domains = self._initialize_domains()
        self.assignments = {}  # (i,j) -> value
        self.neighbors = self._build_neighbors()

    def _initialize_domains(self) -> dict:
        domains = {}
        for i, j in self.variables:
            used = set()
            # Row
            for k in range(self.n):
                if self.grid[i][k] != 0:
                    used.add(self.grid[i][k])
            # Col
            for k in range(self.n):
                if self.grid[k][j] != 0:
                    used.add(self.grid[k][j])
            # Box
            box_i, box_j = (i // self.sqrt_n) * self.sqrt_n, (
                j // self.sqrt_n
            ) * self.sqrt_n
            for di in range(self.sqrt_n):
                for dj in range(self.sqrt_n):
                    val = self.grid[box_i + di][box_j + dj]
                    if val != 0:
                        used.add(val)
            domains[(i, j)] = set(range(1, 10)) - used
        return domains

    def _build_neighbors(self) -> dict:
        neighbors = {}
        for var in self.variables:
            i, j = var
            neigh = set()
            # Row
            for k in range(self.n):
                if (i, k) in self.variables and (i, k) != var:
                    neigh.add((i, k))
            # Col
            for k in range(self.n):
                if (k, j) in self.variables and (k, j) != var:
                    neigh.add((k, j))
            # Box
            box_i, box_j = (i // self.sqrt_n) * self.sqrt_n, (
                j // self.sqrt_n
            ) * self.sqrt_n
            for di in range(self.sqrt_n):
                for dj in range(self.sqrt_n):
                    ni, nj = box_i + di, box_j + dj
                    if (ni, nj) in self.variables and (ni, nj) != var:
                        neigh.add((ni, nj))
            neighbors[var] = neigh
        return neighbors

    def is_consistent(self, var: Tuple[int, int], value: int) -> bool:
        i, j = var
        # Row
        for k in range(self.n):
            if self.grid[i][k] == value:
                return False
        # Col
        for k in range(self.n):
            if self.grid[k][j] == value:
                return False
        # Box
        box_i, box_j = (i // self.sqrt_n) * self.sqrt_n, (
            j // self.sqrt_n
        ) * self.sqrt_n
        for di in range(self.sqrt_n):
            for dj in range(self.sqrt_n):
                if self.grid[box_i + di][box_j + dj] == value:
                    return False
        return True

    def forward_check(self, var: Tuple[int, int], value: int) -> bool:
        i, j = var
        # Temporarily assign
        self.grid[i][j] = value
        # Prune neighbors
        for neigh in self.neighbors.get(var, []):
            ni, nj = neigh
            if self.grid[ni][nj] == 0:  # Unassigned
                old_domain = self.domains[neigh].copy()
                self.domains[neigh] -= {
                    value
                }  # Remove value if in row/col/box, but since consistent, it's row/col/box prune
                # Check row prune
                for k in range(self.n):
                    if (
                        k != j and self.grid[i][k] == value
                    ):  # Wait, already assigned, but prune based on this
                        pass  # Actually, since is_consistent checked, but for forward, remove from neigh domains if conflict
                # More precise: for each neigh, remove values that conflict with this assignment
                # But since constraints are all-diff, remove value from neigh if same row/col/box
                if (
                    ni == i
                    or nj == j
                    or (
                        (ni // self.sqrt_n) == (i // self.sqrt_n)
                        and (nj // self.sqrt_n) == (j // self.sqrt_n)
                    )
                ):
                    self.domains[neigh].discard(value)
                if not self.domains[neigh]:
                    # Backtrack
                    self.grid[i][j] = 0
                    self.domains[neigh] = old_domain
                    return False
        self.assignments[var] = value
        return True

    def undo_forward_check(self, var: Tuple[int, int]):
        i, j = var
        self.grid[i][j] = 0
        del self.assignments[var]
        # Restore domains - but since we only removed one value, need to track removed
        # For simplicity, I'll re-init domains for affected, but inefficient; in practice, track removals
        # Here, since small, I'll skip full restore and use copy in recurse

    def select_variable(self, heuristic: str = "none") -> Optional[Tuple[int, int]]:
        if not self.variables:
            return None
        if heuristic == "mrv":
            return min(
                [v for v in self.variables if v not in self.assignments],
                key=lambda v: len(self.domains[v]),
            )
        elif heuristic == "degree":
            return min(
                [v for v in self.variables if v not in self.assignments],
                key=lambda v: len(self.neighbors[v]),
            )
        else:
            return self.variables[0]  # Arbitrary

    def order_values(self, var: Tuple[int, int], heuristic: str = "none") -> List[int]:
        if heuristic == "lcv":
            values = list(self.domains[var])

            def constraining_count(val):
                count = 0
                for neigh in self.neighbors.get(var, []):
                    if neigh in self.assignments:
                        continue
                    if val in self.domains[neigh]:  # Would prune this
                        count += 1
                return count

            return sorted(values, key=constraining_count)
        return list(self.domains[var])

    def revise(self, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
        revised = False
        i1, j1 = xi
        i2, j2 = xj
        same_row = i1 == i2
        same_col = j1 == j2
        same_box = (i1 // 3 == i2 // 3) and (j1 // 3 == j2 // 3)
        if not (same_row or same_col or same_box):
            return False
        to_remove = []
        for val in self.domains[xi]:
            consistent = False
            for valj in self.domains[xj]:
                # Check if val in xi consistent with valj in xj
                if val != valj:  # All diff
                    consistent = True
                    break
            if not consistent:
                to_remove.append(val)
                revised = True
        for val in to_remove:
            self.domains[xi].remove(val)
        return revised

    def ac3(self) -> bool:
        queue = list(itertools.product(self.variables, self.variables))
        queue = [
            (xi, xj)
            for xi, xj in queue
            if xi != xj and xj in self.neighbors.get(xi, [])
        ]
        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in [
                    x
                    for x in self.variables
                    if x != xj and x in self.neighbors.get(xi, [])
                ]:
                    queue.append((xk, xi))
        return True

    def solve(
        self,
        forward_checking: bool = False,
        heuristic_var: str = "none",
        heuristic_val: str = "none",
        use_ac3: bool = False,
    ) -> bool:
        if use_ac3 and not self.ac3():
            return False
        var = self.select_variable(heuristic_var)
        if var is None:
            return True  # Solved
        for value in self.order_values(var, heuristic_val):
            if self.is_consistent(var, value):
                old_domains = copy.deepcopy(self.domains) if forward_checking else None
                if forward_checking:
                    if not self.forward_check(var, value):
                        self.domains = old_domains
                        continue
                if self.solve(forward_checking, heuristic_var, heuristic_val, use_ac3):
                    self.grid[var[0]][var[1]] = value
                    return True
                if forward_checking:
                    self.undo_forward_check(var)
                    self.domains = old_domains
        return False



