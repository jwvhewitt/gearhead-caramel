import base
import pbge
import pygame

class InfoPanel( object ):
    # An InfoPanel contains a bunch of InfoBlocks which get arranged vertically.
    # Each InfoBlock needs a width, height, and render(x,y)
    DEFAULT_BLOCKS = list()
    def __init__(self,padding=3,**kwargs):
        self.padding = padding
        self.info_blocks = list()
        for b in self.DEFAULT_BLOCKS:
            self.info_blocks.append(b(**kwargs))

    def get_dimensions( self ):
        width = 0
        height = -self.padding
        for block in self.info_blocks:
            width = max(block.width,width)
            height += block.height + self.padding
        return width,height

    def render( self, x, y ):
        w,h = self.get_dimensions()
        pbge.default_border.render(pygame.Rect(x,y,w,h))
        for block in self.info_blocks:
            block.render(x,y)
            y += block.height + self.padding

class NameBlock( object ):
    def __init__(self,model,width=220,**kwargs):
        self.model = model
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT,str(model),width,justify=0)
        self.height = self.image.get_height()
    def render(self,x,y):
        pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))

class ListBlock( object ):
    def __init__(self,items,width=220,**kwargs):
        self.items = items
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT,'\n'.join([str(i) for i in items]),width,justify=-1)
        self.height = self.image.get_height()
    def render(self,x,y):
        pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))

