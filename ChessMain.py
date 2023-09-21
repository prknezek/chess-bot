'''
This is our main driver file. Responsible for handling user input and displaying the current GameState object
'''
import pygame as py
import ChessEngine

WIDTH = HEIGHT = 512 # 400 is another option
DIMENSION = 8 # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations
IMAGES = {}

'''
Initialize global dictionary of images. This will be called exactly once in the main
'''

def load_images() :
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces :
        IMAGES[piece] = py.transform.scale(py.image.load("./images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # We can access an image by saying 'IMAGES['wp']'

'''
Responsible for all the graphics within a current game state
'''
def draw_game_state(screen, gs) :
    draw_board(screen) # draw the squares on the board
    draw_pieces(screen, gs.board) # draw the pieces on top of the squares

'''
Draw the squares on the board. The top left square is always light
'''
def draw_board(screen) :
    colors = [py.Color(238,238,210), py.Color(118,150,86)]
    for rank in range(DIMENSION) :
        for file in range(DIMENSION) :
            color = colors[(rank + file) % 2]
            py.draw.rect(screen, color, py.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState board
'''
def draw_pieces(screen, board) :
    for rank in range(DIMENSION) :
        for file in range(DIMENSION) :
            piece = board[rank][file]

            if piece != "--" : # not an empty square
                screen.blit(IMAGES[piece], py.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Main driver for our code. This will handle user input and updating the graphics
'''

def main() :
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill(py.Color('white'))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable for when a move is made

    load_images() # only do this once before the while loop
    running = True
    selected_sq = () # tuple : (row, col)
    player_clicks = [] # keep track of player clicks (two tuples : [(6, 4), (4, 4)])


    while running :
        for e in py.event.get() :
            if e.type == py.QUIT :
                running = False
            # mouse handling
            elif e.type == py.MOUSEBUTTONDOWN :
                location = py.mouse.get_pos() # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if selected_sq == (row, col) : # user clicked the same sq twice (undo)
                    selected_sq = () # unselect the square
                    player_clicks = [] # clear the clicks
                else :
                    selected_sq = (row, col)
                    player_clicks.append(selected_sq)
                if len(player_clicks) == 2 :
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)

                    if move in valid_moves :
                        print(move.get_chess_notation())
                        gs.make_move(move)
                        move_made = True
                        selected_sq = ()
                        player_clicks = []
                    else : # instead of resetting clicks we change pieces
                        player_clicks = [selected_sq]
            # key handling
            elif e.type == py.KEYDOWN :
                if e.key == py.K_z : # undo move when z pressed
                    gs.undo_move()
                    move_made = True

        if move_made :
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        py.display.flip()

if __name__ == "__main__" :
    main()