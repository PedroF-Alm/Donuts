import pygame
import sys
from time import sleep
from core.game import Game
from gui.board import Board
from gui.square import Square
from gui.tray import Tray
from gui.donut import Donut

if __name__ != '__main__':
    print("main.py deve ser o arquivo principal.")
    exit(1)

def create_board(board_size: tuple, tray_size: tuple, game: Game) -> tuple[Board, pygame.rect.Rect, tuple]:
    board = Board(size=board_size, tray_size=tray_size, game=game)
    board_rect = board.get_rect() 
    board_rect.center = (screen_width // 2, screen_height // 2)
    board_offset = board_rect.topleft
    return (board, board_rect, board_offset)

seed = 1
game = Game(seed=seed)

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load('../assets/sounds/songs/music.ogg')
pygame.mixer.music.play(-1)

roundstart_sfx = pygame.mixer.Sound('../assets/sounds/sfx/roundstart.ogg')

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

background = pygame.image.load('../assets/images/background.webp')
background = pygame.transform.scale(background, (screen_width, screen_height)).convert()
screen.blit(background, (0, 0))

icon = pygame.image.load('../assets/images/donut1.webp')
icon = pygame.transform.scale(icon, (32, 32))

pygame.display.set_caption("Donuts")
pygame.display.set_icon(icon)

board_size = (471, 511)
tray_size = (80, 472)

board, board_rect, board_offset = create_board(board_size, tray_size, game)

clock = pygame.time.Clock() 

roundstart_sfx.play(0)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Detecta qual quadrado foi clicado
            clicked_square: Square = board.handle_click(event.pos, board_offset)
            if clicked_square is not None and not clicked_square.disabled:
                board.place_donut(clicked_square)

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_z:                
                last_state = game.last_state()
                if last_state:
                    board, board_rect, board_offset = create_board(board_size, tray_size, game)

            if game.end and event.key == pygame.K_SPACE:
                seed += 1
                game = Game(seed=seed)

                board, board_rect, board_offset = create_board(board_size, tray_size, game)                

    board.update()

    screen.blit(board, board_rect)

    screen.blit(board.tray1, (board_rect.centerx - 471 // 2 - tray_size[0] - 20, 85))
    screen.blit(board.tray2, (board_rect.centerx + 471 // 2 + 20, 85))    

    if game.end:
        font = pygame.font.SysFont(None, 40)
        if game.winner is None:
            text_surface = font.render(f"TIE!", True, (222, 130, 245), (255, 255, 255))                
        else:
            text_surface = font.render(f"PLAYER {'ONE' if game.winner == Game.PLAYER_ONE else 'TWO'} WON!", True, (222, 130, 245), (255, 255, 255))                
        text_rect = text_surface.get_rect(center=(400, 300))                
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(8, 8), 8)        
        screen.blit(text_surface, text_rect)

    pygame.display.flip() 
    
    clock.tick(60) 

pygame.quit()
sys.exit()
