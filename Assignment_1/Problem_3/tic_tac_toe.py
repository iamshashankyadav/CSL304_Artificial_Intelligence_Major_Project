import math

X, O, E = "X", "O", "_"


class TicTacToe:
    X, O, E = "X", "O", "_"

    def print_board(board):
        for row in board:
            print(" ".join(row))
        print()

    def evaluation(board):
        lines = []
        for i in range(3):
            lines.append(board[i])
            lines.append([board[0][i], board[1][i], board[2][i]])
        lines.append([board[0][0], board[1][1], board[2][2]])
        lines.append([board[0][2], board[1][1], board[2][0]])

        X1 = X2 = X3 = O1 = O2 = O3 = 0
        for line in lines:
            if O not in line:
                c = line.count(X)
                if c == 1:
                    X1 += 1
                elif c == 2:
                    X2 += 1
                elif c == 3:
                    X3 += 1
            if X not in line:
                c = line.count(O)
                if c == 1:
                    O1 += 1
                elif c == 2:
                    O2 += 1
                elif c == 3:
                    O3 += 1

        return 8 * X3 + 3 * X2 + X1 - (8 * O3 + 3 * O2 + O1)

    def is_terminal(board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != E:
                return True
            if board[0][i] == board[1][i] == board[2][i] != E:
                return True
        if board[0][0] == board[1][1] == board[2][2] != E:
            return True
        if board[0][2] == board[1][1] == board[2][0] != E:
            return True
        return all(board[i][j] != E for i in range(3) for j in range(3))

    def get_moves(board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == E]

    # 1. Plain Minimax
    def minimax_plain(self, board, depth, maximizing):
        if self.is_terminal(board) or depth == 0:
            return self.evaluation(board), None

        if maximizing:
            max_eval, best_move = -math.inf, None
            for i, j in self.get_moves(board):
                board[i][j] = X
                eval_val, _ = self.minimax_plain(board, depth - 1, False)
                board[i][j] = E
                if eval_val > max_eval:
                    max_eval, best_move = eval_val, (i, j)
            return max_eval, best_move
        else:
            min_eval, best_move = math.inf, None
            for i, j in self.get_moves(board):
                board[i][j] = O
                eval_val, _ = self.minimax_plain(board, depth - 1, True)
                board[i][j] = E
                if eval_val < min_eval:
                    min_eval, best_move = eval_val, (i, j)
            return min_eval, best_move

    # 2. Minimax with Alpha–Beta
    def minimax_ab(self, board, depth, alpha, beta, maximizing):
        if self.is_terminal(board) or depth == 0:
            return self.evaluation(board), None

        if maximizing:
            max_eval, best_move = -math.inf, None
            for i, j in self.get_moves(board):
                board[i][j] = X
                eval_val, _ = self.minimax_ab(board, depth - 1, alpha, beta, False)
                board[i][j] = E
                if eval_val > max_eval:
                    max_eval, best_move = eval_val, (i, j)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval, best_move = math.inf, None
            for i, j in self.get_moves(board):
                board[i][j] = O
                eval_val, _ = self.minimax_ab(board, depth - 1, alpha, beta, True)
                board[i][j] = E
                if eval_val < min_eval:
                    min_eval, best_move = eval_val, (i, j)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return min_eval, best_move
