import gears
import materials
import re

# Cache the contents of the gears and materials modules, for later use.
GEARS_DIR = dir( gears )
MATERIALS_DIR = dir( materials )

# Generate state constants for the placement mode.
SUB, INV, NEXT = range( 3 )

# Pre-compile our regular expressions.
DICT_UNPACKER = re.compile( r'["\']?(\w+)["\']?\s?=\s?([\w"\']+)' )

class Loader( list ):

    def flush( self ):
        """Move the requested gear to the gear list."""
        if self.gear_class != None:
            fgear = self.gear_class( **self.current_dict )
            self.gear_class = None
            self.current_dict = {}
            self.current_gear = fgear

            if ( self.parent_gear == None ) or ( self.placement_mode == NEXT ):
                self.append( fgear )

    def load( self , g_file ):
        """Given an open file, load the text and store the list of described gears"""
        # If it is a command, do that command.
        # If it has an =, add it to the dict
        # Otherwise, check to see if it's a Gear type

        self.current_gear = None
        self.parent_gear = None
        self.gear_class = None
        self.current_dict = {}
        self.placement_mode = NEXT

        for rawline in g_file:
            line = rawline.strip()
            if len( line ) > 0:
                if line[0] == "#":
                    # This line is a comment. Ignore.
                    pass
                elif "=" in line:
                    # This is a dict line. Add to the current_dict.
                    m = DICT_UNPACKER.match( line )
                    if m != None:
                        # The value of the dictionary entry may need some decoding.
                        rawval = m.group( 2 )
                        if rawval[0] in ( '"' , "'" ):
                            # This is a literal string. Get rid of the quotes.
                            truval = rawval.strip( '"\'' )
                        elif rawval.isdigit():
                            # This is presumably a number. Convert.
                            truval = int( rawval )
                        elif rawval in GEARS_DIR:
                            # This is probably a class. Make an instance.
                            truval = getattr( gears , rawval )()
                        elif rawval in MATERIALS_DIR:
                            # This is a material. Set the correct value.
                            truval = getattr( materials , rawval )
                        else:
                            # This is a string. Leave it alone.
                            truval = rawval

                        self.current_dict[ m.group( 1 ) ] = truval

                elif line in GEARS_DIR:
                    # This is a gear request.
                    self.flush()
                    self.gear_class = getattr( gears , line )
        # Do one last flush at the end of the file, to make sure we got everything.
        self.flush()

def load_file( fname ):
    l = Loader()
    with open( "design/" + fname , "r" ) as gear_file:
        l.load( gear_file )
    return l

if __name__=='__main__':
    vadel = load_file( "Vadel.txt" )
    for g in vadel:
        g.termdump()


