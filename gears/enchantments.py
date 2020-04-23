
END_COMBAT = "END_COMBAT"
ON_MOVE = "ON_MOVE"


class EnchantmentList(list):
    def get_stat( self , stat ):
        p_max,n_max = 0,0
        for thing in self:
            if hasattr( thing, "get_stat" ):
                v = thing.get_stat( stat )
                if v > 0:
                    p_max = max( v , p_max )
                elif v < 0:
                    n_max = min( v , n_max )
        return p_max + n_max

    def add_enchantment(self, target, ench_type, ench_params):
        current_ench = self.get_enchantment_of_class(ench_type)
        if current_ench and hasattr(current_ench,'add_enchantment'):
            current_ench.merge_enchantment(**ench_params)
        elif ench_type.can_affect(target) and not current_ench:
            self.append(ench_type(**ench_params))

    def tidy( self, dispel_this ):
        for thing in list(self):
            if hasattr( thing, "dispel" ) and dispel_this in thing.dispel:
                self.remove( thing )

    def get_enchantment_of_class( self, find_this ):
        for thing in self:
            if thing.__class__ is find_this:
                return thing

    def has_enchantment_of_type( self, find_this ):
        for thing in self:
            if hasattr( thing, "dispel" ) and find_this in thing.dispel:
                return True

    def update(self,camp,owner):
        for thing in list(self):
            if hasattr(thing,"update"):
                thing.update(camp,owner)
            if hasattr(thing,'duration') and thing.duration:
                thing.duration -= 1
                if thing.duration < 1:
                    self.remove(thing)

    def get_funval(self, owner, funname):
        # The funval function takes owner as parameter.
        # Existing funval types:
        #   get_mobility_bonus
        #   get_penetration_bonus
        p_max,n_max = 0,0
        for thing in self:
            if hasattr( thing, funname ):
                v = getattr(thing,funname)( owner )
                if v > 0:
                    p_max = max( v , p_max )
                elif v < 0:
                    n_max = min( v , n_max )
        return p_max + n_max
    def get_tags(self,tag_id):
        return [getattr(thing,tag_id) for thing in self if hasattr(thing,tag_id)]


class Enchantment(object):
    DEFAULT_DURATION = None
    DEFAULT_DISPEL = (END_COMBAT,)
    def __init__(self, duration=None, dispel=None, **kwargs):
        self.duration = duration or self.DEFAULT_DURATION
        self.dispel = dispel or self.DEFAULT_DISPEL

    def merge_enchantment(self, **kwargs):
        # An enchantment of the same type is being added to this one.
        if self.duration:
            d = kwargs.get('duration') or self.DEFAULT_DURATION
            if d:
                self.duration += max(d-1,1)

    def end(self):
        self.duration = 0

    @classmethod
    def can_affect(cls,target):
        return True



