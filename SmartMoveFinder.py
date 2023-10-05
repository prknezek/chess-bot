from random import randint, shuffle

piece_score = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

'''
Picks and returns a random move
'''
def find_random_move(valid_moves) :
    return valid_moves[randint(0, len(valid_moves) - 1)]

'''
Finds the best move based on material alone
'''
# def find_best_move(gs, valid_moves) :
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
    find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    return next_move

def find_move_minmax(gs, valid_moves, depth, white_to_move) :
    global next_move
    # base cases
    if depth == 0 :
        return score_board(gs.board)

    if white_to_move :
        max_score = -CHECKMATE
        for move in valid_moves :
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, False)
            if score > max_score :
                max_score = score
                if depth == DEPTH :
                    next_move = move
            gs.undo_move()
        return max_score
    else :
        min_score = CHECKMATE
        for move in valid_moves :
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, True)
            if score < min_score :
                min_score = score
                if depth == DEPTH :
                    next_move = move
            gs.undo_move()
        return min_score
            
def find_move_nega_max(gs, valid_moves, depth, turn_multiplier) :
    global next_move
    if depth == 0 :
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves :
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score :
            max_score = score
            if depth == DEPTH :
                next_move = move
        gs.undo_move()
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
    for row in gs.board :
        for square in row :
            if square[0] == 'w' :
                score += piece_score[square[1]]
            elif square[0] == 'b' :
                score -= piece_score[square[1]]
    
    return score

'''
Score the board based on material
'''
def score_material(board) :
    score = 0
    for row in board :
        for square in row :
            if square[0] == 'w' :
                score += piece_score[square[1]]
            elif square[0] == 'b' :
                score -= piece_score[square[1]]
    
    return score

