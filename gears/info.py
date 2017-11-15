import base
import pbge
import pygame

class ModuleDisplay( object ):
    # The dest area should be 60x50.
    # Increasing the width is okay, but the height is set in stone.
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
    def __init__( self, dest, model ):
        self.dest = dest
        self.model = model
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
        my_modules.render( self.module_dest, self.part_struct_frame( module ) )
        armor = module.get_armor()
        if armor:
            my_modules.render( self.module_dest, self.part_armor_frame( module, armor ) )
        self.module_num += 1

    def add_parts_of_type( self, mod_form ):
        for module in self.model.sub_com:
            if hasattr( module, "form" ) and module.form is mod_form and module.info_tier is None:
                self.draw_this_part( module )

    def add_parts_of_tier( self, mod_tier ):
        for module in self.model.sub_com:
            if hasattr( module, "form" ) and module.info_tier == mod_tier:
                self.draw_this_part( module )

    def render( self ):
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


class MechaStatusDisplay( object ):
    # A floating status display, drawn wherever the mouse is pointing.
    def __init__( self, dest, model ):
        myrect = pygame.Rect(0,0,220,150)
        myrect.midbottom = dest
        self.dest = myrect
        self.model = model
        self.module_display = ModuleDisplay(pygame.Rect(myrect.centerx-30,myrect.y+16,60,50),model)
        self.render()
    def render( self ):
        pbge.default_border.render(self.dest)
        pbge.draw_text(BIGFONT, str(self.model), self.dest, justify=0)
        self.module_display.render()
        mydest = self.dest.copy()
        mydest.y += 70
        pbge.draw_text(pbge.SMALLFONT, str(self.model.get_pilot()), mydest, justify=-1)
        mydest.y += 12
        pbge.draw_text(pbge.SMALLFONT, 'Speed: {}'.format(str(self.model.get_current_speed())), mydest, justify=-1)

