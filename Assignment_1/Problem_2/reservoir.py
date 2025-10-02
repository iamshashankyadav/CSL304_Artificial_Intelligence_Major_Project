from collections import deque
from fractions import Fraction
from decimal import Decimal, getcontext
import math
import heapq
import matplotlib.pyplot as plt

getcontext().prec = 28


class Reservoir:
    def parse_line_of_numbers(s):
        return [Fraction(Decimal(x)) for x in s.strip().split()]

    def pour(state, i, j, capacities):
        src, dst = state[i], state[j]
        cap_src, cap_dst = capacities[i], capacities[j]
        min_src = cap_src * Fraction(1, 5)
        available = src - min_src
        if available <= 0:
            return None, Fraction(0)
        space_dst = cap_dst - dst
        if space_dst <= 0:
            return None, Fraction(0)
        transfer = min(available, space_dst)
        if transfer <= 0:
            return None, Fraction(0)
        new_state = list(state)
        new_state[i] -= transfer
        new_state[j] += transfer
        return tuple(new_state), transfer

    def reconstruct_path(parent, end_state):
        path, states, cur = [], [], end_state
        while cur in parent:
            prev, action = parent[cur]
            path.append(action)
            states.append(cur)
            cur = prev
        states.append(cur)
        path.reverse()
        states.reverse()
        return path, states

    def bfs(start, target, capacities, self):
        q = deque([start])
        parent, visited = {}, {start}
        while q:
            state = q.popleft()
            if state == target:
                return self.reconstruct_path(parent, state)
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    new_state, _ = self.pour(state, i, j, capacities)
                    if new_state and new_state not in visited:
                        visited.add(new_state)
                        parent[new_state] = (state, (i, j))
                        q.append(new_state)
        return None, None

    def dfs_limited(self, start, target, capacities, max_depth=20):
        visited_path, parent = {start}, {}

        def dfs(state, depth):
            if state == target:
                return True
            if depth >= max_depth:
                return False
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    new_state, _ = self.pour(state, i, j, capacities)
                    if new_state and new_state not in visited_path:
                        visited_path.add(new_state)
                        parent[new_state] = (state, (i, j))
                        if dfs(new_state, depth + 1):
                            return True
                        visited_path.remove(new_state)
            return False

        if dfs(start, 0):
            return self.reconstruct_path(parent, target)
        return None, None

    def heuristic_d_over_max_capacity(state, target, capacities):
        total_deficit = sum(max(target[i] - state[i], 0) for i in range(3))
        if total_deficit == 0:
            return 0
        return math.ceil(float(total_deficit / max(capacities)))

    def a_star(self, start, target, capacities, heuristic_func):
        gscore, fscore, parent = {start: 0}, {start: heuristic_func(start)}, {}
        open_heap, closed = [(fscore[start], 0, start)], set()
        while open_heap:
            f, g, state = heapq.heappop(open_heap)
            if state in closed:
                continue
            closed.add(state)
            if state == target:
                return self.reconstruct_path(parent, state)
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    new_state, _ = self.pour(state, i, j, capacities)
                    if not new_state:
                        continue
                    tentative_g = gscore[state] + 1
                    if new_state in gscore and tentative_g >= gscore[new_state]:
                        continue
                    parent[new_state] = (state, (i, j))
                    gscore[new_state] = tentative_g
                    h = heuristic_func(new_state)
                    fscore[new_state] = tentative_g + h
                    heapq.heappush(
                        open_heap, (fscore[new_state], tentative_g, new_state)
                    )
        return None, None

    def print_solution_sequence(seq):
        for i, j in seq:
            print(f"Open valve ({i+1}->{j+1})")
        print(f"Number of valve operations = {len(seq)}")

    def print_states_with_transfers(states, capacities):
        print("States (R1, R2, R3):")
        for idx, s in enumerate(states):
            s_floats = [float(x) for x in s]
            print(
                f" Step {idx}: ({s_floats[0]:.6g}, {s_floats[1]:.6g}, {s_floats[2]:.6g})"
            )

    def visualize_solution(states, actions, capacities, title="Valve Pouring Solution"):
        steps = list(range(len(states)))
        r1, r2, r3 = (
            [float(s[0]) for s in states],
            [float(s[1]) for s in states],
            [float(s[2]) for s in states],
        )
        plt.figure(figsize=(9, 5))
        plt.plot(steps, r1, marker="o", label="R1")
        plt.plot(steps, r2, marker="o", label="R2")
        plt.plot(steps, r3, marker="o", label="R3")
        plt.xlabel("Operation step (0 = start)")
        plt.ylabel("Water amount")
        plt.title(title)
        plt.grid(True)
        plt.legend()
        for k, act in enumerate(actions):
            i, j = act
            x = k + 0.5
            y = (
                float(states[k][i])
                + float(states[k + 1][i])
                + float(states[k][j])
                + float(states[k + 1][j])
            ) / 4.0
            plt.annotate(
                f"{i+1}->{j+1}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=9,
            )
        plt.tight_layout()
        plt.show()

    def run_all_methods(self, capacities, initial, target):
        print("=== BFS ===")
        bfs_seq, bfs_states = self.bfs(initial, target, capacities)
        if bfs_seq:
            self.print_solution_sequence(bfs_seq)
            self.print_states_with_transfers(bfs_states, capacities)
        else:
            print("BFS: No solution found.")
        print("\n=== DFS ===")
        max_depth = max(20, len(bfs_seq) * 2) if bfs_seq else 20
        dfs_seq, dfs_states = self.dfs_limited(
            initial, target, capacities, max_depth=max_depth
        )
        if dfs_seq:
            self.print_solution_sequence(dfs_seq)
            self.print_states_with_transfers(dfs_states, capacities)
        else:
            print(f"DFS: No solution within depth {max_depth}.")
        print("\n=== A* (h=0) ===")
        a0_seq, a0_states = self.a_star(initial, target, capacities, lambda s: 0)
        if a0_seq:
            self.print_solution_sequence(a0_seq)
            self.print_states_with_transfers(a0_states, capacities)
        else:
            print("A*(h=0): No solution found.")
        print("\n=== A* (h_deficit) ===")
        hfunc = lambda s: self.heuristic_d_over_max_capacity(s, target, capacities)
        a1_seq, a1_states = self.a_star(initial, target, capacities, hfunc)
        if a1_seq:
            self.print_solution_sequence(a1_seq)
            self.print_states_with_transfers(a1_states, capacities)
        else:
            print("A*(h_deficit): No solution found.")
        if bfs_seq:
            self.visualize_solution(bfs_states, bfs_seq, capacities, "BFS Solution")
        elif a1_seq:
            self.visualize_solution(
                a1_states, a1_seq, capacities, "A* (h_deficit) Solution"
            )
        elif a0_seq:
            self.visualize_solution(a0_states, a0_seq, capacities, "A* (h=0) Solution")
        elif dfs_seq:
            self.visualize_solution(dfs_states, dfs_seq, capacities, "DFS Solution")
        else:
            print("No solution available to visualize.")
