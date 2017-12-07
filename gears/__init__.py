import pbge

import base
import calibre
import damage
import materials
import scale
import stats
import geffects
import info

import inspect
import re
from numbers import Number

GEAR_TYPES = dict()
SINGLETON_TYPES = dict()

def harvest( mod, subclass_of, dict_to_add_to, exclude_these ):
    for name in dir( mod ):
        o = getattr( mod, name )
        if inspect.isclass( o ) and issubclass( o , subclass_of ) and o not in exclude_these:
            dict_to_add_to[ o.__name__ ] = o

harvest( base, base.BaseGear, GEAR_TYPES, (base.BaseGear,base.MovementSystem,base.Weapon,base.Usable))
harvest( scale, scale.MechaScale, SINGLETON_TYPES, () )
harvest( base, base.ModuleForm, SINGLETON_TYPES, (base.ModuleForm,) )
harvest( materials, materials.Material, SINGLETON_TYPES, (materials.Material,) )
harvest( calibre, calibre.BaseCalibre, SINGLETON_TYPES, (calibre.BaseCalibre,) )
harvest( base, base.MT_Battroid, SINGLETON_TYPES, () )
SINGLETON_TYPES['None'] = None
harvest( stats, stats.Stat, SINGLETON_TYPES, (stats.Stat,) )
harvest( stats, stats.Skill, SINGLETON_TYPES, (stats.Skill,) )
harvest( geffects, pbge.scenes.animobs.AnimOb,SINGLETON_TYPES, ())

class GearHeadScene( pbge.scenes.Scene ):
    def is_an_actor( self, model ):
        return isinstance(model,(base.Mecha,base.Character))
    def get_actors( self, pos ):
        return [a for a in self._contents if (self.is_an_actor(a) and (a.pos == pos)) ]
    def get_blocked_tiles( self ):
        return {a.pos for a in self._contents if (self.is_an_actor(a) and a.is_operational()) }

class GearHeadCampaign( pbge.campaign.Campaign ):
    fight = None
    def first_active_pc( self ):
        # The first active PC is the first PC in the party list who is
        # both operational and on the map.
        flp = None
        for pc in self.party:
            if pc.is_operational() and pc in self.scene._contents:
                flp = pc
                break
        return flp


# Why did I create this complicated regular expression to parse lines of
# the form "a = b"? I guess I didn't know about string.partition at the time.
# Anyhow, I'm leaving this here as a comment to remind me of the dangers of
# overengineering. Also in case I ever need it again because I don't really
# remember how regular expressions work and this looks complicated as heck.
#DICT_UNPACKER = re.compile( r'["\']?(\w+)["\']?\s?=\s?([\w"\']+)' )


class ProtoGear( object ):
    """Used by the loader to hold gear definitions before creating the actual gear."""
    def __init__(self,gclass):
        self.gclass = gclass
        self.gparam = dict()
        self.sub_com = list()
        self.inv_com = list()

