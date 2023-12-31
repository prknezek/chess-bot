from random import randint, shuffle

piece_score = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}

knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]]

queen_scores = [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rook_scores = [ [4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

white_pawn_scores =[[10, 10, 10, 10, 10, 10, 10, 10],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_scores =[[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [10, 10, 10, 10, 10, 10, 10, 10]]
    

piece_position_scores = {"N" : knight_scores, "B" : bishop_scores, "R" : rook_scores,
                         "Q" : queen_scores, "bp" : black_pawn_scores, "wp" : white_pawn_scores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

'''
Picks and returns a random move
'''
def find_random_move(valid_moves) :
    return valid_moves[randint(0, len(valid_moves) - 1)]
    # turn_multiplier = 1 if gs.white_to_move else -1
    # opponent_minmax_score = CHECKMATE # from black's perspective, checkmate is the worst possible score
    # best_player_move = None
    # shuffle(valid_moves)

    # for player_move in valid_moves :
    #     gs.make_move(player_move)
    #     opponents_moves = gs.get_valid_moves()

    #     if gs.check_mate :
    #         opponent_max_score = -CHECKMATE
    #     elif gs.stale_mate :
    #         opponent_max_score = STALEMATE
    #     else :
    #         opponent_max_score = -CHECKMATE
    #         for opponent_move in opponents_moves :
    #             gs.make_move(opponent_move)
    #             gs.get_valid_moves()
    #             if gs.check_mate :
    #                 score = CHECKMATE
    #             elif gs.stale_mate :
    #                 score = STALEMATE
    #             else :
    #                 score = -turn_multiplier * score_material(gs.board)
                
    #             if score > opponent_max_score :
    #                 opponent_max_score = score
    #             gs.undo_move()

    #     if opponent_max_score < opponent_minmax_score :
    #         opponent_minmax_score = opponent_max_score
    #         best_player_move = player_move
    #     gs.undo_move()

    # return best_player_move

'''
Helper method to make the first recursive call to find the best move
'''
def find_best_move(gs, valid_moves) :
    global next_move
    next_move = None
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return next_move

'''
Find the best move using the nega max alpha beta pruning algorithm
'''
def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier) :
    global next_move
    if depth == 0 :
        return turn_multiplier * score_board(gs)

    # move ordering - implement later
    max_score = -CHECKMATE
    for move in valid_moves :
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score :
            max_score = score
            if depth == DEPTH :
                next_move = move
        gs.undo_move()

        if max_score > alpha : # PRUNING
            alpha = max_score
        if alpha >= beta :
            break
    return max_score

'''
A Positive score is good for white, a negative score is good for black
'''
def score_board(gs) :
    if gs.check_mate :
        if gs.white_to_move :
            return -CHECKMATE # black wins
        else :
            return CHECKMATE # white wins
    elif gs.stale_mate :
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)) :
        for col in range(len(gs.board[row])) :
            square = gs.board[row][col]
            if square != '--' :
                piece_position_score = 0
                # score it positionally
                if square[1] != "K" : # no position table for king
                    if square[1] == 'p' : # for pawns
                        piece_position_score = piece_position_scores[square][row][col]
                    else : # for other pieces
                        piece_position_score = piece_position_scores["N"][row][col]

                if square[0] == 'w' :
                    score += piece_score[square[1]] + piece_position_score * .1
                elif square[0] == 'b' :
                    score -= piece_score[square[1]] + piece_position_score * .1

    return score