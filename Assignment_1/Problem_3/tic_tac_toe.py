class TicTacToe:
    def __init__(self, board):
        self.board = board

    def evaluate(self, b):
        score = 0
        lines = [
            [b[0], b[1], b[2]],
            [b[3], b[4], b[5]],
            [b[6], b[7], b[8]],
            [b[0], b[3], b[6]],
            [b[1], b[4], b[7]],
            [b[2], b[5], b[8]],
            [b[0], b[4], b[8]],
            [b[2], b[4], b[6]],
        ]

        def count(line, ch):
            return line.count(ch)

        for line in lines:
            if count(line, "O") == 0:
                if count(line, "X") == 3:
                    score += 8
                elif count(line, "X") == 2:
                    score += 3
                elif count(line, "X") == 1:
                    score += 1
            if count(line, "X") == 0:
                if count(line, "O") == 3:
                    score -= 8
                elif count(line, "O") == 2:
                    score -= 3
                elif count(line, "O") == 1:
                    score -= 1
        return score

    def minimax(self, b, depth, alpha, beta, maximizing):
        if "_" not in b:
            return self.evaluate(b), None
        if maximizing:
            best = -1e9
            move = None
            for i in range(9):
                if b[i] == "_":
                    nb = b[:i] + "X" + b[i + 1 :]
                    val, _ = self.minimax(nb, depth + 1, alpha, beta, False)
                    if val > best:
                        best, val = val, val
                        move = i
                    alpha = max(alpha, val)
                    if beta <= alpha:
                        break
            return best, move
        else:
            best = 1e9
            move = None
            for i in range(9):
                if b[i] == "_":
                    nb = b[:i] + "O" + b[i + 1 :]
                    val, _ = self.minimax(nb, depth + 1, alpha, beta, True)
                    if val < best:
                        best, val = val, val
                        move = i
                    beta = min(beta, val)
                    if beta <= alpha:
                        break
            return best, move

    def solve(self):
        score, move = self.minimax(self.board, 0, -1e9, 1e9, True)
        print("\n--- Problem 3 Results ---")
        print("Best move for X at position:", move)
        print("Evaluation score:", score)
