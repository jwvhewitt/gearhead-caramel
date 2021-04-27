import glob
import pbge
import json
import collections


ALL_BRICKS = list()
BRICKS_BY_LABEL = collections.defaultdict(list)
BRICKS_BY_NAME = dict()


class PlotBrick(object):
    def __init__(self, scripts=None, **kwargs):
        self.scripts = dict()
        if scripts:
            self.scripts.update(scripts)
        self.data = kwargs.copy()


class BluePrint(object):
    def __init__(self, brick: PlotBrick):
        self._brick_name = brick.data.get("name")
        self.brick = brick

        self.children = list()
        self.vars = dict()
        self.vars.update(brick.data.get("vars", {}))

    def get_section(self, section_name, my_scripts, child_scripts, prefix, touched_scripts, done_scripts):
        if section_name in touched_scripts:
            if section_name in done_scripts:
                return done_scripts[section_name]
            else:
                print("Error: Circular Reference!")
                return ()
        else:
            touched_scripts.add(section_name)

        mys: str = my_scripts.get(section_name, "")
        for script_line in mys.splitlines():
            if script_line:
                n = script_line.find("#:")
                if n >= 0:
                    print("Adding section..." + script_line)
                    new_prefix = prefix + " " * n
                    new_section_name = script_line[n+2:]
                    insert_lines = self.get_section(new_section_name, my_scripts, child_scripts, new_prefix, touched_scripts, done_scripts)
                    done_scripts[section_name] += insert_lines
                else:
                    done_scripts[section_name].append(prefix + script_line)

        for script_line in child_scripts.get(section_name, ()):
            done_scripts[section_name].append(prefix + script_line)

        return done_scripts[section_name]

    def compile(self, inherited_vars=None):
        # Return a dict of Python scripts to be added to the output file.
        if inherited_vars:
            vars = inherited_vars.copy()
        else:
            vars = dict()
        vars.update(self.vars)

        # Step one: collect the scripts from all children.
        mykids = collections.defaultdict(list)
        for kid in self.children:
            kid_scripts = kid.compile(inherited_vars=vars)
            for k,v in kid_scripts.items():
                mykids[k] += v

        # Step two: collect the default scripts from the brick.
        myscripts = self.brick.scripts.copy()
        for k,v in myscripts.items():
            myscripts[k] = v.format(**self.vars)

        touchedscripts = set()
        donescripts = collections.defaultdict(list)
        for k in myscripts.keys():
            self.get_section(k, myscripts, mykids, "", touchedscripts, donescripts)

        for k in mykids.keys():
            if k not in donescripts:
                self.get_section(k, myscripts, mykids, "", touchedscripts, donescripts)

        return donescripts

    # Gonna set up the brick as a property.
    def _get_brick(self):
        return BRICKS_BY_NAME.get(self._brick_name,None)

    def _set_brick(self,nuval):
        self._brick_name = nuval.data.get("name")

    def _del_brick(self):
        self._brick_name = None

    brick = property(_get_brick,_set_brick,_del_brick)



def init_plotcreator():
    protobits = list()
    myfiles = glob.glob(pbge.util.data_dir( "pb_*.json"))
    for f in myfiles:
        with open(f, 'rt') as fp:
            mylist = json.load(fp)
            if mylist:
                protobits += mylist
    for j in protobits:
        mybrick = PlotBrick(**j)
        ALL_BRICKS.append(mybrick)
        BRICKS_BY_LABEL[j["label"]].append(mybrick)
        if j["name"] in BRICKS_BY_NAME:
            print("Plot Brick Error: Multiple bricks named {}".format(j["name"]))
        BRICKS_BY_NAME[j["name"]] = mybrick

    brick1 = BluePrint(ALL_BRICKS[0])
    brick1.children.append(BluePrint(ALL_BRICKS[1]))
    scripts = brick1.compile()
    for sl in scripts.get("main"):
        print(sl)
