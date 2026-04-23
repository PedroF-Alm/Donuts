import pygame
from gui.square import Square
from gui.tray import Tray
from gui.donut import Donut
from core.game import Game

class Board(pygame.Surface):

    def __init__(self, size: tuple, tray_size: tuple, game: Game, flags: int = pygame.SRCALPHA) -> None:
        super().__init__(size, flags)
        self.game = game
        
        try:
            self.background = pygame.image.load('../assets/images/boardback.webp').convert_alpha()
            self.background = pygame.transform.scale(self.background, size)
            self.blit(self.background, (0, 0))
        except pygame.error:
            print("Aviso: Imagem de fundo não encontrada. Usando fundo transparente.")
        
        self.squares_group = pygame.sprite.Group()
        
        square_dim = (size[0] // 7, size[0] // 7)
        margin_x = 40
        margin_y = 85
        spacing = 10

        for i in range(36):
            col = i % 6
            row = i // 6
            
            x = margin_x + (square_dim[0] + spacing) * col
            y = margin_y + (square_dim[0] + spacing) * row
            
            new_square = Square(size=square_dim, id=i, mirror=game.grid[i], pos=(x, y))
            new_square.board = self            
                    
            self.squares_group.add(new_square)

        self.tray_size = tray_size

        self.tray1 = Tray(tray_size, Donut.DONUT_PLAYER_ONE, game.player_rings[0])
        self.tray2 = Tray(tray_size, Donut.DONUT_PLAYER_TWO, game.player_rings[1])           
            
        self.squares_group_list = self.squares_group.sprites()

    def draw_squares(self) -> None:
        self.squares_group.draw(self)
        for square in self.squares_group.sprites():
            square.draw_donut()

    def update_squares(self) -> None:
        self.blit(self.background, (0, 0)) 
        self.squares_group.update()

    def update_trays(self) -> None:
        self.tray1.draw_donuts()
        self.tray2.draw_donuts()

    def update(self) -> None:
        self.update_squares() 
        self.draw_squares()   
        self.update_trays()

    def place_donut(self, square: Square) -> None:
        if self.game.place_ring(square.id % 6, square.id // 6):            
            if self.game.turn == Game.PLAYER_TWO:
                self.tray1.place_donut(square)      
            elif self.game.turn == Game.PLAYER_ONE:
                self.tray2.place_donut(square)      

    def handle_click(self, mouse_pos: tuple, board_offset: tuple = (0, 0)) -> Square | None:
            
            # Ajusta a posição do mouse para o sistema de coordenadas do Board
            adjusted_pos = (mouse_pos[0] - board_offset[0], mouse_pos[1] - board_offset[1])

            for square in self.squares_group:
                if square.rect.collidepoint(adjusted_pos):                                        
                    return square
            return None