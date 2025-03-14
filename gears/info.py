from . import base
import pbge
import pygame
from . import stats


class InfoPanel(object):
    # An InfoPanel contains a bunch of InfoBlocks which get arranged vertically.
    # Each InfoBlock needs a width, height, and render(x,y)
    # An InfoPanel should not be stored in the campaign structure because it may contain pygame Surfaces, which
    #   can't be pickled! Instead create the info panel anew as needed.
    DEFAULT_BLOCKS = list()

    def __init__(self, padding=3, draw_border=True, view=None, view_pos=(0, 0), border_style=pbge.default_border,
                 **kwargs):
        self.padding = padding
        self.info_blocks = list()
        for b in self.DEFAULT_BLOCKS:
            self.info_blocks.append(b(**kwargs))
        self.draw_border = draw_border
        self.border_style = border_style
        self.view = view
        self.view_pos = view_pos

    def get_dimensions(self):
        width = 0
        height = -self.padding
        for block in self.info_blocks:
            width = max(block.width, width)
            height += block.height + self.padding
        return width, height

    def render(self, x, y):
        w, h = self.get_dimensions()
        if self.draw_border:
            self.border_style.render(pygame.Rect(x, y, w, h))
        for block in self.info_blocks:
            block.render(x, y)
            y += block.height + self.padding

    def update(self):
        for block in self.info_blocks:
            if hasattr(block, "update"):
                block.update()

    def popup(self, pos=None, anchor=None):
        w, h = self.get_dimensions()
        if pos:
            x, y = pos
        else:
            x, y = pbge.my_state.mouse_pos
        x -= w // 2
        y -= h + 64
        myrect = pygame.Rect(x, y, w, h)
        #        if anchor and hasattr(myrect, anchor):
        #            setattr(myrect, anchor, (x,y))
        myrect.clamp_ip(pbge.my_state.screen.get_rect())
        self.render(myrect.left, myrect.top)

    def view_display(self, camp):
        if not self.view:
            self.popup()
        else:
            w, h = self.get_dimensions()
            myrect = pygame.Rect(0, 0, w, h)
            if pbge.util.config.getboolean("GENERAL", "dock_tile_info_panel"):
                myrect.x = 16
                myrect.y = 16
                if camp.fight:
                    myrect.top += 64
            else:
                x, y = self.view.foot_coords(*self.view_pos)
                y -= 64
                myrect.midbottom = (x, y)
                myrect.clamp_ip(pbge.my_state.screen.get_rect())
            self.render(myrect.left, myrect.top)


class AbstractModelTextBlock(object):
    # Do not use this block on its own!!! Instead, subclass it and replace the get_text function with whatever
    # text function you need!
    COLOR_OVERRIDE = None
    def __init__(self, model, width=220, font=None, color=pbge.INFO_GREEN, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.color = self.COLOR_OVERRIDE or color
        self.update()
        self.height = self.image.get_height()

    def update(self):
        self.image = pbge.render_text(self.font, self.get_text(),
                                      self.width, justify=0, color=self.color)

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))

    def get_text(self):
        raise RuntimeError("AbstractModelTextBlock.get_text called")


class NameBlock(AbstractModelTextBlock):
    def get_text(self):
        return str(self.model)


class TitleBlock(object):
    def __init__(self, title="Title Block!", title_color=pbge.INFO_HILIGHT, width=220, **kwargs):
        self.title = title
        self.width = width
        self.image = pbge.render_text(pbge.my_state.huge_font, title, width, justify=0, color=title_color)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class FullNameBlock(AbstractModelTextBlock):
    COLOR_OVERRIDE = pbge.WHITE

    def get_text(self):
        return self.model.get_full_name()


class ListBlock(object):
    def __init__(self, items, width=220, **kwargs):
        self.items = items
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT, '\n'.join([str(i) for i in items]), width, justify=-1,
                                      color=pbge.INFO_GREEN)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class DescBlock(AbstractModelTextBlock):
    def get_text(self):
        return self.model.desc


