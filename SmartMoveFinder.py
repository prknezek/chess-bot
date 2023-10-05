from random import randint, shuffle

piece_score = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0

'''
Picks and returns a random move
'''
def find_random_move(valid_moves) :
    return valid_moves[randint(0, len(valid_moves) - 1)]

'''
Finds the best move based on material alone
'''
def find_best_move(gs, valid_moves) :
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_minmax_score = CHECKMATE # from black's perspective, checkmate is the worst possible score
    best_player_move = None
    shuffle(valid_moves)

    for player_move in valid_moves :
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()

        if gs.check_mate :
            opponent_max_score = -CHECKMATE
        elif gs.stale_mate :
            opponent_max_score = STALEMATE
        else :
            opponent_max_score = -CHECKMATE
            for opponent_move in opponents_moves :
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.check_mate :
                    score = CHECKMATE
                elif gs.stale_mate :
                    score = STALEMATE
                else :
                    score = -turn_multiplier * score_material(gs.board)
                
                if score > opponent_max_score :
                    opponent_max_score = score
                gs.undo_move()

        if opponent_max_score < opponent_minmax_score :
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()

    return best_player_move

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

