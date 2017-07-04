import random
import weakref

class PlotError( Exception ):
    """Plot init will call this if initialization impossible."""
    pass

class Chapter( object ):
    """ A chapter links a group of plots to a root plot and/or a world."""
    def __init__( self, root=None, world = None ):
        self.root = root
        self.world = world

class PlotState( object ):
    """For passing state information to subplots."""
    def __init__( self, chapter=None, rank=None, elements=None ):
        self.chapter = chapter
        self.rank = rank
        if elements:
            self.elements = elements.copy()
        else:
            self.elements = dict()
    def based_on( self, oplot ):
        self.chapter = self.chapter or oplot.chapter
        self.rank = self.rank or oplot.rank
        # Only copy over the elements not marked as private.
        for k,v in oplot.elements.iteritems():
            if isinstance( k, str ) and len(k)>0 and k[0]!="_":
                if k not in self.elements:
                    self.elements[k] = v
        # Why return self? Because this function will often be called straight
        # from the generator.
        return self

def all_contents( thing, check_subscenes=True ):
    """Iterate over this thing and all of its descendants."""
    yield thing
    if hasattr( thing, "contents" ):
        for t in thing.contents:
            if check_subscenes or not isinstance( t, maps.Scene ):
                for tt in all_contents( t, check_subscenes ):
                    yield tt
    if hasattr( thing, "sub_scenes" ):
        for t in thing.sub_scenes:
            if check_subscenes or not isinstance( t, maps.Scene ):
                for tt in all_contents( t, check_subscenes ):
                    yield tt

class Plot( object ):
    """The building block of the adventure."""
    LABEL = ""
    UNIQUE = False
    COMMON = False
    chapter = None
    rank = 1
    active = False

    _used = 0

    # Scope determines from where the event scripts in this plot will be called.
    # If scope is the element ID of a scene, then this plot's scripts will only
    # be triggered from within that scene.
    # If scope is True, then this plot is global, and its scripts will be
    # triggered no matter where the party happens to be.
    # If scope is None, then this plot will get thrown away after the narrative
    # gets built and its scripts will never be called.
    # Also note that self.active must be True for scripts to be triggered.
    scope = None
    def __init__( self, nart, pstate ):
        """Initialize + install this plot, or raise PlotError"""
        # nart = The Narrative object
        # pstate = The current plot state

        # Inherit the plot state.
        self.chapter = pstate.chapter or self.chapter
        self.rank = pstate.rank or self.rank
        self.elements = pstate.elements.copy()
        self.subplots = dict()

        # Increment the usage count, for getting info on plot numbers!
        self.__class__._used += 1

        # The move_records are stored in case this plot gets removed.
        self.move_records = list()

        # Do the custom initialization
        allok = self.custom_init( nart )

        # If failure, delete currently added subplots + raise error.
        if not allok:
            self.fail(nart)

    def fail( self, nart ):
        self.remove( nart )
        raise PlotError( str( self.__class__ ) )

    def get_element_idents( self, ele ):
        """Return list of element idents assigned to this object."""
        return [key for key,value in self.elements.items() + self.subplots.items() if value is ele]

    def add_sub_plot( self, nart, splabel, spstate=None, ident=None, necessary=True ):
        if not spstate:
            spstate = PlotState().based_on(self)
        if not ident:
            ident = "_autoident_{0}".format( len( self.subplots ) )
        sp = nart.generate_sub_plot( spstate, splabel )
        if necessary and not sp:
            self.fail( nart )
        elif sp:
            self.subplots[ident] = sp
        return sp

    def add_first_locale_sub_plot( self, nart, locale_type="CITY_SCENE" ):
        # Utility function for a frequently used special case.
        sp = self.add_sub_plot( nart, locale_type )
        if sp:
            nart.camp.scene = sp.elements.get( "LOCALE" )
            self.register_element( "LOCALE", sp.elements.get( "LOCALE" ) )
            nart.camp.entrance = sp.elements.get( "ENTRANCE" )
        return sp

    def move_element( self, ele, dest ):
        # Record when a plot places an element; if this plot is removed, the
        # element will be removed from its location as well.
        if hasattr( ele, "container" ) and ele.container:
            ele.container.remove( ele )
        dest.contents.append( ele )
        self.move_records.append( (ele,dest.contents) )

    def register_element( self, ident, ele, dident=None ):
        # dident is an element itent for this element's destination.
        self.elements[ident] = ele
        if dident:
            mydest = self.elements.get(dident)
            if mydest:
                self.move_element( ele, mydest )
        return ele

    def seek_element( self, nart, ident, seek_func, dident=None, scope=None, must_find=True, check_subscenes=True ):
        """Check scope and all children for a gear that seek_func returns True"""
        if not scope:
            scope = nart.camp
        candidates = list()
        for e in all_contents( scope, check_subscenes ):
            if seek_func( e ):
                candidates.append( e )
        if candidates:
            e = random.choice( candidates )
            self.register_element( ident, e, dident )
            return e
        elif must_find:
            self.fail( nart )

    def register_scene( self, nart, myscene, mygen, ident=None, dident=None, rank=None ):
        if not myscene.name:
            myscene.name = namegen.DEFAULT.gen_word()
        if not dident:
            if self.chapter and self.chapter.world:
                self.chapter.world.contents.append( myscene )
                self.move_records.append( (myscene,self.chapter.world.contents) )
            else:
                nart.camp.contents.append( myscene )
                self.move_records.append( (myscene,nart.camp.contents) )
        self.register_element( ident, myscene, dident )
        nart.generators.append( mygen )
        self.move_records.append( (mygen,nart.generators) )
        myscene.rank = rank or self.rank
        return myscene

    def custom_init( self, nart ):
        """Return True if everything ok, or False otherwise."""
        return True

    def remove( self, nart=None ):
        """Remove this plot, including subplots and new elements, from campaign."""
        # First, remove all subplots.
        for sp in self.subplots.itervalues():
            sp.remove( nart )
        # Next, remove any elements created by this plot.
        if hasattr( self, "move_records" ):
            for e,d in self.move_records:
                if e in d:
                    d.remove( e )

        self.__class__._used += -1

        # Remove self from the adventure.
        if hasattr( self, "container" ) and self.container:
            self.container.remove( self )

        # Remove self from the uniques set, if necessary.
        if nart and self.UNIQUE and self.__class__ in nart.camp.uniques:
            nart.camp.uniques.remove( self.__class__ )

    def install( self, nart ):
        """Plot generation complete. Mesh plot with campaign."""
        for sp in self.subplots.itervalues():
            sp.install( nart )
        del self.move_records
        if self.scope:
            dest = self.elements.get( self.scope )
            if dest and hasattr( dest, "scripts" ):
                dest.scripts.append( self )
            else:
                nart.camp.scripts.append( self )

    def display( self, lead="" ):
        print lead + str( self.__class__ )
        for sp in self.subplots.itervalues():
            sp.display(lead+" ")

    def handle_trigger( self, explo, trigger, thing=None ):
        """A trigger has been tripped; make this plot react if appropriate."""
        # The trigger handler will be a method of this plot. If a thing is
        # involved, and that thing is an element, the handler's id will be
        # "[element ident]_[trigger type]". If no thing is involved, the
        # trigger handler will be "t_[trigger type]".
        # Trigger handler methods take the Exploration as a parameter.
        if thing:
            if thing is self:
                handler = getattr( self, "SELF_{0}".format( trigger ), None )
                if handler:
                    handler( explo )
            idlist = self.get_element_idents( thing )
            for label in idlist:
                handler = getattr( self, "{0}_{1}".format( label, trigger ), None )
                if handler:
                    handler( explo )
        else:
            handler = getattr( self, "t_{0}".format( trigger ), None )
            if handler:
                handler( explo )

    def get_dialogue_offers( self, npc, explo ):
        """Get any dialogue offers this plot has for npc."""
        # Method [ELEMENTID]_offers will be called. This method should return a
        # list of offers to be built into the conversation.
        ofrz = self.get_generic_offers( npc, explo )
        npc_ids = self.get_element_idents( npc )
        for i in npc_ids:
            ogen = getattr( self, "{0}_offers".format(i), None )
            if ogen:
                ofrz += ogen( explo )
        return ofrz

    def modify_puzzle_menu( self, thing, thingmenu ):
        """Modify the thingmenu based on this plot."""
        # Method [ELEMENTID]_menu will be called with the menu as parameter.
        # This method should modify the menu as needed- typically by altering
        # the "desc" property (menu caption) and adding menu items.
        thing_ids = self.get_element_idents( thing )
        for i in thing_ids:
            ogen = getattr( self, "{0}_menu".format(i), None )
            if ogen:
                ogen( thingmenu )

    def get_generic_offers( self, npc, explo ):
        """Get any offers that could apply to non-element NPCs."""
        return list()

    def get_dialogue_grammar( self, npc, explo ):
        """Return any grammar rules appropriate to this situation."""
        return None


    @classmethod
    def matches( self, pstate ):
        """Returns True if this plot matches the current plot state."""
        return True