class EnchantmentBlock(object):
    def __init__(self, model, width=220, **kwargs):
        self.model = model
        self.width = width
        if model.ench_list:
            self.image = pbge.render_text(pbge.SMALLFONT, ', '.join([e.name for e in model.ench_list]), width,
                                          justify=-1, color=pbge.INFO_HILIGHT)
            self.height = self.image.get_height()
        else:
            self.image = None
            self.height = 0

    def render(self, x, y):
        if self.image:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class ModuleStatusBlock(object):
    # This block contains both the module display and the Armor/Mobility displays.
    def __init__(self, model, width=220, **kwargs):
        self.model = model
        self.width = width
        self.height = 50
        self.module_display = ModuleDisplay(model)
        self.am_sprite = pbge.image.Image('sys_armormobility.png', 40, 50)

    def render(self, x, y):
        mydest = pygame.Rect(x, y, 40, 50)
        self.am_sprite.render(mydest, 0)
        textdest = pygame.Rect(mydest.x + 5, mydest.y + 10, 30, 16)
        pbge.draw_text(pbge.BIGFONT, str(self.model.calc_average_armor()), textdest, justify=0, color=pbge.INFO_HILIGHT)
        mydest.right = x + self.width
        self.am_sprite.render(mydest, 1)
        textdest = pygame.Rect(mydest.x + 5, mydest.y + 10, 30, 16)
        pbge.draw_text(pbge.BIGFONT, str(self.model.calc_mobility()), textdest, justify=0, color=pbge.INFO_HILIGHT)
        self.module_display.render(x + self.width // 2 - 30, y)


class BeingStatusBlock(object):
    DARK_HEALTH = pygame.Color(10, 50, 0)
    BRIGHT_HEALTH = pygame.Color(30, 150, 0)
    DARK_MENTAL = pygame.Color(0, 30, 50)
    BRIGHT_MENTAL = pygame.Color(0, 90, 150)
    DARK_STAMINA = pygame.Color(50, 0, 10)
    BRIGHT_STAMINA = pygame.Color(150, 0, 30)

    def __init__(self, model: base.Being, width=220, **kwargs):
        self.width = width
        self.model = model
        self.height = max(pbge.SMALLFONT.get_linesize(), 12)
        self.power_sprite = pbge.image.Image('sys_powerindicator.png', 32, 12)

    def render(self, x, y):
        field_width = (self.width - 47) // 3
        text_width = max(pbge.SMALLFONT.size(a)[0] for a in ("H:", "M:", "S:"))
        mydest = pygame.Rect(x, y, field_width, self.height)

        pbge.draw_text(pbge.SMALLFONT, 'H:', mydest, justify=-1, color=pbge.INFO_GREEN)
        maxi = self.model.max_health
        mini = self.model.current_health
        dark_rect = mydest.copy()
        dark_rect.x += text_width
        dark_rect.w -= text_width
        pbge.my_state.screen.fill(self.DARK_HEALTH, dark_rect)
        bright_rect = dark_rect.copy()
        bright_rect.w = int((bright_rect.w * mini) / maxi)
        pbge.my_state.screen.fill(self.BRIGHT_HEALTH, bright_rect)
        pbge.draw_text(pbge.SMALLFONT, str(mini), dark_rect, justify=0, vjustify=0, color=pbge.WHITE)

        mydest.x += field_width + 5
        pbge.draw_text(pbge.SMALLFONT, 'M:', mydest, justify=-1, color=pbge.INFO_GREEN)
        maxi = self.model.get_max_mental()
        mini = self.model.get_current_mental()
        dark_rect = mydest.copy()
        dark_rect.x += text_width
        dark_rect.w -= text_width
        pbge.my_state.screen.fill(self.DARK_MENTAL, dark_rect)
        bright_rect = dark_rect.copy()
        bright_rect.w = int((bright_rect.w * mini) / maxi)
        pbge.my_state.screen.fill(self.BRIGHT_MENTAL, bright_rect)
        pbge.draw_text(pbge.SMALLFONT, str(mini), dark_rect, justify=0, vjustify=0, color=pbge.WHITE)

        mydest.x += field_width + 5
        pbge.draw_text(pbge.SMALLFONT, 'S:', mydest, justify=-1, color=pbge.INFO_GREEN)
        maxi = self.model.get_max_stamina()
        mini = self.model.get_current_stamina()
        dark_rect = mydest.copy()
        dark_rect.x += text_width
        dark_rect.w -= text_width
        pbge.my_state.screen.fill(self.DARK_STAMINA, dark_rect)
        bright_rect = dark_rect.copy()
        bright_rect.w = int((bright_rect.w * mini) / maxi)
        pbge.my_state.screen.fill(self.BRIGHT_STAMINA, bright_rect)
        pbge.draw_text(pbge.SMALLFONT, str(mini), dark_rect, justify=0, vjustify=0, color=pbge.WHITE)

        cp, mp = self.model.get_current_and_max_power()
        if mp > 0:
            mydest = self.power_sprite.get_rect(0)
            mydest.midright = (x + self.width, y + self.height // 2)
            self.power_sprite.render(mydest, 10 - max(cp * 10 // mp, 1))


class PilotStatusBlock(object):
    DARK_HEALTH = pygame.Color(10, 50, 0)
    BRIGHT_HEALTH = pygame.Color(40, 200, 0)
    DARK_MENTAL = pygame.Color(0, 30, 50)
    BRIGHT_MENTAL = pygame.Color(0, 120, 200)
    DARK_STAMINA = pygame.Color(50, 0, 10)
    BRIGHT_STAMINA = pygame.Color(200, 0, 40)

    # Holds details on the pilot.
    def __init__(self, model, width=220, **kwargs):
        if model:
            self.model = model.get_pilot()
            self.mover = model
        else:
            self.model = None
        self.width = width
        self.height = max(pbge.SMALLFONT.get_linesize(), 12)
        self.power_sprite = pbge.image.Image('sys_powerindicator.png', 32, 12)

    def render(self, x, y):
        pbge.draw_text(pbge.SMALLFONT, str(self.model), pygame.Rect(x, y, self.width, self.height), justify=-1)
        if self.model:
            show_numbers = pbge.util.config.getboolean("GENERAL", "show_numbers_in_pilot_info")
            field_width = (self.width - 130) // 3
            text_width = max(pbge.SMALLFONT.size(a)[0] for a in ("H:", "M:", "S:"))
            mydest = pygame.Rect(x + 83, y, field_width, self.height)

            if show_numbers:
                pbge.draw_text(pbge.SMALLFONT, 'H:{}'.format(self.model.current_health), mydest.inflate(8, 0),
                               justify=-1, color=pbge.INFO_GREEN)
            else:
                pbge.draw_text(pbge.SMALLFONT, 'H:', mydest, justify=-1, color=pbge.INFO_GREEN)
                maxi = self.model.max_health
                mini = self.model.current_health
                dark_rect = mydest.copy()
                dark_rect.x += text_width
                dark_rect.w -= text_width
                pbge.my_state.screen.fill(self.DARK_HEALTH, dark_rect)
                bright_rect = dark_rect.copy()
                bright_rect.w = int((bright_rect.w * mini) / maxi)
                pbge.my_state.screen.fill(self.BRIGHT_HEALTH, bright_rect)

            mydest.x += field_width + 5
            if show_numbers:
                pbge.draw_text(pbge.SMALLFONT, 'M:{}'.format(self.model.get_current_mental()), mydest.inflate(8, 0),
                               justify=-1, color=pbge.INFO_GREEN)
            else:
                pbge.draw_text(pbge.SMALLFONT, 'M:', mydest, justify=-1, color=pbge.INFO_GREEN)
                maxi = self.model.get_max_mental()
                mini = self.model.get_current_mental()
                dark_rect = mydest.copy()
                dark_rect.x += text_width
                dark_rect.w -= text_width
                pbge.my_state.screen.fill(self.DARK_MENTAL, dark_rect)
                bright_rect = dark_rect.copy()
                bright_rect.w = int((bright_rect.w * mini) / maxi)
                pbge.my_state.screen.fill(self.BRIGHT_MENTAL, bright_rect)

            mydest.x += field_width + 5
            if show_numbers:
                pbge.draw_text(pbge.SMALLFONT, 'S:{}'.format(self.model.get_current_stamina()), mydest.inflate(8, 0),
                               justify=-1, color=pbge.INFO_GREEN)
            else:
                pbge.draw_text(pbge.SMALLFONT, 'S:', mydest, justify=-1, color=pbge.INFO_GREEN)
                maxi = self.model.get_max_stamina()
                mini = self.model.get_current_stamina()
                dark_rect = mydest.copy()
                dark_rect.x += text_width
                dark_rect.w -= text_width
                pbge.my_state.screen.fill(self.DARK_STAMINA, dark_rect)
                bright_rect = dark_rect.copy()
                bright_rect.w = int((bright_rect.w * mini) / maxi)
                pbge.my_state.screen.fill(self.BRIGHT_STAMINA, bright_rect)

            cp, mp = self.mover.get_current_and_max_power()
            if mp > 0:
                mydest = self.power_sprite.get_rect(0)
                mydest.midright = (x + self.width, y + self.height // 2)
                self.power_sprite.render(mydest, 10 - max(cp * 10 // mp, 1))


class CharacterStatusBlock(object):
    # Holds details on the pilot.
    def __init__(self, model, width=220, info_font=None, **kwargs):
        if model:
            self.model = model.get_pilot()
        else:
            self.model = None
        self.font = info_font or pbge.ITALICFONT
        self.width = width
        self.height = max(self.font.get_linesize() * 3, 12)
        self.rowheight = self.font.get_linesize()

    def render(self, x, y):
        if self.model:
            pbge.draw_text(self.font, 'Health: {}/{}'.format(self.model.current_health, self.model.max_health),
                           pygame.Rect(x, y, self.width, self.rowheight), justify=0, color=pbge.INFO_GREEN)
            pbge.draw_text(self.font,
                           'Mental: {}/{}'.format(self.model.get_current_mental(), self.model.get_max_mental()),
                           pygame.Rect(x, y + self.rowheight, self.width, self.rowheight), justify=0,
                           color=pbge.INFO_GREEN)
            pbge.draw_text(self.font,
                           'Stamina: {}/{}'.format(self.model.get_current_stamina(), self.model.get_max_stamina()),
                           pygame.Rect(x, y + self.rowheight * 2, self.width, self.rowheight), justify=0,
                           color=pbge.INFO_GREEN)


class OddsInfoBlock(object):
    def __init__(self, odds, modifiers, width=220, **kwargs):
        self.odds = odds
        self.modifiers = modifiers
        self.modifiers.sort(key=lambda x: -abs(x[0]))
        self.width = width
        self.height = pbge.SMALLFONT.get_linesize() * 3

    def render(self, x, y):
        pbge.draw_text(pbge.my_state.huge_font, '{}%'.format(max(min(int(self.odds * 100), 99), 1)),
                       pygame.Rect(x, y, 75, 32),
                       justify=0, color=pbge.INFO_HILIGHT)
        pbge.draw_text(pbge.my_state.big_font, 'TO HIT',
                       pygame.Rect(x, y + pbge.my_state.huge_font.get_linesize(), 75, 32), justify=0,
                       color=pbge.INFO_HILIGHT)
        t = 0
        for mymod in self.modifiers:
            pbge.draw_text(pbge.my_state.small_font, '{:+d}: {}'.format(int(mymod[0]), mymod[1]),
                           pygame.Rect(x + 77, y + t * pbge.SMALLFONT.get_linesize(), self.width - 77, 32), justify=-1,
                           color=pbge.INFO_GREEN)
            t += 1
            if t > 2:
                break


class PrimaryStatsBlock(object):
    def __init__(self, model, width=220, font=None, **kwargs):
        if model:
            self.model = model.get_pilot()
            self.mover = model
        else:
            self.model = None
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.height = self.font.get_linesize() * len(stats.PRIMARY_STATS)

    STAT_RANKS = (
        'Hopeless', 'Pathetic', 'Terrible', 'Poor', 'Average', 'Good', 'Great', 'Amazing', 'Incredible', 'Legendary')

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        max_w = 0
        for ps in stats.PRIMARY_STATS:
            mytext = '{}: '.format(ps.name)
            pbge.draw_text(self.font, mytext, mydest, color=pbge.INFO_GREEN)
            max_w = max(max_w, self.font.size(mytext)[0])
            mydest.y += self.font.get_linesize()
        if self.model:
            mydest = pygame.Rect(x + max_w, y, 36, self.height)
            rankdest = pygame.Rect(x + max_w + 36, y, self.width - max_w - 36, self.height)
            has_statline = hasattr(self.model, 'statline')
            for ps in stats.PRIMARY_STATS:
                statval = self.model.get_stat(ps)
                statstr = str(statval)
                if has_statline:
                    basestat = self.model.statline.get(ps, 0)
                    if statval > basestat:
                        statstr += ' +'
                    elif statval < basestat:
                        statstr += ' -'
                pbge.draw_text(self.font, statstr, mydest, color=pbge.INFO_HILIGHT)
                mydest.y += self.font.get_linesize()
                pbge.draw_text(self.font, self.STAT_RANKS[max(min((statval - 2) // 2, len(self.STAT_RANKS) - 1), 0)],
                               rankdest, color=pbge.INFO_GREEN)
                rankdest.y = mydest.y


class MechaStatsBlock(object):
    def __init__(self, model: base.Mecha, font=None, width=220, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.height = self._get_text_image().get_height()

    def _get_text_image(self):
        return pbge.render_text(self.font,
                                "Mass: {:.1f} tons \n Armor: {} \n Mobility: {} \n Speed: {} \n Sensor Range: {} \n E-War Progs: {} \n Action Bonus: {}".format(
                                    self.model.mass / 10000.0,
                                    self.model.calc_average_armor(),
                                    self.model.calc_mobility(),
                                    self.model.get_max_speed(),
                                    self.model.get_sensor_range(self.model.scale),
                                    self.model.get_ewar_rating(),
                                    self.model.get_bonus_action_cost_mod()
                                    ),
                                self.width, justify=0, color=pbge.INFO_GREEN)

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        myimg = self._get_text_image()
        pbge.my_state.screen.blit(myimg, mydest)


class LabeledItemsListBlock(object):
    LABEL = "???"

    def __init__(self, model, width=220, font=None, color=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.color = color or pbge.INFO_GREEN
        self.update()

    def update(self):
        itemz = self.get_sorted_items()
        self.image = pbge.render_text(self.font, '{}: {}'.format(self.LABEL, ', '.join(itemz or ["None"])), self.width,
                                      justify=-1, color=self.color)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))

    # Can override in derived class if you want your own sort.
    # Return a list of strings.
    def get_sorted_items(self):
        itemz = self.get_items()
        itemz.sort()
        return itemz

    # Override in derived class to give what you want to show.
    # Return a list of strings.
    def get_items(self):
        raise RuntimeError('LabeldItemsListBlock.get_items called')


class InstalledCyberwaresBlock(LabeledItemsListBlock):
    LABEL = "Cyberware"

    def get_items(self):
        return [c.name for c in self.model.cyberware()]


class NonComSkillBlock(LabeledItemsListBlock):
    LABEL = "Skills"

    def get_sorted_items(self):
        # First, generate the base skills and the effective skills.
        base_skills = set([sk for sk in list(self.model.statline.keys()) if sk in stats.NONCOMBAT_SKILLS])
        all_skills = self.model.get_all_skills()
        effective_skills = set([sk for sk in all_skills if sk in stats.NONCOMBAT_SKILLS])
        # Now get normal skills everyone has that are lost.
        lost_combat_skills = set(stats.COMBATANT_SKILLS).difference(all_skills)
        # Get the union of all skills to be listed.
        listed_skills = list(base_skills.union(effective_skills, lost_combat_skills))
        # Sort it here.
        listed_skills.sort(key=lambda sk: sk.name)

        # For each skill, annotate.
        def annotate(sk):
            if not sk in effective_skills:
                return '({})'.format(sk.name)
            if not sk in base_skills:
                return '+{}'.format(sk.name)
            else:
                return sk.name

        return [annotate(sk) for sk in listed_skills]


class PetSkillBlock(LabeledItemsListBlock):
    LABEL = "Skills"

    def get_sorted_items(self):
        # First, generate the base skills and the effective skills.
        return [str(sk) for sk in list(self.model.statline.keys()) if sk in stats.NONCOMBAT_SKILLS] or ["None"]


class MeritBadgesBlock(LabeledItemsListBlock):
    LABEL = "Badges"

    def get_items(self):
        return [b.name for b in self.model.badges]


class CharacterTagsBlock(LabeledItemsListBlock):
    LABEL = "Tags"

    def get_items(self):
        return [str(b) for b in self.model.get_tags(include_all=False)]


class ExperienceBlock(object):
    def __init__(self, model, width=220, font=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        self.image = pbge.render_text(self.font, 'XP: {}/{}'.format(
            self.model.experience[self.model.TOTAL_XP] - self.model.experience[self.model.SPENT_XP],
            self.model.experience[self.model.TOTAL_XP]),
                                      self.width, justify=0, color=pbge.INFO_GREEN)

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class ModuleDisplay(object):
    # The dest area should be 60x50.
    MODULE_FORM_FRAME_OFFSET = {
        base.MF_Torso: 0,
        base.MF_Head: 9,
        base.MF_Arm: 18,
        base.MF_Leg: 27,
        base.MF_Wing: 36,
        base.MF_Tail: 45,
        base.MF_Turret: 54,
        base.MF_Storage: 63,
    }

    def __init__(self, model):
        self.model = model
        self.module_sprite = pbge.image.Image('sys_modules.png', 16, 16)

    def part_struct_frame(self, module):
        if module.is_destroyed():
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form, 0) + 8
        else:
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form, 0) + min((module.get_damage_status() + 5) // 14, 7)

    def part_armor_frame(self, module, armor):
        if armor.is_destroyed():
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form, 0) + 80
        else:
            return self.MODULE_FORM_FRAME_OFFSET.get(module.form, 0) + 72 + min((armor.get_damage_status() + 5) // 14,
                                                                                7)

    def draw_this_part(self, module):
        if (self.module_num % 2) == 1:
            self.module_dest.centerx = self.dest.centerx - 12 * self.module_num // 2 - 6
        else:
            self.module_dest.centerx = self.dest.centerx + 12 * self.module_num // 2
        self.module_sprite.render(self.module_dest, self.part_struct_frame(module))
        armor = module.get_armor(destroyed_ok=True)
        if armor:
            self.module_sprite.render(self.module_dest, self.part_armor_frame(module, armor))
        self.module_num += 1

    def add_parts_of_type(self, mod_form):
        for module in self.model.sub_com:
            if hasattr(module, "form") and module.form is mod_form and module.info_tier is None:
                self.draw_this_part(module)

    def add_parts_of_tier(self, mod_tier):
        for module in self.model.sub_com:
            if hasattr(module, "form") and module.info_tier == mod_tier:
                self.draw_this_part(module)

    def render(self, x, y):
        self.dest = pygame.Rect(x, y, 60, 50)
        self.module_dest = pygame.Rect(self.dest.x, self.dest.y, 16, 16)

        self.module_num = 0
        self.add_parts_of_type(base.MF_Head)
        self.add_parts_of_type(base.MF_Turret)
        self.module_num = max(self.module_num, 1)  # Want pods to either side of body; head and/or turret in middle.
        self.add_parts_of_type(base.MF_Storage)
        self.add_parts_of_tier(1)

        self.module_num = 0
        self.module_dest.y += 17
        self.add_parts_of_type(base.MF_Torso)
        self.add_parts_of_type(base.MF_Arm)
        self.add_parts_of_type(base.MF_Wing)
        self.add_parts_of_tier(2)

        self.module_num = 0
        self.module_dest.y += 17
        self.add_parts_of_type(base.MF_Tail)
        self.module_num = max(self.module_num, 1)  # Want legs to either side of body; tail in middle.
        self.add_parts_of_type(base.MF_Leg)
        self.add_parts_of_tier(3)


class PropStatusBlock(object):
    # This block contains the armor/damage graphic.
    def __init__(self, model, width=220, **kwargs):
        self.model = model
        self.width = width
        self.height = 32
        self.status_sprite = pbge.image.Image("sys_propstatus.png", 32, 32)

    def prop_struct_frame(self):
        if self.model.is_destroyed():
            return 8
        else:
            return min((self.model.get_damage_status() + 5) // 14, 7)

    def prop_armor_frame(self, armor):
        if armor.is_destroyed():
            return 18
        else:
            return 10 + min((armor.get_damage_status() + 5) // 14, 7)

    def render(self, x, y):
        mydest = pygame.Rect(x + self.width // 2 - 16, y, 32, 32)

        self.status_sprite.render(mydest, self.prop_struct_frame())
        armor = self.model.get_armor(destroyed_ok=True)
        if armor:
            self.status_sprite.render(mydest, self.prop_armor_frame(armor))


class MechaFeaturesAndSpriteBlock(object):
    def __init__(self, model: base.Mecha, width=360, additional_info="", **kwargs):
        self.model = model
        self.width = width
        self.height = 136
        mybmp = pygame.Surface((128, 128))
        mybmp.fill((0, 0, 255))
        mybmp.set_colorkey((0, 0, 255), pygame.RLEACCEL)
        myimg = self.model.get_sprite()
        myimg.render(dest_surface=mybmp, dest=pygame.Rect(0, 0, 128, 128), frame=self.model.frame)
        self.image = pygame.transform.scale2x(mybmp)
        self.bg = pbge.image.Image("sys_mechascalegrid.png", 136, 136)
        self.additional_info = additional_info

    def render(self, x, y):
        self.bg.render(pygame.Rect(x, y, 136, 136), 0)
        pbge.my_state.screen.blit(self.image, pygame.Rect(x + 4, y + 4, 128, 128))
        mydest = pygame.Rect(x + 140, y, self.width - 140, self.height)
        pbge.draw_text(pbge.MEDIUMFONT,
                       "Mass: {:.1f} tons \n Armor: {} \n Mobility: {} \n Speed: {} \n Sensor Range: {} \n E-War Progs: {} \n Action Bonus: {} {}".format(
                           self.model.mass / 10000.0,
                           self.model.calc_average_armor(),
                           self.model.calc_mobility(),
                           self.model.get_max_speed(),
                           self.model.get_sensor_range(self.model.scale),
                           self.model.get_ewar_rating(),
                           self.model.get_bonus_action_cost_mod(),
                           self.additional_info),
                       mydest, color=pbge.INFO_GREEN)


class CharaPortraitAndSkillsBlock(object):
    def __init__(self, model, width=360, additional_info="", **kwargs):
        self.model = model
        self.width = width
        self.height = 100
        self.image = model.get_portrait()
        self.additional_info = additional_info

    def render(self, x, y):
        self.image.render(pygame.Rect(x, y, 100, 100), 1)
        mydest = pygame.Rect(x + 110, y, self.width - 110, self.height)
        skillz = [sk.name for sk in list(self.model.statline.keys()) if sk in stats.NONCOMBAT_SKILLS]
        pbge.draw_text(pbge.MEDIUMFONT, 'Skills: {}'.format(', '.join(skillz or ["None"])), mydest, justify=-1,
                       color=pbge.INFO_GREEN)


class MassVolumeBlock(object):
    def __init__(self, model, width=220, info_font=None, **kwargs):
        self.model = model
        self.width = width
        self.image = None
        self.font = info_font or pbge.ITALICFONT
        self.height = self.font.get_linesize()

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        pbge.draw_text(self.font, self.model.scale.get_mass_string(self.model.mass), mydest, color=pbge.INFO_GREEN)
        pbge.draw_text(self.font, '{} slots'.format(self.model.volume), mydest, justify=1, color=pbge.INFO_GREEN)


class MassVolumeHPBlock(object):
    def __init__(self, model, width=220, info_font=None, **kwargs):
        self.model = model
        self.width = width
        self.image = None
        self.font = info_font or pbge.ITALICFONT
        self.height = self.font.get_linesize()

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        pbge.draw_text(self.font, self.model.scale.get_mass_string(self.model.mass), mydest, color=pbge.INFO_GREEN)
        pbge.draw_text(self.font, '{} slots'.format(self.model.volume), mydest, justify=1, color=pbge.INFO_GREEN)
        pbge.draw_text(self.font, '{} HP'.format(self.model.max_health), mydest, justify=0, color=pbge.INFO_GREEN)


class WeaponStatsBlock(object):
    def __init__(self, model, width=220, font=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.stars = pbge.image.Image('sys_weaponstar.png', 16, 16)
        self.linesize = max(self.font.get_linesize(), 16)
        self.height = self.linesize * len(self.WEAPON_STAT_NAMES)

    WEAPON_STAT_NAMES = ('Damage', 'Accuracy', 'Penetration', 'Reach')

    def _draw_stars(self, x, y, n):
        for t in range(n):
            mydest = pygame.Rect(x + t * 18, y, 16, 16)
            self.stars.render(mydest, 0)

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width // 2, self.height)
        for ps in self.WEAPON_STAT_NAMES:
            pbge.draw_text(self.font, '{}: '.format(ps), mydest, justify=1, color=pbge.INFO_GREEN)
            mydest.y += self.linesize
        if self.model:
            self._draw_stars(x + self.width // 2 + 16, y, self.model.damage)
            self._draw_stars(x + self.width // 2 + 16, y + self.linesize, self.model.accuracy)
            self._draw_stars(x + self.width // 2 + 16, y + self.linesize * 2, self.model.penetration)
            mydest = pygame.Rect(x + self.width // 2 + 16, y + self.linesize * 3, self.width // 2 - 16, self.linesize)
            pbge.draw_text(self.font, self.model.get_reach_str(), mydest, color=pbge.INFO_HILIGHT)


class LauncherStatsBlock(WeaponStatsBlock):
    def __init__(self, model, **kwargs):
        self.model = model.get_ammo()
        super(LauncherStatsBlock, self).__init__(model=self.model, **kwargs)
        if not self.model:
            self.height = 0

    def render(self, x, y):
        if self.model:
            super(LauncherStatsBlock, self).render(x, y)


class ItemStatsBlock(object):
    # get_item_stats is a function which returns a list of (k,v) tuples describing this item's stats.
    def __init__(self, model, width=220, font=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.linesize = self.font.get_linesize()
        if hasattr(model, "get_item_stats"):
            self.height = self.font.get_linesize() * len(self.model.get_item_stats())
        else:
            self.height = 0

    def render(self, x, y):
        if hasattr(self.model, "get_item_stats"):
            mydest_k = pygame.Rect(x, y, self.width // 2, self.height)
            mydest_v = pygame.Rect(x + self.width // 2 + 16, y, self.width // 2 - 16, self.height)
            for k, v in self.model.get_item_stats():
                pbge.draw_text(self.font, "{}:".format(k), mydest_k, pbge.INFO_GREEN, justify=1)
                pbge.draw_text(self.font, v, mydest_v, pbge.INFO_HILIGHT, justify=-1)
                mydest_k.y += self.linesize
                mydest_v.y += self.linesize


class WeaponSkillBlock(object):
    def __init__(self, model, width=220, font=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.image = pbge.render_text(self.font,
                                      '{} + {}'.format(model.get_attack_skill().name, model.attack_stat.name), width,
                                      justify=0, color=pbge.INFO_GREEN)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class ItemsListBlock(object):
    def __init__(self, model, width=220, font=None, color=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.color = color or pbge.INFO_HILIGHT
        items = list(self.get_items())
        if items:
            items.sort()
            self.image = pbge.render_text(self.font, ', '.join(items), width, justify=0, color=self.color)
            self.height = self.image.get_height()
        else:
            self.image = None
            self.height = 0

    # Override this in your derived class
    def get_items(self):
        raise RuntimeError("ItemsListBlock.get_items not overridden!")

    def render(self, x, y):
        if self.height > 0:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class WeaponAttributesBlock(ItemsListBlock):
    def get_items(self):
        attatts = self.model.get_attributes()
        return [att.name for att in attatts]


class ProgramsBlock(ItemsListBlock):
    def get_items(self):
        programs = self.model.programs
        return [program.name for program in programs]


class CyberwareStatlineBlock(ItemsListBlock):
    def get_items(self):
        items = list()
        for stat in self.model.statline.keys():
            value = self.model.statline[stat]
            if value == 0:
                continue
            items.append('{} {:+}'.format(stat.name, value))
        return items


class SubComsBlock(ItemsListBlock):
    def get_items(self):
        return [item.name for item in list(self.model.sub_com)]


class NonArmorSubComsBlock(ItemsListBlock):
    def get_items(self):
        return [item.get_full_name() for item in list(self.model.sub_com) if not isinstance(item, base.Armor)]


class HostilityStatusBlock(object):
    def __init__(self, model, width=220, font=None, scene=None, **kwargs):
        self.model = model
        self.scene = scene
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()

    def update(self):
        if self.scene and self.scene.is_hostile_to_player(self.model):
            self.image = pbge.render_text(self.font, 'HOSTILE UNIT', self.width, justify=0, color=pbge.ENEMY_RED)
            self.height = self.image.get_height()
        else:
            self.image = None
            self.height = 0

    def render(self, x, y):
        if self.image:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class DesignViabilityBlock(object):
    def __init__(self, model, width=220, font=None, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.MEDIUMFONT
        self.update()

    def update(self):
        if self.model and not self.model.check_design():
            self.image = pbge.render_text(self.font, 'INVALID DESIGN', self.width, justify=0, color=pbge.ENEMY_RED)
            self.height = self.image.get_height()
        else:
            self.image = None
            self.height = 0

    def render(self, x, y):
        if self.image:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class ClothingArmorBlock(object):
    def __init__(self, model, width=220, info_font=None, **kwargs):
        self.model = model
        self.armor_gear = None
        for ag in model.sub_com:
            if isinstance(ag, base.Armor):
                self.armor_gear = ag
                break
        self.width = width
        self.font = info_font or pbge.MEDIUMFONT
        self.height = self.font.get_linesize()

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        if self.armor_gear:
            pbge.draw_text(self.font, "Armor: {}/{}".format(self.armor_gear.get_armor_rating(),
                                                            self.armor_gear.get_armor_rating(False)), mydest,
                           color=pbge.INFO_GREEN, justify=0)
        else:
            pbge.draw_text(self.font, "Armor: 0/0", mydest, color=pbge.INFO_GREEN, justify=0)


class CreditsBlock(object):
    def __init__(self, camp, font=None, width=220, **kwargs):
        self.camp = camp
        self.width = width
        self.font = font or pbge.SMALLFONT
        self.image = None
        self.update()
        self.height = self.image.get_height()

    def _should_abbreviate(self):
        return self.width < 150

    def update(self):
        creds = self.camp.credits
        if creds > 999999999 and self._should_abbreviate():
            cred_string = "${:,}M".format(creds//1000000)
        elif creds > 9999999 and self._should_abbreviate():
            cred_string = "${:,}k".format(creds//1000)
        else:
            cred_string = '${:,}'.format(creds)

        self.image = pbge.render_text(
            self.font, cred_string, self.width, justify=0, color=pbge.INFO_GREEN
        )

    def render(self, x, y):
        self.update()
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class EncumberanceBlock(object):
    def __init__(self, model, font=None, width=220, **kwargs):
        self.model = model
        self.width = width
        self.font = font or pbge.SMALLFONT

    @property
    def height(self):
        if hasattr(self.model, "carrying_capacity") and self._should_split():
            return self.font.get_linesize() * 2
        else:
            return self.font.get_linesize()

    def _should_split(self):
        return self.width < 150

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        mymass = self.model.get_inv_mass()
        mycolor = pbge.INFO_GREEN
        if hasattr(self.model, "carrying_capacity"):
            mycapacity = self.model.carrying_capacity()
            if mymass > mycapacity * 1.25:
                mycolor = pbge.ENEMY_RED
            elif mymass > mycapacity:
                mycolor = pygame.Color("yellow")
            if self._should_split():
                base_msg = "{} \n/{}"
            else:
                base_msg = "{}/{}"
            pbge.draw_text(
                self.font,
                base_msg.format(self.model.scale.get_mass_string(mymass), self.model.scale.get_mass_string(mycapacity)),
                mydest, mycolor, justify=0
            )
        else:
            pbge.draw_text(
                self.font, self.model.scale.get_mass_string(mymass), mydest, mycolor, justify=0
            )



class MechaStatusDisplay(InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (FullNameBlock, HostilityStatusBlock, ModuleStatusBlock, PilotStatusBlock, EnchantmentBlock)


class BeingStatusDisplay(InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (FullNameBlock, HostilityStatusBlock, ModuleStatusBlock, BeingStatusBlock, EnchantmentBlock)


class PropStatusDisplay(InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (FullNameBlock, HostilityStatusBlock, PropStatusBlock, EnchantmentBlock)


class NameStatusDisplay(InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (NameBlock,)


class ListDisplay(InfoPanel):
    DEFAULT_BLOCKS = (ListBlock,)


class ItemIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeHPBlock, ItemStatsBlock, DescBlock)


class WeaponIP(InfoPanel):
    DEFAULT_BLOCKS = (
        FullNameBlock, MassVolumeHPBlock, WeaponStatsBlock, ItemStatsBlock, WeaponSkillBlock, WeaponAttributesBlock,
        DescBlock)

class AmmoIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeHPBlock, ItemStatsBlock, WeaponAttributesBlock, DescBlock)

class LauncherIP(InfoPanel):
    DEFAULT_BLOCKS = (
        FullNameBlock, MassVolumeBlock, LauncherStatsBlock, ItemStatsBlock, WeaponSkillBlock, WeaponAttributesBlock,
        DescBlock)


class EWSystemIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeHPBlock, ItemStatsBlock, ProgramsBlock, DescBlock)


class CyberwareIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeHPBlock, ItemStatsBlock, CyberwareStatlineBlock, DescBlock)


class ShieldIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeHPBlock, ItemStatsBlock, SubComsBlock, DescBlock)


class MechaIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, DesignViabilityBlock, MechaFeaturesAndSpriteBlock, DescBlock)


class CharacterIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, ModuleStatusBlock, ExperienceBlock, CharacterStatusBlock, PrimaryStatsBlock,
                      InstalledCyberwaresBlock, NonComSkillBlock, MeritBadgesBlock, CharacterTagsBlock)


class ClothingIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, MassVolumeBlock, ClothingArmorBlock, NonArmorSubComsBlock, DescBlock)


class MonsterIP(InfoPanel):
    DEFAULT_BLOCKS = (FullNameBlock, ModuleStatusBlock, ExperienceBlock,
                      CharacterStatusBlock, PrimaryStatsBlock, PetSkillBlock)


class ShortItemIP(InfoPanel):
    DEFAULT_BLOCKS = (DescBlock,)


class ShortWeaponIP(InfoPanel):
    DEFAULT_BLOCKS = (WeaponStatsBlock, ItemStatsBlock, WeaponSkillBlock, WeaponAttributesBlock)


class ShortLauncherIP(InfoPanel):
    DEFAULT_BLOCKS = (LauncherStatsBlock, ItemStatsBlock, WeaponSkillBlock, WeaponAttributesBlock)


def get_status_display(model, **kwargs):
    if isinstance(model, base.Mecha):
        return MechaStatusDisplay(model=model, **kwargs)
    elif isinstance(model, base.Being):
        return BeingStatusDisplay(model=model, **kwargs)
    elif isinstance(model, base.Prop):
        return PropStatusDisplay(model=model, **kwargs)
    else:
        return NameStatusDisplay(model=model, **kwargs)


def get_longform_display(model, **kwargs):
    if isinstance(model, base.Weapon):
        return WeaponIP(model=model, **kwargs)
    elif isinstance(model, base.Ammo):
        return AmmoIP(model=model, **kwargs)
    elif isinstance(model, base.Launcher):
        return LauncherIP(model=model, **kwargs)
    elif isinstance(model, base.EWSystem):
        return EWSystemIP(model=model, **kwargs)
    elif isinstance(model, base.BaseCyberware):
        return CyberwareIP(model=model, **kwargs)
    elif isinstance(model, base.Shield):
        return ShieldIP(model=model, **kwargs)
    elif isinstance(model, base.Mecha):
        return MechaIP(model=model, **kwargs)
    elif isinstance(model, base.Character):
        return CharacterIP(model=model, **kwargs)
    elif isinstance(model, base.Clothing):
        return ClothingIP(model=model, **kwargs)
    elif isinstance(model, base.Monster):
        return MonsterIP(model=model, **kwargs)
    else:
        return ItemIP(model=model, **kwargs)


def get_shortform_display(model, **kwargs):
    if isinstance(model, base.Weapon):
        return ShortWeaponIP(model=model, **kwargs)
    elif isinstance(model, base.Launcher):
        return ShortLauncherIP(model=model, **kwargs)
    else:
        return ShortItemIP(model=model, **kwargs)


ENEMY_BORDER = pbge.Border(
    border_width=8, tex_width=16, border_name="sys_enemyborder.png",
    tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2
)


class InfoWidget(pbge.widgets.Widget):
    # A widget that holds an info panel. Works just like a normal widget. Provide your own info panel and make sure
    # that the dimensions are compatible,
    def __init__(self, dx, dy, w, h, info_panel: InfoPanel, **kwargs):
        super().__init__(dx, dy, w, h, **kwargs)
        self.info_panel = info_panel

    def render(self, flash=False):
        if self.info_panel:
            mydest = self.get_rect()
            pbge.my_state.screen.set_clip(mydest)
            self.info_panel.render(mydest.x, mydest.y)
            pbge.my_state.screen.set_clip(None)
