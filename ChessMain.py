# Chess Main File

import pygame
from pygame.locals import *
from pygame.time import Clock
from pygame.math import Vector2
import sys

from chess.ChessEngine import GameState, Move

# Initialize pygame
pygame.init()

# screen settings
WIDTH = 512
HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION

# game settings
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))

# Main driver function
def main():
    # Create screen and clock objects
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = Clock()

    screen.fill(pygame.Color("white"))

    # Create game state object
    gs = GameState()

    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable for when a move is mad


    # Load images
    load_images()

    square_selected = () # no square is selected initially
    player_clicks = [] # keep track of player clicks

    # Main game loop
    while True:
        # event loop
        for event in pygame.event.get():
            # event handler
            if event.type == pygame.QUIT:
                sys.exit()

            # mouse handler
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if square_selected == (row, col): # user clicked same square twice
                    square_selected = () # unselect
                    player_clicks = [] # clear the player clicks
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)

                if len(player_clicks) == 2: # after 2nd click
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                        square_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [square_selected]

            # key handlers
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick()
        pygame.display.flip()

# Draws all graphics
def draw_game_state(screen, gs):
    draw_board(screen)

    draw_pieces(screen, gs.board)

# Draws the squares on the board
def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color,
                             pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE,
                                        SQUARE_SIZE, SQUARE_SIZE))

# Draw the pieces on the board
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not an empty square
                screen.blit(IMAGES[piece],
                            pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE,
                                        SQUARE_SIZE, SQUARE_SIZE))

if __name__ == "__main__":
    main()
