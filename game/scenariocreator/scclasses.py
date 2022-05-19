import collections
import copy

import pbge.container
from . import scvars


class ElementDefinition(object):
    def __init__(self, name, e_type="misc", aliases=(), uid=None, **kwargs):
        # name = Human readable name; may use variables like a script block.
        # aliases = Names used to reference this element by descendant parts. Should be all-caps.
        # uid = The element's unique ID; only provided for "live" elements.
        self.name = name
        self.e_type = e_type
        self.aliases = list(aliases)
        self.etc = kwargs
        self.uid = uid


class PhysicalDefinition(object):
    def __init__(self, the_brick, element_key, parent=None, variable_keys=(), child_keys=(), **kwargs):
        # the_brick = The brick that contains this physical object; used for error checking
        # element_key = The element th is physical definition is based on; must be an element defined in this brick.
        # parent = The element this physical definition will be shown as a child of in the browser; if None or not
        #   found, this physical definition will be shown as a child of World.
        # variable_keys: Which PlotBrick variables are associated with this thing and can be edited in the thing view.
        # child_keys: Which PlotBrick child types are associated with this thing and can be edited in the thing view.
        #   If None, all of the child types will be shown in the thing view.
        self.element_key = element_key
        if element_key and element_key not in the_brick.elements:
            print("Physical Error in {}: Element {} not found".format(the_brick, element_key))
        self.parent = parent
        if parent and parent not in the_brick.elements:
            print("Physical Error in {}: Parent {} not found".format(the_brick, parent))
        self.variable_keys = set(variable_keys)
        if not self.variable_keys.issubset(the_brick.vars.keys()):
            print("Physical Error in {}: Variable keys {} not found".format(
                the_brick, self.variable_keys.difference(the_brick.vars.get_keys())
            ))
        if isinstance(child_keys, (list, tuple, set)):
            self.child_keys = set(child_keys)
            if not self.child_keys.issubset(the_brick.child_types):
                print("Physical Error in {}: Child types {} not found".format(
                    the_brick, self.child_keys.difference(the_brick.child_types)
                ))
        else:
            self.child_keys = None


class PlotBrick(object):
    # label is a string describing what sort of brick this is.
    # name is a unique identifier for this plot brick.
    # desc is a human-readable description of its function, for a certain definition of "human-readable".
    # scripts is a dict containing the scripts that will be placed in the compiled Python script.
    #    key = section name; this determines where the script will be placed.
    #    index = the block of Python code to be inserted.
    # vars: Descriptions for the user-configurable variables of this plot block.
    #    key = variable name. Should be all lowercase.
    #    value = variable description.
    # child_types: List of brick labels that can be added as children of this brick.
    # elements: Descriptions for the elements defined within this brick in dict form.
    #     Element keys should be all uppercase to differentiate them from variable identifiers
    # physicals: Descriptions for the physical objects defined within this brick in list form.
    # is_new_branch: True if this brick begins a new Plot. This is needed to check element + var inheritance.
    def __init__(
            self, label="PLOT_BLOCK", name="", display_name="", desc="", scripts=None, vars=None, child_types=(),
            elements=None, physicals=(), is_new_branch=False, sorting_rank=1000, singular=False, **kwargs
    ):
        self.label = label
        self.name = name
        self.display_name = display_name or name
        self.desc = desc
        self.scripts = dict()
        if scripts:
            self.scripts.update(scripts)
        self.vars = dict()
        if vars:
            for k, v in vars.items():
                self.vars[k] = scvars.get_variable_definition(**v)
        self.child_types = list(child_types)
        self.elements = dict()
        if elements:
            for k,v in elements.items():
                self.elements[k] = ElementDefinition(**v)
        self.physicals = [PhysicalDefinition(self, **v) for v in physicals]
        self.is_new_branch = is_new_branch
        self.sorting_rank = sorting_rank
        self.singular = singular
        self.data = kwargs.copy()

        self._format_scripts()

    def _format_scripts(self):
        if not self.is_new_branch and self.elements:
            if "plot_init" not in self.scripts:
                self.scripts["plot_init"] = ""
            for elemkey, elemdesc in self.elements.items():
                for a in elemdesc.aliases:
                    self.scripts["plot_init"] += "\nelement_alias_list.append(('{}','{}'))".format(a, elemkey)

            for phys in self.physicals:
                self.scripts["plot_init"] += "\n+register_physical {}".format(phys.element_key)

    def get_default_vars(self):
        myvars = dict()
        for k, v in self.vars.items():
            myvars[k] = copy.copy(v.default_val)
        return myvars

    def __str__(self):
        return self.name


