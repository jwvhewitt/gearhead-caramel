import pygame

import gears
import pbge

LEFT_COLUMN = pbge.frects.Frect(-300, 0, 200, 200)
CENTER_COLUMN = pbge.frects.Frect(-72, -200, 225, 400)
RIGHT_COLUMN = pbge.frects.Frect(175, -215, 200, 430)

UTIL_INFO = pbge.frects.Frect(-50, -200, 300, 200)
UTIL_MENU = pbge.frects.Frect(-50, 50, 300, 150)

RIGHT_INFO = pbge.frects.Frect(175, -200, 200, 150)
RIGHT_MENU = pbge.frects.Frect(175, -20, 200, 170)


class MechasPilotBlock(object):
    # There should be an apostrophe in there, but y'know...
    def __init__(self, model, camp, font=None, width=220, **kwargs):
        self.model = model
        self.camp = camp
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        pilot = self.model.pilot
        if pilot not in self.camp.party:
            self.model.pilot = None
            pilot = None
        if not pilot and hasattr(self.model, "owner") and self.model.owner:
            self.image = pbge.render_text(self.font, 'Owner: {}'.format(str(self.model.owner)), self.width,
                                          justify=-1, color=pbge.INFO_HILIGHT)
        else:
            self.image = pbge.render_text(self.font, 'Pilot: {}'.format(str(pilot)), self.width, justify=-1,
                                          color=pbge.INFO_HILIGHT)

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class ItemsOwnerBlock(object):
    # There should be an apostrophe in there, but y'know...
    def __init__(self, model, camp, font=None, width=220, **kwargs):
        self.model = model
        self.camp = camp
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        if self.image:
            self.height = self.image.get_height()
        else:
            self.height = 0

    def update(self):
        if hasattr(self.model, "owner") and self.model.owner:
            self.image = pbge.render_text(self.font, 'Owner: {}'.format(str(self.model.owner)), self.width,
                                          justify=-1, color=pbge.INFO_HILIGHT)
        else:
            self.image = None

    def render(self, x, y):
        if self.image:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class PilotsMechaBlock(object):
    # There should be an apostrophe in there, but y'know...
    def __init__(self, model, camp, font=None, width=220, **kwargs):
        self.model = model
        self.camp = camp
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        mek = self.camp.get_pc_mecha(self.model)
        if mek:
            self.image = pbge.render_text(self.font, 'Mecha: {}'.format(mek.get_full_name()), self.width, justify=-1,
                                          color=pbge.INFO_HILIGHT)
        else:
            self.image = pbge.render_text(self.font, 'Mecha: None', self.width, justify=-1, color=pbge.INFO_HILIGHT)

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class TrainerBlock(object):
    # There should be an apostrophe in there, but y'know...
    def __init__(self, model: gears.base.Monster, camp, font=None, width=220, **kwargs):
        self.model = model
        self.camp = camp
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        msg = "Trainer: {}\nActive: {}".format(self.model.pet_data.trainer, self.model.pet_data.active)
        self.image = pbge.render_text(self.font, msg, self.width, justify=-1, color=pbge.INFO_HILIGHT)

    def render(self, x, y):
        self.update()
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class RenownBlock(object):
    def __init__(self, model: gears.base.Character, camp, font=None, width=220, **kwargs):
        self.model = model
        self.camp = camp
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        renown = self.model.renown
        if renown > 80:
            title = "Ace"
        elif renown > 60:
            title = "Elite"
        elif renown > 40:
            title = "Veteran"
        elif renown > 20:
            title = "Regular"
        elif renown >= 0:
            title = "Green"
        else:
            title = "Wangtta"
        msg = "Renown: {} ({})".format(title, renown)
        self.image = pbge.render_text(self.font, msg, self.width, justify=0, color=pbge.INFO_GREEN)

    def render(self, x, y):
        self.update()
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class CharaFHQIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (
    gears.info.FullNameBlock, gears.info.ModuleStatusBlock, PilotsMechaBlock, RenownBlock, gears.info.ExperienceBlock,
    gears.info.CharacterStatusBlock, gears.info.PrimaryStatsBlock, gears.info.InstalledCyberwaresBlock,
    gears.info.NonComSkillBlock, gears.info.CharacterTagsBlock)


class MechaFHQIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (
    gears.info.FullNameBlock, gears.info.ModuleStatusBlock, gears.info.DesignViabilityBlock, MechasPilotBlock,
    gears.info.MechaStatsBlock, gears.info.DescBlock)


class PetFHQIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.ModuleStatusBlock, TrainerBlock, gears.info.ExperienceBlock,
                      gears.info.CharacterStatusBlock, gears.info.PrimaryStatsBlock, gears.info.PetSkillBlock)


def create_item_fhq_ip(**keywords):
    base_ip = gears.info.get_longform_display(**keywords)
    owner_block = ItemsOwnerBlock(**keywords)
    base_ip.info_blocks.insert(2, owner_block)
    return base_ip


class AssignMechaIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.MechaFeaturesAndSpriteBlock)


class AssignPilotIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.CharaPortraitAndSkillsBlock)
