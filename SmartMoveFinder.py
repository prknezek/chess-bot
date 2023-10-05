from random import randint

def find_random_move(valid_moves) :
    return valid_moves[randint(0, len(valid_moves) - 1)]

def find_best_move() :
    return