class ChipPlacement:
    def __init__(self, chips, connections, W=10, H=10):
        self.chips = chips
        self.connections = connections
        self.W = W
        self.H = H

    def overlap(self, c1, c2):
        x1, y1, w1, h1 = (
            self.chips[c1][3],
            self.chips[c1][2],
            self.chips[c1][0],
            self.chips[c1][1],
        )
        x2, y2, w2, h2 = (
            self.chips[c2][3],
            self.chips[c2][2],
            self.chips[c2][0],
            self.chips[c2][1],
        )
        ox = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        oy = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        return ox * oy

    def wiring(self, c1, c2):
        x1, w1, y1 = self.chips[c1][3], self.chips[c1][0], self.chips[c1][2]
        x2, w2, y2 = self.chips[c2][3], self.chips[c2][0], self.chips[c2][2]
        return max(0, x2 - (x1 + w1), x1 - (x2 + w2)) + abs(y1 - y2)

    def conflict(self):
        score = 0
        for a, b in self.connections:
            score += self.wiring(a, b)
            score += self.overlap(a, b)
        return score

    def descent(self, iters=20):
        history = []
        for _ in range(iters):
            improved = False
            best_score = self.conflict()
            for cid in self.chips:
                origx = self.chips[cid][3]
                for dx in [-1, 1]:
                    self.chips[cid] = (
                        self.chips[cid][0],
                        self.chips[cid][1],
                        self.chips[cid][2],
                        origx + dx,
                    )
                    if self.chips[cid][3] < 0:
                        self.chips[cid] = (
                            self.chips[cid][0],
                            self.chips[cid][1],
                            self.chips[cid][2],
                            origx,
                        )
                    score = self.conflict()
                    if score < best_score:
                        best_score = score
                        improved = True
                    else:
                        self.chips[cid] = (
                            self.chips[cid][0],
                            self.chips[cid][1],
                            self.chips[cid][2],
                            origx,
                        )
            history.append(best_score)
            if not improved:
                break
        return history

    def solve(self):
        hist = self.descent()
        print("\n--- Problem 4 Results ---")
        print("Final conflict score:", hist[-1])
        print("Final positions:")
        for cid in self.chips:
            w, h, y, x = self.chips[cid]
            print(f"Chip {cid}: (x={x}, y={y})")