class BluePrint(object):
    def __init__(self, brick: PlotBrick, parent, loaded_uid=0, loaded_vars=None):
        if parent:
            parent.children.append(self)
        self._brick_name = brick.name
        self.brick = brick

        self.children = pbge.container.ContainerList(owner=self)
        self.raw_vars = brick.get_default_vars()
        if loaded_vars:
            self.raw_vars.update(loaded_vars)
        self._uid = 0 or loaded_uid

        for k,v in brick.elements.items():
            if self.get_element_uid_var_name(k) not in self.raw_vars:
                self.raw_vars[self.get_element_uid_var_name(k)] = self.new_element_uid()

    def get_element_uid_var_name(self, rawvarname):
        return "{}_UID".format(rawvarname)

    def new_element_uid(self):
        myroot = self.get_root()
        if not hasattr(myroot, "max_element_uid"):
            myroot.max_element_uid = 0
        myroot.max_element_uid += 1
        return repr("{:0=8X}".format(myroot.max_element_uid))

    def get_save_dict(self, include_uid=True):
        mydict = dict()
        mydict["brick"] = self._brick_name
        mydict["vars"] = self.raw_vars
        mydict["children"] = list()
        if include_uid:
            mydict["uid"] = self._uid
            if hasattr(self, "max_uid"):
                mydict["max_uid"] = self.max_uid
            if hasattr(self, "max_element_uid"):
                mydict["max_element_uid"] = self.max_element_uid

        for c in self.children:
            mydict["children"].append(c.get_save_dict(include_uid))
        return mydict

    @classmethod
    def load_save_dict(cls, jdict: dict, parent=None):
        mybrick = BRICKS_BY_NAME[jdict["brick"]]
        mybp = cls(mybrick, parent, loaded_uid=jdict.get("uid", 0), loaded_vars=jdict["vars"])
        if "max_uid" in jdict:
            mybp.max_uid = jdict["max_uid"]
        if "max_element_uid" in jdict:
            mybp.max_element_uid = jdict["max_element_uid"]
        for cdict in jdict["children"]:
            cls.load_save_dict(cdict, mybp)
        mybp.sort()
        return mybp

    def copy(self):
        oldcontainer = getattr(self, "container", None)
        self.container = None
        myclone = copy.deepcopy(self)
        myclone._uid = 0
        self.container = oldcontainer
        return myclone

    def _get_formatted_vars(self):
        # Get vars in the format they need to be in for output to a Python file.
        myvars = dict()
        for k,v in self.raw_vars.items():
            vardef = self.brick.vars.get(k)
            if vardef:
                myvars[k] = vardef.format_for_python(v)
            else:
                myvars[k] = v
        return myvars

    def get_ultra_vars(self):
        # Return all variables readable by this blueprint, including the _uid.
        # Don't pass on private vars- those preceded by an underscore.
        vars = dict()
        my_ancestors = list(self.ancestors())
        my_ancestors.reverse()
        for a in my_ancestors:
            avars = a._get_formatted_vars()
            for k,v in avars.items():
                if not k.startswith("_"):
                    vars[k] = v
            # Add the aliased element UIDs
            for k,v in a.brick.elements.items():
                for alias in v.aliases:
                    vars[a.get_element_uid_var_name(alias)] = avars[a.get_element_uid_var_name(k)]

        vars.update(self._get_formatted_vars())
        vars["_uid"] = self.uid
        return vars

    def compile(self):
        # Return a dict of Python scripts to be added to the output file.
        # Inside the scripts, "#:" marks a place where a block will be inserted.
        ultravars = self.get_ultra_vars()

        # Step one: collect the scripts from all children.
        mykids = collections.defaultdict(str)
        for kid in self.children:
            kid_scripts = kid.compile()
            for k,v in kid_scripts.items():
                mykids[k] += "\n" + v

        # Step two: collect the default scripts from the brick.
        myscripts = self.brick.scripts.copy()
        for k,v in myscripts.items():
            myscripts[k] = v.format(**ultravars)

        to_be_merged = list()

        # Step three: If any of the default scripts have slots for the kid scripts, insert those there.
        for k,v in myscripts.items():
            nuscript = list()
            to_be_processed = v.splitlines()
            while to_be_processed:
                script_line = to_be_processed.pop(0)
                if script_line:
                    if script_line.strip().startswith("#:"):
                        n = script_line.find("#:")
                        prefix = " " * n
                        new_section_name = script_line[n + 2:].strip()

                        if new_section_name in mykids:
                            to_be_processed = ["{}{}".format(prefix, line) for line in mykids[new_section_name].splitlines()] + to_be_processed
                            del mykids[new_section_name]
                        else:
                            # No kids found here... maybe it'll come in handy later?
                            nuscript.append(script_line)

                    elif script_line.strip().startswith("+subplot"):
                        n = script_line.find("+subplot")
                        prefix = " " * n
                        subplot_name = script_line[n + 8:].strip()
                        if subplot_name:
                            nuscript.append(
                                prefix + "self.add_sub_plot(nart, '{}', elements={})".format(
                                    subplot_name,
                                    "dict([(a, self.elements[b]) for a,b in element_alias_list])"
                                )
                            )
                        else:
                            print("Error in {}: No subplot for {}".format(self.brick.name, script_line))

                    elif script_line.strip().startswith("+add_physical"):
                        n = script_line.find("+add_physical")
                        prefix = " " * n
                        element_name, variable_name = script_line[n + 13:].strip().split()
                        if element_name and element_name in self.brick.elements and variable_name.is_identifier():
                            nuscript.append(
                                prefix + "the_world[{}] = {}".format(
                                    ultravars[self.get_element_uid_var_name(element_name)],
                                    variable_name
                                )
                            )
                        else:
                            print("Error in {}: Cannot parse {}".format(self.brick.name, script_line))
                    elif script_line.strip().startswith("+register_physical"):
                        n = script_line.find("+register_physical")
                        prefix = " " * n
                        element_name = script_line[n + 18:].strip()
                        if element_name and element_name in self.brick.elements:
                            nuscript.append(
                                prefix + "self.elements['{}'] = nart.camp.campdata[THE_WORLD][{}]".format(
                                    element_name,
                                    ultravars[self.get_element_uid_var_name(element_name)]
                                )
                            )
                        else:
                            print("Error in {}: Cannot parse {}".format(self.brick.name, script_line))

                    elif script_line.strip().startswith("+init_plot"):
                        n = script_line.find("+init_plot")
                        prefix = " " * n
                        aliases = list()
                        for elemkey, elemdesc in self.brick.elements.items():
                            for a in elemdesc.aliases:
                                aliases.append((a, elemkey))
                        to_be_processed.insert(0, "{}element_alias_list = {}\n".format(prefix, repr(aliases)))

                        for phys in self.brick.physicals:
                            to_be_processed.insert(0, "{}+register_physical {}".format(prefix, phys.element_key))

                    elif script_line.strip().startswith("+"):
                        print("Error in {}: Unknown macro {}".format(self.brick.name, script_line))

                    else:
                        nuscript.append(script_line)

            myscripts[k] = "\n".join(nuscript)

        for k in mykids.keys():
            ms = myscripts.get(k, "")
            ks = mykids.get(k, "")
            if ms or ks:
                myscripts[k] = ms + "\n" + ks

        return myscripts

    # Gonna set up the brick as a property.
    def _get_brick(self):
        return BRICKS_BY_NAME.get(self._brick_name,None)

    def _set_brick(self,nuval):
        self._brick_name = nuval.name

    def _del_brick(self):
        self._brick_name = None

    brick = property(_get_brick,_set_brick,_del_brick)

    def _get_name(self):
        return self.brick.display_name.format(**self.get_ultra_vars())

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

    def get_elements(self, uvars=None):
        # Return a dict of elements accessible from this block.
        # key = element_ID
        # value = ElementDefinition
        elements = dict()
        my_ancestors = list(self.predecessors())
        my_ancestors.reverse()
        for a in my_ancestors:
            avars = a.get_ultra_vars()
            for k,v in a.brick.elements.items():
                elements[k] = ElementDefinition(v.name.format(**avars), e_type=v.e_type, uid=avars[self.get_element_uid_var_name(k)])

        if not uvars:
            uvars = self.get_ultra_vars()
        for k,v in self.brick.elements.items():
            elements[k] = ElementDefinition(v.name.format(**uvars), e_type=v.e_type, uid=uvars[self.get_element_uid_var_name(k)])

        return elements

    def get_campaign_variable_names(self, start_with_root=True):
        myset = set()
        if start_with_root:
            part = self.get_root()
        else:
            part = self
        for k,v in part.brick.vars.items():
            if v.var_type == "campaign_variable":
                myset.add(part.raw_vars.get(k,"x"))
        for p in part.children:
            myset.update(p.get_campaign_variable_names(False))
        return myset

    def sort(self):
        self.children.sort(key=lambda c: c.brick.sorting_rank)
        for c in self.children:
            c.sort()

ALL_BRICKS = list()
BRICKS_BY_LABEL = collections.defaultdict(list)
BRICKS_BY_NAME = dict()