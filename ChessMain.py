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
    colors = [py.Color("light gray"), py.Color("dark green")]
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
    load_images() # only do this once before the while loop
    running = True

    while running :
        for e in py.event.get() :
            if e.type == py.QUIT :
                running = False
            elif e.type == py.MOUSEBUTTONDOWN :
                location = py.mouse.get_pos() # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        py.display.flip()

if __name__ == "__main__" :
    main()