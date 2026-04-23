import pygame
from core.slot import Slot
from gui.donut import Donut

class Square(pygame.sprite.Sprite):
    
    def __init__(self, size: tuple, id: int, mirror: Slot, pos: tuple = (0, 0)) -> None:
        super().__init__()

        self.id = id
        self.pos = pos

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.background = pygame.image.load('../assets/images/bars.webp').convert_alpha()
        self.background = pygame.transform.scale(self.background, (564 / 2, 282 / 2))

        self.direction = mirror.direction
        self.bg_offsetx = -70 * (mirror.direction % 4)                

        self.image.blit(self.background, (self.bg_offsetx, 0))           
        self.rect = self.image.get_rect(center=self.pos)
        self.board = None

        self.disabled = False
        self.highlighted = False
        
        self.mirror = mirror
        self.donut = pygame.sprite.GroupSingle()        

        if self.mirror.ring is not None and self.donut.sprite is None:
                donut = Donut((70, 70), self.mirror.ring.owner, pos=(0,0))
                donut.rect = self.rect
                self.donut.add(donut)

    def draw_donut(self) -> None:
        if self.donut.sprite != None:
            self.donut.draw(self.board)

    def disable(self) -> None:  
        if self.mirror.direction == Slot.FIRST_DIAGONAL:   
            rotated_background = pygame.transform.rotate(self.background.copy(), 180)                 
            self.image.blit(rotated_background, (-70 * (3 - Slot.FIRST_DIAGONAL), 0))
        else:
            self.image.blit(self.background, (self.bg_offsetx, -70))    
        self.rect = self.image.get_rect(center=self.pos)    
        self.disabled = True

    def enable(self) -> None:              
        self.image.blit(self.background, (self.bg_offsetx, 0))    
        self.rect = self.image.get_rect(center=self.pos)  
        self.disabled = False

    def update(self) -> None:   
        if self.mirror.ring is not None and self.mirror.ring.owner != self.donut.sprite.owner:      
            self.donut.sprite.change_owner(self.mirror.ring.owner)
        if self.mirror.blocked and not self.disabled:
            self.disable()
        elif not self.mirror.blocked and self.disabled:
            self.enable()
        if self.mirror.marked and not self.highlighted:            
            tint_color = (255, 0, 0, 128) 
            highlighted_bg = self.background.copy()
            highlighted_bg.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)   
            self.image.blit(highlighted_bg, (self.bg_offsetx, 0))    
            self.rect = self.image.get_rect(center=self.pos)    
            self.highlighted = True  
        elif not self.mirror.marked:
            self.highlighted = False
        
