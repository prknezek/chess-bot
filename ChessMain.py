'''
This is our main driver file. Responsible for handling user input and displaying the current GameState object
'''
import pygame as py
import ChessEngine, SmartMoveFinder

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
Highlight the square selected and moves for the piece selected
'''
def highlight_squares(screen, gs, valid_moves, selected_sq, move_log) :
    s = py.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(150) # transparency -> 0 transparent; 255 opaque
    s.fill(py.Color(222, 222, 82))
    # highlight where the last move was to
    if len(move_log) > 0 :
        screen.blit(s, (move_log[-1].end_col * SQ_SIZE, move_log[-1].end_row * SQ_SIZE))
    if selected_sq != () :
        r, c = selected_sq
        # make sure the square selected is a piece that can be moved
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b') :
            # highlight the selected square
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.set_alpha(100)
            s.fill(py.Color(246,246,130))
            for move in valid_moves :
                if move.start_row == r and move.start_col == c :
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

'''
Responsible for all the graphics within a current game state
'''
def draw_game_state(screen, gs, valid_moves, selected_sq) :
    draw_board(screen) # draw the squares on the board
    highlight_squares(screen, gs, valid_moves, selected_sq, gs.move_log)
    draw_pieces(screen, gs.board) # draw the pieces on top of the squares

'''
Draw the squares on the board. The top left square is always light
'''
def draw_board(screen) :
    global colors
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
Animating a move
'''
def animate_move(move, screen, board, clock) :
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frame_count = 10 # frames to make a move
    for frame in range(frame_count + 1) :
        r, c = (move.start_row + dR * (frame / frame_count), 
                       move.start_col + dC * (frame / frame_count))
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = py.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        py.draw.rect(screen, color, end_square)
        # draw captured piece back
        if move.piece_captured != '--' :
            if move.is_enpassant_move :
                enpassant_row = (move.end_row + 1) if move.piece_captured[0] == 'b' else (move.end_row - 1)
                end_square = py.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw the moving piece
        if move.piece_moved != '--' :
            screen.blit(IMAGES[move.piece_moved], py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(60)

'''
Draws text for the end screen
'''
def draw_text(screen, text) :
    font = py.font.SysFont('monospace', 32, True, False)
    text_object = font.render(text, 0, py.Color('White'))
    text_location = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width() / 2,
                                                      HEIGHT/2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, py.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))

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
    animate = False # flag variable for when we should animate a move

    load_images() # only do this once before the while loop
    running = True
    selected_sq = () # tuple : (row, col)
    player_clicks = [] # keep track of player clicks (two tuples : [(6, 4), (4, 4)])
    game_over = False
    player_one = True # If a human is playing white, then this will be True. If an AI is playing, then false
    player_two = True # Same as above but for black

    while running :
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in py.event.get() :
            if e.type == py.QUIT :
                running = False
            # mouse handling
            elif e.type == py.MOUSEBUTTONDOWN :
                if not game_over and human_turn : # can only play if the game isn't done (checkmate/stalemate)
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
                        for i in range(len(valid_moves)) :
                            if move == valid_moves[i] :
                                print(move.get_chess_notation())
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_sq = ()
                                player_clicks = []
                        if not move_made : # instead of resetting clicks we change pieces
                            player_clicks = [selected_sq]
            # key handling
            elif e.type == py.KEYDOWN :
                if e.key == py.K_z : # undo move when z pressed
                    game_over = False
                    animate = False
                    gs.undo_move()
                    move_made = True
                if e.key == py.K_r : # reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = animate = game_over = False
                if e.key == py.K_p : # pause the game
                    pause = True
                    while pause :
                        for e in py.event.get() :
                            if e.type == py.KEYDOWN :
                                if e.key == py.K_p :
                                    pause = False
                                    break
                            if e.type == py.QUIT :
                                pause = False
                                running = False
                                break

        # AI move finder
        if not game_over and not human_turn :
            AI_move = SmartMoveFinder.find_best_move(gs, valid_moves)
            if AI_move == None :
                AI_move = SmartMoveFinder.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True
            animate = True

        if move_made :
            if len(gs.move_log) > 0 :
                if not gs.move_log[-1].is_castle_move and animate :
                    animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, selected_sq)

        if gs.check_mate :
            game_over = True
            if gs.white_to_move :
                draw_text(screen, "Black wins by checkmate")
            else :
                draw_text(screen, "White wins by checkmate")
        elif gs.stale_mate :
            game_over = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        py.display.flip()

if __name__ == "__main__" :
    main()