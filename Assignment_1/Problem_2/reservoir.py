from collections import deque


class Reservoir:
    def __init__(self, caps, init, target):
        self.caps = caps
        self.init = tuple(init)
        self.target = tuple(target)
        self.min_levels = [0.2 * c for c in caps]

    def valid(self, state):
        return all(
            state[i] >= self.min_levels[i] - 1e-6 and state[i] <= self.caps[i] + 1e-6
            for i in range(3)
        )

    def next_states(self, state):
        states = []
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                src = state[i]
                dst = state[j]
                src_min = self.min_levels[i]
                give = src - src_min
                take = self.caps[j] - dst
                if give <= 0 or take <= 0:
                    continue
                transfer = min(give, take)
                new = list(state)
                new[i] -= transfer
                new[j] += transfer
                states.append((tuple(new), (i + 1, j + 1)))
        return states

    def bfs(self):
        q = deque([(self.init, [])])
        seen = {self.init}
        while q:
            state, ops = q.popleft()
            if all(abs(state[i] - self.target[i]) < 1e-6 for i in range(3)):
                return ops
            for nxt, op in self.next_states(state):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, ops + [op]))
        return None

    def solve(self):
        ops = self.bfs()
        print("\n--- Problem 2 Results ---")
        if ops:
            for a, b in ops:
                print(f"Open valve ({a}->{b})")
            print("Number of valve operations =", len(ops))
