from pbge import image

class AreaEnchantment:
    def __init__(self, pos=None, altitude=None, duration=2, scene=None):
        self.altitude = altitude
        self.duration = duration
        if scene and pos:
            self.place(scene, pos)
        else:
            self.pos = pos

    def place(self, scene, pos):
        if hasattr(self, "container") and self.container:
            self.container.remove(self)

        for thing in scene.contents:
            if hasattr(thing, "pos") and thing.pos == pos and hasattr(thing, "AREA_ENCHANTMENT_TYPE") and thing.AREA_ENCHANTMENT_TYPE == self.AREA_ENCHANTMENT_TYPE:
                # Can't place a new enchantment in this tile. Extend the duration of the existing enchantment.
                thing.duration += self.duration
                return
                
        scene.contents.append(self)
        self.pos = pos

    AREA_ENCHANTMENT_TYPE = "Area Enchantment"
    IMAGENAME = ""
    COLORS = None
    IMAGEHEIGHT = 64
    IMAGEWIDTH = 64
    FRAME = 0
    FRAMES = ()
    sort_priority = 99
    TRANSPARENT = True
    # A set of tags describing how this area enchantment may be dispelled.
    DISPEL = {}

    def get_sprite(self):
        """Generate the sprite for this thing."""
        return image.Image(self.IMAGENAME, self.IMAGEWIDTH, self.IMAGEHEIGHT, self.COLORS, transparent=self.TRANSPARENT)

    def render(self, foot_pos, view):
        spr = view.get_sprite(self)
        if self.FRAMES:
            frame = self.FRAMES[view.phase % len(self.FRAMES)]
        else:
            frame = self.FRAME
        mydest = spr.get_rect(frame)
        mydest.midbottom = foot_pos.midbottom
        spr.render(mydest, frame)

    def update(self, myscene):
        # Handle upkeep. Return True if this enchantment should be removed.
        self.duration -= 1
        return bool(self.duration <= 1)

    def get_invocation(self, myscene):
        # If this area enchantment has an effect, like fire or poison gas or something,
        # handle that here.
        return None

    def __str__(self):
        return self.AREA_ENCHANTMENT_TYPE

