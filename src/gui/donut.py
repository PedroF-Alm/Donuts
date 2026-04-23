import pygame

class Donut(pygame.sprite.Sprite):

    DONUT_PLAYER_ONE = 0
    DONUT_PLAYER_TWO = 1

    def __init__(self, size, player, *groups, pos):
        super().__init__(*groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.owner = player        
        self.background1 = pygame.image.load('../assets/images/donut1.webp')
        self.background2 = pygame.image.load('../assets/images/donut2.webp')        
        self.background1 = pygame.transform.scale(self.background1, size)
        self.background2 = pygame.transform.scale(self.background2, size)
        if player == Donut.DONUT_PLAYER_ONE:
            self.image.blit(self.background1, (0, 0))
        if player == Donut.DONUT_PLAYER_TWO:
            self.image.blit(self.background2, (0, 0))            
        self.rect = self.image.get_rect(center=pos)     
    
    def change_owner(self, owner):
        self.owner = owner
        if owner == Donut.DONUT_PLAYER_ONE:
            self.image.blit(self.background1, (0, 0))
        if owner == Donut.DONUT_PLAYER_TWO:
            self.image.blit(self.background2, (0, 0))            