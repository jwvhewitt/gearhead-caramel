import collections

import pbge.container


class VariableDefinition(object):
    def __init__(self, default_val=0, var_type="integer", **kwargs):
        self.default_val = default_val
        self.var_type = var_type
        self.data = kwargs.copy()


class ElementDefinition(object):
    def __init__(self, name, e_type="misc", **kwargs):
        self.name = name
        self.e_type = e_type
        self.etc = kwargs


class PlotBrick(object):
    def __init__(self, name="", desc="", scripts=None, vars=None, child_types=(), elements=None, is_new_branch=False, **kwargs):
        self.name = name
        self.desc = desc
        self.scripts = dict()
        if scripts:
            self.scripts.update(scripts)
        self.vars = dict()
        if vars:
            for k, v in vars.items():
                self.vars[k] = VariableDefinition(**v)
        self.child_types = list(child_types)
        self.elements = dict()
        if elements:
            for k,v in elements.items():
                self.elements[k] = ElementDefinition(**v)
        self.is_new_branch = is_new_branch
        self.data = kwargs.copy()


    def get_default_vars(self):
        myvars = dict()
        for k,v in self.vars.items():
            myvars[k] = v.default_val
        return myvars

class BluePrint(object):
    def __init__(self, brick: PlotBrick):
        self._brick_name = brick.name
        self.brick = brick

        self.children = pbge.container.ContainerList(owner=self)
        self.vars = brick.get_default_vars()
        self._uid = 0

    def get_save_dict(self):
        mydict = dict()
        mydict["brick"] = self._brick_name
        mydict["uid"] = self._uid
        mydict["vars"] = self.vars
        mydict["children"] = list()
        if hasattr(self, "max_uid"):
            mydict["max_uid"] = self.max_uid
        for c in self.children:
            mydict["children"].append(c.get_save_dict())
        return mydict

    @classmethod
    def load_save_dict(cls, jdict: dict):
        mybrick = BRICKS_BY_NAME[jdict["brick"]]
        mybp = cls(mybrick)
        mybp._uid = jdict["uid"]
        mybp.vars.update(jdict["vars"])
        if "max_uid" in jdict:
            mybp.max_uid = jdict["max_uid"]
        for cdict in jdict["children"]:
            mybp.children.append(cls.load_save_dict(cdict))
        return mybp

    def get_section(self, section_name, my_scripts, child_scripts, prefix, touched_scripts, done_scripts, used_scripts):
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
                    new_prefix = prefix + " " * n
                    new_section_name = script_line[n+2:].strip()
                    insert_lines = self.get_section(new_section_name, my_scripts, child_scripts, new_prefix, touched_scripts, done_scripts, used_scripts)
                    done_scripts[section_name] += insert_lines
                    used_scripts.add(new_section_name)
                else:
                    done_scripts[section_name].append(prefix + script_line)

        for script_line in child_scripts.get(section_name, ()):
            done_scripts[section_name].append(prefix + script_line)

        return done_scripts[section_name]

    def get_ultra_vars(self):
        # Return all variables readable by this blueprint, including the _uid.
        vars = dict()
        my_ancestors = list(self.ancestors())
        my_ancestors.reverse()
        for a in my_ancestors:
            vars.update(a.vars)
        vars.update(self.vars)
        vars["_uid"] = self.uid
        return vars

    def compile(self, inherited_vars=None):
        # Return a dict of Python scripts to be added to the output file.
        if inherited_vars:
            vars = inherited_vars.copy()
        else:
            vars = dict()
        vars.update(self.vars)

        ultravars = vars.copy()
        ultravars["_uid"] = self.uid

        # Step one: collect the scripts from all children.
        mykids = collections.defaultdict(list)
        for kid in self.children:
            kid_scripts = kid.compile(inherited_vars=vars)
            for k,v in kid_scripts.items():
                mykids[k] += v

        # Step two: collect the default scripts from the brick.
        myscripts = self.brick.scripts.copy()
        for k,v in myscripts.items():
            myscripts[k] = v.format(**ultravars)

        touchedscripts = set()
        donescripts = collections.defaultdict(list)
        usedscripts = set()
        for k in myscripts.keys():
            self.get_section(k, myscripts, mykids, "", touchedscripts, donescripts, usedscripts)

        for k in mykids.keys():
            if k not in donescripts:
                self.get_section(k, myscripts, mykids, "", touchedscripts, donescripts, usedscripts)

        for k in usedscripts:
            if k in donescripts:
                del donescripts[k]

        return donescripts

    # Gonna set up the brick as a property.
    def _get_brick(self):
        return BRICKS_BY_NAME.get(self._brick_name,None)

    def _set_brick(self,nuval):
        self._brick_name = nuval.name

    def _del_brick(self):
        self._brick_name = None

    brick = property(_get_brick,_set_brick,_del_brick)

    def _get_name(self):
        return self._brick_name

    name = property(_get_name)

    def get_root(self):
        if hasattr(self, "container") and self.container:
            return self.container.owner.get_root()
        else:
            return self

    def ancestors(self):
        if hasattr(self, "container") and self.container:
            yield self.container.owner
            for p in self.container.owner.ancestors():
                yield p

    def predecessors(self):
        if hasattr(self, "container") and self.container:
            yield self.container.owner
            for p in self.container.owner.children:
                if p is self:
                    break
                elif not p.brick.is_new_branch:
                    yield p
            for p in self.container.owner.predecessors():
                yield p

    def _get_uid(self):
        if self._uid != 0:
            return self._uid
        else:
            myroot = self.get_root()
            if hasattr(myroot, "max_uid"):
                myroot.max_uid += 1
            else:
                myroot.max_uid = 1
            self._uid = myroot.max_uid
            return self._uid

    uid = property(_get_uid)

    def get_elements(self):
        # Return a dict of elements accessible from this block.
        # key = element_ID
        # value = ElementDefinition
        elements = dict()
        my_ancestors = list(self.predecessors())
        my_ancestors.reverse()
        for a in my_ancestors:
            avars = a.get_ultra_vars()
            for k,v in a.brick.elements.items():
                elements[k.format(**avars)] = ElementDefinition(v.name.format(**avars), e_type=v.e_type)

        avars = self.get_ultra_vars()
        for k,v in self.brick.elements.items():
            elements[k.format(**avars)] = ElementDefinition(v.name.format(**avars), e_type=v.e_type)

        return elements


ALL_BRICKS = list()
BRICKS_BY_LABEL = collections.defaultdict(list)
BRICKS_BY_NAME = dict()