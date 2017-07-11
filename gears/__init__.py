import base
import calibre
import damage
import materials
import scale

import inspect
import re

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

class Loader( list ):
    def __init__( self, fname ):
        self.fname = fname

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

                elif "=" in line:
                    # This is a dict line. Add to the current_dict.
                    a,b,c = line.partition('=')
                    rawkey = a.strip()
                    rawval = c.strip()
                    if rawval:
                        # The value of the dictionary entry may need some decoding.
                        if rawval[0] in ( '"' , "'" ):
                            # This is a literal string. Get rid of the quotes.
                            truval = rawval.strip( '"\'' )
                        elif rawval.isdigit():
                            # This is presumably a number. Convert.
                            truval = int( rawval )

                        elif rawval in SINGLETON_TYPES:
                            # This is a named constant of some type.
                            truval = SINGLETON_TYPES[ rawval ]
                        else:
                            # This is a string. Leave it alone.
                            truval = rawval

                        current_gear.gparam[ rawkey ] = truval

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