class Loader( object ):
    def __init__( self, fname ):
        self.fname = fname

    def process_list( self, string ):
        # This string describes a list. There may be additional lists in
        # the list. Deal with that.
        current_list = None
        stack = []
        start_token = -1
        for i, c in enumerate(string):
            if c in '([':
                # Begin a new list
                nulist = list()
                if current_list is not None:
                    stack.append(current_list)
                    current_list.append( nulist )
                current_list = nulist
                start_token = i + 1
            elif c in ')]':
                # Pop out to previous list
                if start_token < i:
                    toke = string[start_token:i]
                    current_list.append(self.string_to_object(toke))
                if stack:
                    current_list = stack.pop()
                start_token=i+1
            elif c == ',':
                # Store the current item in the list
                toke = string[start_token:i]
                if toke:
                    current_list.append(self.string_to_object(toke))
                start_token=i+1
        return current_list


    def string_to_object( self, string ):
        # Given a string, return the game object it represents.
        rawval = string.strip()
        if rawval:
            if rawval[0] in ( '"' , "'" ):
                # This is a literal string. Get rid of the quotes.
                truval = rawval.strip( '"\'' )
            elif rawval[0] in '([':
                # Happy Happy Joy Joy it's a fucking list
                truval = self.process_list( rawval )
            elif rawval.isdigit():
                # This is presumably a number. Convert.
                truval = int( rawval )

            elif rawval in SINGLETON_TYPES:
                # This is a named constant of some type.
                truval = SINGLETON_TYPES[ rawval ]
            else:
                # This is a string. Leave it alone.
                truval = rawval
            return truval

    def process_dict( self, dict_desc ):
        mydict = dict()
        # Is this really the best way to get rid of the brackets?
        # Probably not. Somebody Python this up, please.
        dict_desc = dict_desc.replace('{','')
        dict_desc = dict_desc.replace('}','')
        print dict_desc
        for line in dict_desc.split(','):
            a,b,c = line.partition('=')
            k = self.string_to_object(a)
            v = self.string_to_object(c)
            if k and v:
                mydict[ k ] = v
        return mydict


    def load_list( self , g_file ):
        """Given an open file, load the text and return the list of proto-gears"""
        # If it is a command, do that command.
        # If it has an =, add it to the dict
        # Otherwise, check to see if it's a Gear
        masterlist = list()
        current_gear = None
        keep_going = True

        while keep_going:
            rawline = g_file.readline()
            line = rawline.strip()
            if len( line ) > 0:
                if line[0] == "#":
                    # This line is a comment. Ignore.
                    pass

                elif "{" in line:
                    # This is the start of a dictionary.
                    # Load the rest of the dict from the file,
                    # then pass it to the dictionary expander.
                    a,b,c = line.partition('=')
                    k = self.string_to_object(a)
                    my_dict_lines = [c,]
                    while "}" not in my_dict_lines[-1]:
                        nuline = g_file.readline()
                        if nuline:
                            my_dict_lines.append(nuline)
                        else:
                            break
                    v = self.process_dict( ' '.join(my_dict_lines) )
                    print k, '=', v
                    if k and v:
                        current_gear.gparam[ k ] = v

                elif "=" in line:
                    # This is a dict line. Add to the current_dict.
                    a,b,c = line.partition('=')
                    k = self.string_to_object(a)
                    v = self.string_to_object(c)
                    if k and v:
                        current_gear.gparam[ k ] = v

                elif line in GEAR_TYPES:
                    # This is a new gear.
                    current_gear = ProtoGear( GEAR_TYPES[line] )
                    masterlist.append( current_gear )

                elif line == "SUB":
                    # This is a SUB command.
                    current_gear.sub_com = self.load_list( g_file )
                elif line == "INV":
                    # This is a INV command.
                    current_gear.inv_com = self.load_list( g_file )
                elif line == "END":
                    keep_going = False
            elif not rawline:
                keep_going = False

        return masterlist

    def convert( self, protolist ):
        # Convert the provided list to gears.
        mylist = list()
        for pg in protolist:
            my_subs = self.convert( pg.sub_com )
            my_invs = self.convert( pg.inv_com )
            mygear = pg.gclass( sub_com=my_subs, inv_com=my_invs, **pg.gparam )
            mylist.append( mygear )
        return mylist

    def load( self ):
        with open(self.fname,'rb') as f:
            mylist = self.load_list(f)
        return self.convert( mylist )

class Saver( object ):
    """Used to save a gear structure to disk in a human-readable format."""
    def __init__( self, fname ):
        self.fname = fname

    def hashable_to_string( self, wotzit ):
        # Given wotzit, return the string to be output to the file.
        if wotzit is None:
            return 'None'
        elif wotzit in SINGLETON_TYPES.values():
            return wotzit.__name__
        elif isinstance( wotzit, str ) and wotzit not in SINGLETON_TYPES and ' ' not in wotzit:
            return wotzit
        elif isinstance( wotzit, dict ):
            mylist = list()
            for k,v in wotzit.iteritems():
                mylist.append( self.hashable_to_string(k)+' = '+self.hashable_to_string(v) )
            return '{' + ', '.join(mylist) + '}'
        else:
            return repr( wotzit )

    def save_list( self, f, glist, indent='' ):
        for save_the_gear in glist:
            if save_the_gear.__class__.__name__ in GEAR_TYPES:
                # We only save things we can reconstruct.
                f.write('{}{}\n'.format(indent,save_the_gear.__class__.__name__))

                # Go through the ancestors, see what attributes need saving.
                my_params = set()
                for ancestor in save_the_gear.__class__.__mro__:
                    if hasattr( ancestor, 'SAVE_PARAMETERS' ):
                        my_params.update( ancestor.SAVE_PARAMETERS )

                for p in my_params:
                    k = self.hashable_to_string( p )
                    if hasattr( save_the_gear, k ):
                        v = self.hashable_to_string( getattr(save_the_gear,k) )
                        f.write('{}  {} = {}\n'.format(indent,k,v))

                if save_the_gear.sub_com:
                    f.write('{}  SUB\n'.format(indent))
                    self.save_list(f,save_the_gear.sub_com,indent+'    ')
                    f.write('{}  END\n'.format(indent))

                if save_the_gear.inv_com:
                    f.write('{}  SUB\n'.format(indent))
                    self.save_list(f,save_the_gear.inv_com,indent+'    ')
                    f.write('{}  END\n'.format(indent))


    def save( self, glist ):
        with open(self.fname,'wb') as f:
            self.save_list(f,glist)



