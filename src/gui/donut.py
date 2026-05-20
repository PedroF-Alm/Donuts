import pygame
from pathlib import Path

class Donut(pygame.sprite.Sprite):

    DONUT_PLAYER_ONE = 0
    DONUT_PLAYER_TWO = 1

    def __init__(self, size: tuple, player: int, *groups, pos: tuple):
        super().__init__(*groups)
        script_dir = Path(__file__).resolve().parent

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.owner = player        
        self.background1 = pygame.image.load(f'{script_dir}/../../assets/images/donut1.webp')
        self.background2 = pygame.image.load(f'{script_dir}/../../assets/images/donut2.webp')        
        self.background1 = pygame.transform.scale(self.background1, size)
        self.background2 = pygame.transform.scale(self.background2, size)
        if player == Donut.DONUT_PLAYER_ONE:
            self.image.blit(self.background1, (0, 0))
        if player == Donut.DONUT_PLAYER_TWO:
            self.image.blit(self.background2, (0, 0))            
        self.rect = self.image.get_rect(center=pos)     
    
    def change_owner(self, owner) -> None:
        self.owner = owner
        if owner == Donut.DONUT_PLAYER_ONE:
            self.image.blit(self.background1, (0, 0))
        if owner == Donut.DONUT_PLAYER_TWO:
            self.image.blit(self.background2, (0, 0))            