class ModuleStatusBlock( object ):
    # This block contains both the module display and the Armor/Mobility displays.
    def __init__(self,model,width=220,**kwargs):
        self.model = model
        self.width = width
        self.height = 50
        self.module_display = ModuleDisplay(model)
        self.am_sprite = pbge.image.Image('sys_armormobility.png',40,50)
    def render(self,x,y):
        mydest = pygame.Rect(x,y,40,50)
        self.am_sprite.render(mydest,0)
        textdest = pygame.Rect(mydest.x + 5, mydest.y + 10, 30, 16 )
        pbge.draw_text(pbge.BIGFONT, str(self.model.calc_average_armor()), textdest, justify=0)
        mydest.right = x+self.width
        self.am_sprite.render(mydest,1)
        textdest = pygame.Rect(mydest.x + 5, mydest.y + 10, 30, 16 )
        pbge.draw_text(pbge.BIGFONT, str(self.model.calc_mobility()), textdest, justify=0)
        self.module_display.render(x+self.width//2-30,y)

class PilotStatusBlock( object ):
    # Holds details on the pilot.
    def __init__(self,model,width=220,**kwargs):
        if model:
            self.model = model.get_pilot()
            self.mover = model
        else:
            self.model = None
        self.width = width
        self.height = max(pbge.SMALLFONT.get_linesize(),12)
        self.power_sprite = pbge.image.Image('sys_powerindicator.png',32,12)

    def render(self,x,y):
        pbge.draw_text(pbge.SMALLFONT, str(self.model), pygame.Rect(x,y,self.width,self.height), justify=-1)
        if self.model:
            pbge.draw_text(pbge.SMALLFONT, 'H:{}'.format(self.model.current_health), pygame.Rect(x+83,y,35,self.height,justify=0))
            pbge.draw_text(pbge.SMALLFONT, 'M:{}'.format(self.model.get_current_mental()), pygame.Rect(x+118,y,35,self.height,justify=0))
            pbge.draw_text(pbge.SMALLFONT, 'S:{}'.format(self.model.get_current_stamina()), pygame.Rect(x+153,y,35,self.height,justify=0))

            cp,mp = self.mover.get_current_and_max_power()
            if mp > 0:
                mydest = self.power_sprite.get_rect(0)
                mydest.midright = (x + self.width, y + self.height//2)
                self.power_sprite.render(mydest,10-max(cp*10//mp,1))

class OddsInfoBlock( object ):
    def __init__(self,odds,modifiers,width=220,**kwargs):
        self.odds = odds
        self.modifiers = modifiers
        self.modifiers.sort(key = lambda x: -abs(x[0]))
        self.width = width
        self.height = pbge.SMALLFONT.get_linesize() * 3
    def render(self,x,y):
        pbge.draw_text(pbge.my_state.huge_font, '{}%'.format(int(self.odds*100)), pygame.Rect(x,y,75,32),justify=0)
        pbge.draw_text(pbge.my_state.big_font, 'TO HIT', pygame.Rect(x,y+pbge.my_state.huge_font.get_linesize(),75,32),justify=0)
        t = 0
        for mymod in self.modifiers:
            pbge.draw_text(pbge.my_state.small_font, '{:+d}: {}'.format(int(mymod[0]),mymod[1]), pygame.Rect(x+80,y+t*pbge.SMALLFONT.get_linesize(),self.width-80,32),justify=-1)
            t += 1
            if t > 2:
                break


class ModuleDisplay( object ):
    # The dest area should be 60x50.
    MODULE_FORM_FRAME_OFFSET = {
            base.MF_Torso:   0,
            base.MF_Head:    9,
            base.MF_Arm:     18,
            base.MF_Leg:     27,
            base.MF_Wing:    36,
            base.MF_Tail:    45,
            base.MF_Turret:  54,
            base.MF_Storage: 63,
        }
    def __init__( self, model ):
        self.model = model
        self.module_sprite = pbge.image.Image('sys_modules.png',16,16)

    def part_struct_frame( self, module ):
        if module.is_destroyed():
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form,0) + 8
        else:
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form,0) + min((module.get_damage_status()+5)/14, 7 )
    def part_armor_frame( self, module, armor ):
        if armor.is_destroyed():
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form,0) + 80
        else:
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form,0) + 72 + min((armor.get_damage_status()+5)/14, 7 )

    def draw_this_part( self, module ):
        if (self.module_num % 2 ) == 1:
            self.module_dest.centerx = self.dest.centerx - 12 * self.module_num//2 - 6
        else:
            self.module_dest.centerx = self.dest.centerx + 12 * self.module_num//2
        self.module_sprite.render( self.module_dest, self.part_struct_frame( module ) )
        armor = module.get_armor()
        if armor:
            self.module_sprite.render( self.module_dest, self.part_armor_frame( module, armor ) )
        self.module_num += 1

    def add_parts_of_type( self, mod_form ):
        for module in self.model.sub_com:
            if hasattr( module, "form" ) and module.form is mod_form and module.info_tier is None:
                self.draw_this_part( module )

    def add_parts_of_tier( self, mod_tier ):
        for module in self.model.sub_com:
            if hasattr( module, "form" ) and module.info_tier == mod_tier:
                self.draw_this_part( module )

    def render( self, x, y ):
        self.dest = pygame.Rect(x,y,60,50)
        self.module_dest = pygame.Rect(self.dest.x,self.dest.y,16,16)

        self.module_num = 0
    	self.add_parts_of_type( base.MF_Head );
    	self.add_parts_of_type( base.MF_Turret );
        self.module_num = max(self.module_num,1) # Want pods to either side of body; head and/or turret in middle.
    	self.add_parts_of_type( base.MF_Storage );
        self.add_parts_of_tier( 1 )

        self.module_num = 0
        self.module_dest.y += 17
    	self.add_parts_of_type( base.MF_Torso );
    	self.add_parts_of_type( base.MF_Arm );
    	self.add_parts_of_type( base.MF_Wing );
        self.add_parts_of_tier( 2 )

        self.module_num = 0
        self.module_dest.y += 17
    	self.add_parts_of_type( base.MF_Tail );
        self.module_num = max(self.module_num,1) # Want legs to either side of body; tail in middle.
    	self.add_parts_of_type( base.MF_Leg );
        self.add_parts_of_tier( 3 )


class MechaStatusDisplay( InfoPanel ):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (NameBlock,ModuleStatusBlock,PilotStatusBlock)

class ListDisplay( InfoPanel ):
    DEFAULT_BLOCKS = (ListBlock,)


