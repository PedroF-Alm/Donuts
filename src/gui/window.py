
def start_gui(grid, gui_input_queue, gui_output_queue):

    import pygame
    from gui.state import State
    from gui.board import Board
    from gui.square import Square        
    from pathlib import Path
    
    script_dir = Path(__file__).resolve().parent

    def create_board(board_size: tuple, tray_size: tuple, state: State) -> tuple[Board, pygame.rect.Rect, tuple]:
        board = Board(size=board_size, tray_size=tray_size, game=state)
        board_rect = board.get_rect() 
        board_rect.center = (screen_width // 2, screen_height // 2)
        board_offset = board_rect.topleft
        return (board, board_rect, board_offset)                
    

    state = State()
    state.grid = grid

    pygame.init()

    pygame.mixer.init()
    pygame.mixer.music.load(f'{script_dir}/../../assets/sounds/songs/music.ogg')
    # pygame.mixer.music.play(-1)

    roundstart_sfx = pygame.mixer.Sound(f'{script_dir}/../../assets/sounds/sfx/roundstart.ogg')

    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))

    background = pygame.image.load(f'{script_dir}/../../assets/images/background.webp')
    background = pygame.transform.scale(background, (screen_width, screen_height)).convert()
    screen.blit(background, (0, 0))

    icon = pygame.image.load(f'{script_dir}/../../assets/images/donut1.webp')
    icon = pygame.transform.scale(icon, (32, 32))

    pygame.display.set_caption("Donuts")
    pygame.display.set_icon(icon)

    board_size = (471, 511)
    tray_size = (80, 472)

    board, board_rect, board_offset = create_board(board_size, tray_size, state)

    clock = pygame.time.Clock() 

    roundstart_sfx.play(0)

    running = True
    while running:

        while not gui_input_queue.empty():
            msg_type, data = gui_input_queue.get_nowait()
            if msg_type == 'UPDATE':                             
                state.grid, state.turn, state.winner, state.end, state.player_rings = data 
                board, board_rect, board_offset = create_board(board_size, tray_size, state)                                           

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gui_output_queue.put(('QUIT', None))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                
                clicked_square: Square = board.handle_click(event.pos, board_offset)
                if clicked_square is not None and not clicked_square.disabled:
                    gui_output_queue.put(('CLICK', clicked_square.id))               

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_z:                                    
                    gui_output_queue.put(('UNDO', None))                    
                       
        board.update()

        screen.blit(board, board_rect)

        screen.blit(board.tray1, (board_rect.centerx - 471 // 2 - tray_size[0] - 20, 85))
        screen.blit(board.tray2, (board_rect.centerx + 471 // 2 + 20, 85))    

        if state.end:
            font = pygame.font.SysFont(None, 40)
            if state.winner is None:
                text_surface = font.render(f"TIE!", True, (222, 130, 245), (255, 255, 255))                
            else:
                text_surface = font.render(f"PLAYER {'ONE' if state.winner == State.PLAYER_ONE else 'TWO'} WON!", True, (222, 130, 245), (255, 255, 255))                
            text_rect = text_surface.get_rect(center=(400, 300))                
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(8, 8), 8)        
            screen.blit(text_surface, text_rect)

        pygame.display.flip() 
        
        clock.tick(60) 

    pygame.quit()