class NarrativeRequest( object ):
    """The builder class which constructs a story out of individual plots."""
    def __init__( self, camp, pstate, adv_type="ADVENTURE_STUB" ):
        self.camp = camp
        self.generators = list()
        self.errors = list()
        # Add the seed plot.
        self.story = self.generate_sub_plot( pstate, adv_type )

    def random_choice_by_weight( self, candidates ):
        wcan = list()
        for sp in candidates:
            if sp.UNIQUE:
                wcan.append( sp )
            elif sp.COMMON:
                wcan += (sp,sp,sp,sp,sp,sp)
            else:
                wcan += (sp,sp,sp)
        return random.choice( wcan )

    def generate_sub_plot( self, pstate, label ):
        """Locate a plot which matches the request, init it, and return it."""
        # Create a list of potential plots.
        candidates = list()
        for sp in PLOT_LIST[label]:
            if sp.matches( pstate ):
                if not sp.UNIQUE or sp not in self.camp.uniques:
                    candidates.append( sp )
        if candidates:
            cp = None
            while candidates and not cp:
                cpc = self.random_choice_by_weight( candidates )
                candidates.remove( cpc )
                try:
                    cp = cpc(self,pstate)
                    if cpc.UNIQUE:
                        self.camp.uniques.add( cpc )
                except plots.PlotError:
                    cp = None
            if not cp:
                self.errors.append( "No plot accepted for {0}".format( label ) )
            return cp
        else:
            self.errors.append( "No plot found for {0}".format( label ) )

    def get_map_generator( self, gb ):
        # I thought that generators should be changed to a dict, but then I
        # noticed that the generator also gets recorded in a plot's move_records.
        # So, changing it to a dict would require a workaround for that.
        # For now I'm just going to leave this inefficiency in.
        mygen = None
        for mg in self.generators:
            if mg.gb == gb:
                mygen = mg
                break
        return mygen

    def build( self ):
        """Build finished campaign from this narrative."""
        for g in self.generators:
            g.make()
        self.story.install( self )




