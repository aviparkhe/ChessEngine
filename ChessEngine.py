# Chess Engine File
import opcode
import queue

import moviepy.Clip


class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "K": self.get_king_moves,
            "Q": self.get_queen_moves
        }

        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # update king's location if moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

    def undo_move(self):
        if len(self.move_log) != 0: # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move # switch turns

            # update king's location if moved
            if move.piece_moved == "wK":
                self.white_king_location = (move.end_row, move.end_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.end_row, move.end_col)

    def get_valid_moves(self):
        #1.) generate all possible moves
        moves = self.get_all_possible_moves()
        #2.) for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            #3. generate all opponent's moves
            #4.) for each of your opponent's moves, see if they attack your king
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i]) #5.) if they do attack your king, not a valid move
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0: # either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    # Determine if the current player is in check
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    # Determine if the can attack the square (r, c)
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == r and move.end_col == c: # square is under attack
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): # num of rows
            for c in range(len(self.board[r])): # num of cols in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) # calls correct move function based on piece type
        return moves

    # Get pawn moves
    def get_pawn_moves(self, r, c, moves):
        # white pawn moves
        if self.white_to_move:
            if self.board[r - 1][c] == "--": # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and  self.board[r - 2][c] == "--": # 2 aquare pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0: # capturing to the left
                if self.board[r - 1][c - 1][0] == "b": # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))

            if c + 1 <= 7: # capturing to the right
                if self.board[r - 1][c + 1][0] == "b": # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        # black pawn moves
        else:
            if self.board[r + 1][c] == "--": # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and  self.board[r + 2][c] == "--": # 2 aquare pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0: # capturing to the left
                if self.board[r + 1][c - 1][0] == "w": # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))

            if c + 1 <= 7: # capturing to the right
                if self.board[r + 1][c + 1][0] == "w": # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

        # pawn promotions


    # Get rook moves
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on the board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off the board
                    break

    # Get kinght moves
    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.white_to_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # not an ally color (empty or enemy piece)
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    # Get bishop moves
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on the board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off the board
                    break

    # Get king moves
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # not an ally color (empty or enemy piece)
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    # Get queen moves
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)



class Move():
    # maps keys to values
    # key: value

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}

    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    # Overrides the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

