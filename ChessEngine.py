'''
Responsible for storing all the information about the current state of a chess game.
Also responsible for determining the valid moves at the current state.
Will keep a move log.
'''
class GameState() :
    def __init__(self) :
        # board is 8x8 2d list, each element has 2 characters
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'p'
        # "--" represents an empty space with no piece
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

        self.white_to_move = True
        self.move_log = []
    
    def make_move(self, move) :
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

class Move() :

    ranks_to_rows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, 
                     "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rows_to_ranks = {v : k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, 
                     "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board) :
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
    
    def get_chess_notation(self) :
        capture = ""
        if self.piece_captured != "--" :
            piece = self.piece_moved[1]
            start_file = self.get_rank_file(self.start_row, self.start_col)[0]
            if piece == "p" :
                piece = start_file
            
            capture = piece + "x" + self.get_rank_file(self.end_row, self.end_col)
            return capture
        else :
            piece = self.piece_moved[1]
            if piece == "p" :
                piece = ""

            return piece + self.get_rank_file(self.end_row, self.end_col)
    
    def get_rank_file(self, r, c) :
        return self.cols_to_files[c] + self.rows_to_ranks[r]