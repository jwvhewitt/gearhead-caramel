
class RetroGear( object ):
    # A container for gear info.
    def __init__(self, g,s,v,scale):
        self.g = g
        self.s = s
        self.v = v
        self.scale = scale
        self.natt = dict()
        self.satt = dict()
        self sub_com = list()
        self.inv_com = list()

class GH1Loader( object ):
    # Class to load and parse a GearHead1 (aka GearHead Arena) save file.
    def __init__( self, fname ):
        self.fname = fname

    def _read_map(self,myfile):
        # Since we aren't keeping the map, just advance myfile to the end of
        # the map block.
	    #{First, get rid of the descriptive message & the dimensions.}
        myfile.readline()
        x_max = int(myfile.readline())
        y_max = int(myfile.readline())
        tile = 0
        # Read the terrain
        while tile < x_max * y_max:
            count = int(myfile.readline())
            terrain = myfile.readline()
            tile += count
            if len(terrain)<1:
                break
        # Read the second descriptive label
        myfile.readline()
        # Read the visibility
        tile = 0
        while tile < x_max * y_max:
            count = myfile.readline()
            if len(count)<1:
                break
            else:
                tile += int(count)

    SAVE_FILE_CONTINUE = 0
    SAVE_FILE_SENTINEL = -1

    def _extract_value(self,myline):
        bits = myline.split(maxsplit=1)
        if bits:
            v = int(bits[0])
            if len(bits) > 1:
                return v, bits[1]
            else:
                return v, ''
        else:
            return -1, ''

    def _load_gears(self,myfile):
        # Start reading, and keep going until we reach the save file sentinel
        # or end of file.
        keep_going = True
        mylist = list()
        while keep_going:
            rawline = g_file.readline()

            if len(rawline) < 1:
                # Conveniently, a blank line is both the Python end of file
                # indicator and a halting error in GearHead1.
                keep_going = False
            else:
                # This line should contain an "action code".
                n,myline = self._extract_value(rawline)
                if n == self.SAVE_FILE_CONTINUE:
                    # This is a gear.
                    g,myline = self._extract_value(myline)
                    s,myline = self._extract_value(myline)
                    v,myline = self._extract_value(myline)
                    scale,myline = self._extract_value(myline)

                    mygear = RetroGear(g,s,v,scale)
                    mylist.append(mygear)

                    mygear.natt = self._read_numeric_attributes(myfile)

                elif n == self.SAVE_FILE_SENTINEL:
                    keep_going = False
                else:
                    print "GH1Loader Error... no idea what action code {} is.".format(n)

        return mylist

    def _load_list(self,myfile):
        # Load a GH1 RPG_*.txt save file, and extract the useful bits.
        # Map definitions and anything we don't want just gets tossed.

        # Read the comtime and map scale. Promptly throw them out.
        myfile.readline()
        myfile.readline()

        # Read the current map. Throw it out as well.
        self._read_map(myfile)

        # Load the scene index. Throw it out.
        myfile.readline()

        # Load the contents of the current scene.
        mylist = self._load_gears(myfile)



    def load( self ):
        with open(self.fname,'rb') as f:
            mylist = self._load_list(f)
        return mylist


