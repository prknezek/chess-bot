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
    '''
    Takes a move as a parameter and executes it (will not work for castling, en passant, and promotion)
    '''
    def make_move(self, move) :
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    '''
    Undo the last move made
    '''
    def undo_move(self) :
        if self.move_log :
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
    
    '''
    All moves considering checks
    '''
    def get_valid_moves(self) :
        return self.get_all_possible_moves() # not worrying about checks yet

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self) :
        moves = [Move((6,4), (4, 4), self.board)]
        for r in range(len(self.board)) :
            for c in range(len(self.board[r])) :
                square = self.board[r][c]
                turn = square[0] # get color of piece

                # then we should look at this piece
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move): 
                    piece = square[1]
                    if piece == "p" :
                        self.get_pawn_moves(r, c, moves)
                    elif piece == "R" :
                        self.get_rook_moves(r, c, moves)
        
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list of valid moves
    '''
    def get_pawn_moves(self, r, c, moves) :
        pass

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list of valid moves
    '''
    def get_rook_moves(self, r, c, moves) :
        pass



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
        self.piece_captured = board[self.end_row][self.end_col] # piece_captured can be "--" to represent nothing was captured

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    
    '''
    Overwriting the equals method
    '''
    def __eq__(self, __value) :
        if isinstance(__value, Move) :
            return self.move_id == __value.move_id
        return False

    '''
    Returns a move made in chess notation (for debugging purposes)
    '''
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
    
    '''
    Helper method for get_chess_notation()
    '''
    def get_rank_file(self, r, c) :
        return self.cols_to_files[c] + self.rows_to_ranks[r]