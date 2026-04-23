import pygame
from gui.donut import Donut
from gui.square import Square

class Tray(pygame.Surface):

    def __init__(self, size, owner, donuts_count = 15, flags: int = pygame.SRCALPHA):
        super().__init__(size, flags)
        # self.size = size
        pygame.draw.rect(self, (255, 255, 255), (0, 0, size[0], size[1]), border_radius=50)
        self.set_alpha(120)
        self.donuts_group = pygame.sprite.Group()
        self.donuts_count = donuts_count
        for i in range(donuts_count):
            self.donuts_group.add(Donut((70, 70), owner, pos=(size[0] / 2, 28 * i + 40)))     
    
    def draw_donuts(self):
        self.donuts_group.draw(self)

    def place_donut(self, square: Square) -> None:
        if self.donuts_group.sprites():
            donut_2_place: Donut = self.donuts_group.sprites()[-1]     
            donut_2_place.rect = square.rect
            square.donut.add(donut_2_place) 
            self.donuts_group.remove(donut_2_place)            
            pygame.draw.rect(self, (255, 255, 255), (0, 0, self.size[0], self.size[1]), border_radius=50)
            self.draw_donuts()        
        
        