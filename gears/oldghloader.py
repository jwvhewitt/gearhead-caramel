import glob
import pbge
import os
import stats


class RetroGear( object ):
    # A container for gear info.
    def __init__(self, g,s,v,scale):
        self.g = g
        self.s = s
        self.v = v
        self.scale = scale
        self.natt = dict()
        self.satt = dict()
        self.sub_com = list()
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

    #  **************************************
    #  ***   GEARHEAD  ARENA  CONSTANTS   ***
    #  **************************************

    GG_CHARACTER = 2
    NAG_LOCATION = -1
    NAS_TEAM = 4
    NAV_DEFPLAYERTEAM = 1

    NAG_SKILL = 1
    NAS_MECHAGUNNERY = 1
    NAS_MECHAARTILLERY = 2
    NAS_MECHAWEAPONS = 3
    NAS_MECHAFIGHTING = 4
    NAS_MECHAPILOTING = 5
    NAS_SMALLARMS = 6
    NAS_HEAVYWEAPONS = 7
    NAS_ARMEDCOMBAT = 8
    NAS_MARTIALARTS = 9
    NAS_DODGE = 10
    NAS_AWARENESS = 11
    NAS_INITIATIVE = 12
    NAS_VITALITY = 13
    NAS_SURVIVAL = 14
    NAS_MECHAREPAIR = 15
    NAS_MEDICINE = 16
    NAS_ELECTRONICWARFARE = 17
    NAS_SPOTWEAKNESS = 18
    NAS_CONVERSATION = 19
    NAS_FIRSTAID = 20
    NAS_SHOPPING = 21
    NAS_BIOTECHNOLOGY = 22
    NAS_GENERALREPAIR = 23
    NAS_CYBERTECH = 24
    NAS_STEALTH = 25
    NAS_ATHLETICS = 26
    NAS_FLIRTATION = 27
    NAS_INTIMIDATION = 28
    NAS_SCIENCE = 29
    NAS_CONCENTRATION = 30
    NAS_MECHAENGINEERING = 31
    NAS_CODEBREAKING = 32
    NAS_WEIGHTLIFTING = 33
    NAS_MYSTICISM = 34
    NAS_PERFORMANCE = 35
    NAS_RESISTANCE = 36
    NAS_INVESTIGATION = 37
    NAS_ROBOTICS = 38
    NAS_LEADERSHIP = 39
    NAS_DOMINATEANIMAL = 40
    NAS_PICKPOCKETS = 41

    NAG_CHARDESCRIPTION = 3
    NAS_HEROIC = -1
    NAS_LAWFUL = -2
    NAS_SOCIABLE = -3
    NAS_EASYGOING = -4
    NAS_CHEERFUL = -5
    NAS_RENOWNED = -6
    NAS_PRAGMATIC = -7

    SAVE_FILE_CONTINUE = 0
    SAVE_FILE_SENTINEL = -1

    def _extract_value(self,myline):
        bits = myline.split(None,1)
        if bits:
            v = int(bits[0])
            if len(bits) > 1:
                return v, bits[1]
            else:
                return v, ''
        else:
            return -1, ''

    def _read_numeric_attributes(self,myfile):
        # Return the dict of numeric attributes.
        mydict = dict()
        keep_going = True
        while keep_going:
            rawline = myfile.readline()

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
                    mydict[(g,s)] = v

                elif n == self.SAVE_FILE_SENTINEL:
                    keep_going = False
                else:
                    print "GH1Loader Error... no idea what action code {} is.".format(n)
        return mydict

    def _read_string_attributes(self,myfile):
        # Return the dict of string attributes.
        mydict = dict()
        keep_going = True
        while keep_going:
            rawline = myfile.readline()

            if len(rawline) < 1 or '<' not in rawline:
                # Conveniently, a blank line is both the Python end of file
                # indicator and a halting error in GearHead1.
                keep_going = False
            else:
                k,raw_v = rawline.split(None,1)
                v = raw_v.strip().strip('<>')
                mydict[k.upper()] = v

        return mydict

    def _process_stat_line(self,rawline):
        mydict = dict()
        stat_stuff = rawline.split()
        del stat_stuff[0]
        mystat = -1
        for s in stat_stuff:
            if mystat is -1:
                mystat = int(s)
            else:
                mydict[mystat] = int(s)
                mystat = -1
        return mydict

    def _load_gears(self,myfile):
        # Start reading, and keep going until we reach the save file sentinel
        # or end of file.
        keep_going = True
        mylist = list()
        while keep_going:
            rawline = myfile.readline()

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

                    # Read the stats line.
                    rawline = myfile.readline()
                    mygear.stats = self._process_stat_line(rawline)

                    mygear.natt = self._read_numeric_attributes(myfile)
                    mygear.satt = self._read_string_attributes(myfile)
                    mygear.inv_com = self._load_gears(myfile)
                    mygear.sub_com = self._load_gears(myfile)

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

        # Load the contents of the current gameboard.
        self.gb_contents = self._load_gears(myfile)


    @classmethod
    def all_gears( self, mylist ):
        # Cycle through all the gears in this tree.
        for gear in mylist:
            yield gear
            if gear.sub_com:
                for p in self.all_gears(gear.sub_com):
                    yield p
            if gear.inv_com:
                for p in self.all_gears(gear.inv_com):
                    yield p

    def find_pc( self ):
        pc = None
        for mpc in self.all_gears(self.gb_contents):
            if mpc.g == self.GG_CHARACTER and mpc.natt.get((self.NAG_LOCATION,self.NAS_TEAM)) == self.NAV_DEFPLAYERTEAM:
                pc = mpc
        return pc

    def convert_character( self, pc ):
        # Convert a character from GH1 rules to GearHead Caramel rules.
        statline = dict()
        t = 1
        for stat in stats.PRIMARY_STATS:
            statline[stat] = pc.stats.get(t,10)
            t += 1
            print '{} = {}'.format(stat.name,statline[stat])

        # Convert the skills. MechaGunnery is max of MechaGunnery, MechaArtillery
        statline[stats.MechaGunnery] = max(pc.natt.get((self.NAG_SKILL,self.NAS_MECHAGUNNERY),0),pc.natt.get((self.NAG_SKILL,self.NAS_MECHAARTILLERY),0))
        statline[stats.MechaFighting] = max(pc.natt.get((self.NAG_SKILL,self.NAS_MECHAWEAPONS),0),pc.natt.get((self.NAG_SKILL,self.NAS_MECHAFIGHTING),0))
        statline[stats.MechaPiloting] = pc.natt.get((self.NAG_SKILL,self.NAS_MECHAPILOTING),0)
        statline[stats.RangedCombat] = max(pc.natt.get((self.NAG_SKILL,self.NAS_SMALLARMS),0),pc.natt.get((self.NAG_SKILL,self.NAS_HEAVYWEAPONS),0))
        statline[stats.CloseCombat] = max(pc.natt.get((self.NAG_SKILL,self.NAS_ARMEDCOMBAT),0),pc.natt.get((self.NAG_SKILL,self.NAS_MARTIALARTS),0))
        statline[stats.Dodge] = pc.natt.get((self.NAG_SKILL,self.NAS_DODGE),0)
        statline[stats.Repair] = max(pc.natt.get((self.NAG_SKILL,self.NAS_MECHAREPAIR),0),pc.natt.get((self.NAG_SKILL,self.NAS_GENERALREPAIR),0))
        statline[stats.Medicine] = max(pc.natt.get((self.NAG_SKILL,self.NAS_MEDICINE),0),pc.natt.get((self.NAG_SKILL,self.NAS_FIRSTAID),0),pc.natt.get((self.NAG_SKILL,self.NAS_CYBERTECH),0))
        statline[stats.Biotech] = pc.natt.get((self.NAG_SKILL,self.NAS_BIOTECHNOLOGY),0)
        statline[stats.Stealth] = max(pc.natt.get((self.NAG_SKILL,self.NAS_STEALTH),0),pc.natt.get((self.NAG_SKILL,self.NAS_PICKPOCKETS),0))
        statline[stats.Science] = max(pc.natt.get((self.NAG_SKILL,self.NAS_SCIENCE),0),pc.natt.get((self.NAG_SKILL,self.NAS_MECHAENGINEERING),0),pc.natt.get((self.NAG_SKILL,self.NAS_ROBOTICS),0))
        statline[stats.Computers] = max(pc.natt.get((self.NAG_SKILL,self.NAS_ELECTRONICWARFARE),0),pc.natt.get((self.NAG_SKILL,self.NAS_CODEBREAKING),0))
        statline[stats.Performance] = pc.natt.get((self.NAG_SKILL,self.NAS_PERFORMANCE),0)
        statline[stats.Negotiation] = max(pc.natt.get((self.NAG_SKILL,self.NAS_CONVERSATION),0),pc.natt.get((self.NAG_SKILL,self.NAS_SHOPPING),0),
            pc.natt.get((self.NAG_SKILL,self.NAS_FLIRTATION),0),pc.natt.get((self.NAG_SKILL,self.NAS_INTIMIDATION),0),pc.natt.get((self.NAG_SKILL,self.NAS_LEADERSHIP),0))
        statline[stats.Scouting] = max(pc.natt.get((self.NAG_SKILL,self.NAS_AWARENESS),0),pc.natt.get((self.NAG_SKILL,self.NAS_SURVIVAL),0),pc.natt.get((self.NAG_SKILL,self.NAS_INVESTIGATION),0))
        statline[stats.DominateAnimal] = pc.natt.get((self.NAG_SKILL,self.NAS_DOMINATEANIMAL),0)
        statline[stats.Vitality] = max(pc.natt.get((self.NAG_SKILL,self.NAS_VITALITY),0),pc.natt.get((self.NAG_SKILL,self.NAS_RESISTANCE),0))
        statline[stats.Athletics] = max(pc.natt.get((self.NAG_SKILL,self.NAS_ATHLETICS),0),pc.natt.get((self.NAG_SKILL,self.NAS_WEIGHTLIFTING),0))
        statline[stats.Concentration] = max(pc.natt.get((self.NAG_SKILL,self.NAS_CONCENTRATION),0),pc.natt.get((self.NAG_SKILL,self.NAS_INITIATIVE),0),
            pc.natt.get((self.NAG_SKILL,self.NAS_SPOTWEAKNESS),0),pc.natt.get((self.NAG_SKILL,self.NAS_MYSTICISM),0))

        # Generate the personality.
        personality = list()



    def load( self ):
        with open(self.fname,'rb') as f:
            self._load_list(f)

    @classmethod
    def seek_gh1_files( self ):
        myfiles = list()
        myfiles += glob.glob(pbge.util.user_dir('RPG*.txt'))
        myfiles += glob.glob(pbge.util.user_dir(os.path.join('gharena','RPG*.txt')))
        myfiles += glob.glob(os.path.expanduser(os.path.join('~','.config','gharena','SaveGame','RPG*.txt')))
        myfiles += glob.glob(os.path.expanduser(os.path.join('~','gharena','SaveGame','RPG*.txt')))
        print myfiles
        return myfiles

