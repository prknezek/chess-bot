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

        self.move_functions = {'p' : self.get_pawn_moves, 'R' : self.get_rook_moves, 'N' : self.get_knight_moves,
                               'B' : self.get_bishop_moves, 'Q' : self.get_queen_moves, 'K' : self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.in_check = False
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = () # coordinates for the square where an enpassant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True) # have any rules been broken (not if castling is possible)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.pins = []
        self.checks = []

    '''
    Takes a move as a parameter and executes it (will not work for castling, en passant, and promotion)
    '''
    def make_move(self, move) :
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update the king's location if needed
        if move.piece_moved == "wK" :
            self.white_king_loc = (move.end_row, move.end_col)
        if move.piece_moved == "bK" :
            self.black_king_loc = (move.end_row, move.end_col)
        
        if move.is_pawn_promotion :
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'
        
        if move.is_enpassant_move :
            self.board[move.start_row][move.end_col] = '--' # capturing the pawn
        
        # update enpassant possible variable on 2 square pawn advances
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2 :
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else :
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move :
            if move.end_col - move.start_col == 2 : # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1] # moves the rook
                self.board[move.end_row][move.end_col + 1] = '--' # erase the old rook
            else : # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2] # moves the rook
                self.board[move.end_row][move.end_col - 2] = '--' # erase the old rook


        # update castling rights - whenever its a rook or a king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs))
        
        self.enpassant_possible_log.append(self.enpassant_possible)

    '''
    Undo the last move made
    '''
    def undo_move(self) :
        self.check_mate = self.stale_mate = False
        if self.move_log :
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update the king's location if needed
            if move.piece_moved == "wK" :
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == "bK" :
                self.black_king_loc = (move.start_row, move.start_col)
            if move.is_enpassant_move :
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured

            if len(self.enpassant_possible_log) > 0 :
                self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            if len(self.castle_rights_log) > 1 :
                self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]
            # undo castle move
            if move.is_castle_move :
                if move.end_col - move.start_col == 2 : # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1] # move rook back
                    self.board[move.end_row][move.end_col - 1] = '--'
                else : # queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'



    '''
    Update the castle rights given the move
    '''
    def update_castle_rights(self, move) :
        if move.piece_moved == 'wK' :
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK' :
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR' :
            if move.start_row == 7 :
                if move.start_col == 0 : # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7 : # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR' :
            if move.start_row == 0 :
                if move.start_col == 0 : # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7 : # right rook
                    self.current_castling_rights.bks = False
        # if a rook is captured
        if move.piece_captured == 'wR' :
            if move.end_row == 7 :
                if move.end_col == 0 :
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7 :
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR' :
            if move.end_row == 0 :
                if move.end_col == 0 :
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7 :
                    self.current_castling_rights.bks = False

    '''
    All moves considering checks
    '''
    def get_valid_moves(self) :
        temp_enpassant_possible = self.enpassant_possible
        # copy the current castling rights
        temp_castling_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        king_loc = self.white_king_loc if self.white_to_move else self.black_king_loc
        king_row = king_loc[0]
        king_col = king_loc[1]

        if self.in_check :
            if len(self.checks) == 1 :
                moves = self.get_all_possible_moves()
                # to block a check you must move a piece to block or move the king
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = [] # squares that pieces can move to
                # if knight, must capture knight or move king
                if piece_checking[1] == 'N' :
                    valid_squares = [(check_row, check_col)]
                else :
                    # print(f"CHECK LOC: {check_row} {check_col}")
                    # print(f"CHECK DIR: {check[2]} {check[3]}")
                    for i in range(1, 8) :
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col :
                            break
                    # print(f"VALID SQUARES: {valid_squares}")
                # get rid of any moves that dont block check or move king
                for i in range(len(moves) - 1, -1, -1) :
                    if moves[i].piece_moved[1] != "K" : # move doesn't move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares : # move doesn't block check or capture piece
                            del moves[i]
            else : # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else :
            moves = self.get_all_possible_moves()

        if self.white_to_move :
            self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
        else :
            self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)

        self.current_castling_rights = temp_castling_rights
        self.enpassant_possible = temp_enpassant_possible
        # check for checkmate or stalemate
        if len(moves) == 0 :
            if self.in_check :
                self.check_mate = True
            else :
                self.stale_mate = True

        return moves

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self) :
        moves = []
        for r in range(len(self.board)) :
            for c in range(len(self.board[r])) :
                square = self.board[r][c]
                turn = square[0] # get color of piece

                # then we should look at this piece
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move): 
                    piece = square[1]
                    # call the appropriate move function based on piece type
                    self.move_functions[piece](r, c, moves)
        
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list of valid moves
    '''
    def get_pawn_moves(self, r, c, moves) :
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1) :
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                del self.pins[i]
                break

        if self.white_to_move : # then we will look at the white pawns
            king_row, king_col = self.white_king_loc
            if self.board[r - 1][c] == "--" : 
                if not piece_pinned or pin_direction == (-1, 0) :
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # captures to the left
            if c - 1 >= 0 :
                if self.board[r - 1][c - 1][0] == "b" :
                    if not piece_pinned or pin_direction == (-1, -1) :
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassant_possible :
                    if not piece_pinned or pin_direction == (-1, -1) :
                        self.check_enpassant_possible(r, c, "w", moves, False)
            # captures to the right
            if c + 1 <= 7 :
                if self.board[r - 1][c + 1][0] == "b" :
                    if not piece_pinned or pin_direction == (-1, 1) :
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassant_possible :
                    if not piece_pinned or pin_direction == (-1, 1) :
                        self.check_enpassant_possible(r, c, "w", moves, True)
        else : # we look at black pawns
            # 1 and 2 square advance
            if self.board[r + 1][c] == "--" : 
                if not piece_pinned or pin_direction == (1, 0) :
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # captures to the left
            if c - 1 >= 0 :
                if self.board[r + 1][c - 1][0] == "w" :
                    if not piece_pinned or pin_direction == (1, -1) :
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassant_possible :
                    if not piece_pinned or pin_direction == (1, -1) :
                        self.check_enpassant_possible(r, c, "b", moves, False)
            # captures to the right
            if c + 1 <= 7 :
                if self.board[r + 1][c + 1][0] == "w" :
                    if not piece_pinned or pin_direction == (1, 1) :
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassant_possible :
                    if not piece_pinned or pin_direction == (1, 1) :
                        self.check_enpassant_possible(r, c, "b", moves, True)
    
    '''
    Helper function for determining if an enpassant move can be made
    '''
    def check_enpassant_possible(self, r, c, color, moves, is_right) :
        king_row, king_col = self.black_king_loc if color == "b" else self.white_king_loc
        attacking_piece = blocking_piece = False
        offset = 1 if is_right else 0
        if king_row == r :
            if king_col < c :
                inside_range = range(king_col + 1, c - 1 + offset)
                outside_range = range(c + 1 + offset, 8)
            else :
                inside_range = range(king_col - 1, c + offset, -1)
                outside_range = range(c-2 + offset, -1, -1)
            for i in inside_range :
                if self.board[r][i] != '--' : # some other piece besides enpassant pawns blocking
                    blocking_piece = True
            for i in outside_range :
                square = self.board[r][i]
                if square[0] == ("w" if color == "b" else "b") and (square[1] == "R" or square[1] == "Q") :
                    attacking_piece = True
                    break
                elif square != "--" :
                    blocking_piece = True
        if not attacking_piece or blocking_piece :
            if is_right : # c + 1
                if color == "b" :
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))
                else :
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_enpassant_move=True))
            else : # c - 1
                if color == "b" :
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))
                else :
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_enpassant_move=True))
    
    '''
    Get the moves for a directional piece (R, B, Q)
    '''
    def get_directional_piece_moves(self, piece, r, c, moves, directions) :
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1) :
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if piece == "R" :
                    if self.board[r][c][1] != "Q" :
                        del self.pins[i]
                break
        
        opposite_color = "b" if self.white_to_move else "w"

        for d in directions :
            for i in range(1, 8) :
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8 :
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]) :
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--" : # empty space valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == opposite_color : # enemy piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else : # friendly piece invalid
                            break
                else : # off board
                    break
    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list of valid moves
    '''
    def get_rook_moves(self, r, c, moves) :
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        self.get_directional_piece_moves("R", r, c, moves, directions)

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list of valid moves
    '''
    def get_bishop_moves(self, r, c, moves) :
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        self.get_directional_piece_moves("B", r, c, moves, directions)

    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list of valid moves
    '''
    def get_queen_moves(self, r, c, moves) :
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        self.get_directional_piece_moves("Q", r, c, moves, directions)

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list of valid moves
    '''
    def get_knight_moves(self, r, c, moves) :
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1) :
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piece_pinned = True
                del self.pins[i]
                break

        ally_color = "w" if self.white_to_move else "b"
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for d in directions :
            end_row = d[0] + r
            end_col = d[1] + c
            if 0 <= end_row < 8 and 0 <= end_col < 8 :
                if not piece_pinned :
                    end_piece = self.board[end_row][end_col]
                    
                    if end_piece[0] != ally_color :
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_king_moves(self, r, c, moves) :
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8) :
            end_row = row_moves[i] + r
            end_col = col_moves[i] + c
            if 0 <= end_row < 8 and 0 <= end_col < 8 :
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color :
                    # place king on end square and check for checks
                    if ally_color == 'w' :
                        self.white_king_loc = (end_row, end_col)
                    else :
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check :
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == 'w' :
                        self.white_king_loc = (r, c)
                    else :
                        self.black_king_loc = (r, c)

    '''
    Get all valid castle moves for the king at (r, c) and add them to the list of moves
    '''
    def get_castle_moves(self, r, c, moves) :
        if self.in_check :
            return # we can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks) :
            self.get_king_side_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs) :
            self.get_queen_side_castle_moves(r, c, moves)

    def get_king_side_castle_moves(self, r, c, moves) :
        if self.board[r][c+1] == '--'  and self.board[r][c+2] == '--' :
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, r, c, moves) :
        if self.board[r][c-1] == '--'  and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2) :
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))

    def square_under_attack(self, r, c) :
        self.white_to_move = not self.white_to_move
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves :
            if move.end_row == r and move.end_col == c :
                return True
        return False

    '''
    Returns if the player is in check, a list of pins, and a list of checks
    '''
    def check_for_pins_and_checks(self) :
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        in_check = False

        if self.white_to_move :
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else :
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)) :
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8) :
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8 :
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K" :
                        if possible_pin == () : # 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else :
                            break
                    elif end_piece[0] == enemy_color :
                        type = end_piece[1]
                        # 5 possiblities in this conditional
                        # 1) orthoginally away from king and piece is a rook
                        # 2) diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) any direction and piece is a queen
                        # 5) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type =="B") or \
                                (i == 1 and type == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K") :
                            if possible_pin == () : # no piece blocking to check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else : # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else : # enemy piece not applying check
                            break
                else :
                    break # off the board

        # check for knight checks
        knight_moves = ((-1, 2), (-1, -2), (1, 2), (1, -2), (2, -1), (2, 1), (-2, -1), (-2, 1))
        for m in knight_moves :
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8 :
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N' : # enemy knight attack king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks

class CastleRights() :
    def __init__(self, wks, bks, wqs, bqs) :
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move() :

    ranks_to_rows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, 
                     "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rows_to_ranks = {v : k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, 
                     "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, is_castle_move = False) :
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col] # piece_captured can be "--" to represent nothing was captured

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.is_pawn_promotion = ((self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7))
        
        self.is_enpassant_move = is_enpassant_move
        if is_enpassant_move :
            self.piece_captured = board[self.start_row][self.end_col]
        # castle move
        self.is_castle_move = is_castle_move

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
    def __str__(self) :
        if self.is_castle_move :
            return "O-O" if self.end_col == 6 else "O-O-O"
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
    Helper method for printing moves
    '''
    def get_rank_file(self, r, c) :
        return self.cols_to_files[c] + self.rows_to_ranks[r]