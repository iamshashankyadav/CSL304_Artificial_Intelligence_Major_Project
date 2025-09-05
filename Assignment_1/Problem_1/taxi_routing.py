import math
import heapq


class TaxiRouting:
    def __init__(self, n, m, p, w, s, coords, edges, trips):
        self.n = n
        self.m = m
        self.p = p
        self.w = w
        self.s = s
        self.coords = coords
        self.graph = {i: [] for i in range(1, n + 1)}
        for u, v, d in edges:
            self.graph[u].append((v, d))
            self.graph[v].append((u, d))
        self.trips = trips
        self.time_per_km = 60.0 / s
        self.edge_usage = {}

    def heuristic(self, a, b):
        (x1, y1) = self.coords[a - 1]
        (x2, y2) = self.coords[b - 1]
        return math.dist((x1, y1), (x2, y2)) * self.time_per_km

    def astar(self, start, goal, start_time=0):
        pq = [(0, start_time, start, [])]
        dist = {start: 0}
        while pq:
            est_cost, t, node, path = heapq.heappop(pq)
            if node == goal:
                return path + [goal], t
            for nxt, d in self.graph[node]:
                edge_time = d * self.time_per_km
                wait = 0
                edge = tuple(sorted((node, nxt)))
                if edge not in self.edge_usage:
                    self.edge_usage[edge] = []
                conflicts = [
                    interval
                    for interval in self.edge_usage[edge]
                    if not (t + edge_time <= interval[0] or t >= interval[1])
                ]
                if len(conflicts) >= 2:
                    wait = self.w
                new_time = t + edge_time + wait
                if nxt not in dist or new_time < dist[nxt]:
                    dist[nxt] = new_time
                    heapq.heappush(
                        pq,
                        (
                            new_time + self.heuristic(nxt, goal),
                            new_time,
                            nxt,
                            path + [node],
                        ),
                    )
                self.edge_usage[edge].append((t + wait, t + wait + edge_time))
        return None, None

    def solve(self):
        results = []
        total = 0
        for i, (src, dst) in enumerate(self.trips, 1):
            path, time = self.astar(src, dst, 0)
            results.append((i, src, dst, path, time))
            total += time
        print("\n--- Problem 1 Results ---")
        for i, src, dst, path, time in results:
            print(f"Taxi {i}: Passenger {src}->{dst}")
            print(f"Route: {' -> '.join(map(str,path))}")
            print(f"Total time = {time:.1f} minutes\n")
        print(f"Overall Completion Time = {total:.1f} minutes")
