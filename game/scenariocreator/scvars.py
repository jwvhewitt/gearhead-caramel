from . import varwidgets, conditionals, statefinders, worldmapeditor
import pbge
import gears
import copy


class BaseVariableDefinition(object):
    WIDGET_TYPE = None
    DEFAULT_VAR_TYPE = "integer"

    def __init__(self, default_val=0, var_type=None, must_be_defined=False, tooltip="", **kwargs):
        # if must_be_defined is True, this scenario won't compile if the variable is undefined.
        if isinstance(default_val, dict):
            self.default_val = dict()
            self.default_val.update(default_val)
        else:
            self.default_val = default_val
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.must_be_defined = must_be_defined
        self.tooltip = tooltip
        self.data = kwargs.copy()

    def get_widgets(self, part, key, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(self.WIDGET_TYPE(part, key, tooltip=self.tooltip, **kwargs))
        return mylist

    def get_errors(self, part, key):
        # Return a list of strings if there are errors with this variable.
        myerrors = list()
        if self.must_be_defined:
            uvals = part.get_ultra_vars()
            if key not in uvals or not uvals[key]:
                myerrors.append("Variable {} in {} needs a value".format(key, part))
        return myerrors

    @staticmethod
    def format_for_python(value):
        return value


class StringVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "string"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget


class StringLiteralVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "literal"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    @staticmethod
    def format_for_python(value):
        return repr(value)


class StringIdentifierVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "identifier"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        myval = part.get_ultra_vars().get(key, "")
        if not isinstance(myval, str) or not myval.isidentifier():
            myerrors.append("Variable {} in {} is not a valid identifier".format(key, part))

        return myerrors


class IntegerVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "integer"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    @staticmethod
    def format_for_python(value):
        try:
            return int(value)
        except ValueError:
            print("Value error: not an int")
            return 0

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        myval = part.get_ultra_vars().get(key, "")
        try:
            int(myval)
        except ValueError:
            myerrors.append("Variable {} in {} is not an integer".format(key, part))

        return myerrors


class FiniteStateVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
        mystates = [a[1] for a in my_names_and_states]
        mystates.append(None)
        myval = part.get_ultra_vars().get(key, "")
        if myval not in mystates:
            myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors


class FiniteStateListVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.AddRemoveFSOptionsWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
        mystates = [a[1] for a in my_names_and_states]
        mystates.append(None)
        mylist = part.get_ultra_vars().get(key, "")
        for myval in mylist:
            if myval not in mystates:
                myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors


class SceneTagListVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.AddRemoveFSOptionsWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
        mynames = [a[1] for a in my_names_and_states]
        mylist = part.get_ultra_vars().get(key, "")
        for myval in mylist:
            if myval not in mynames:
                myerrors.append("Variable {} in {} has unknown name {}".format(key, part, myval))

        return myerrors

    @staticmethod
    def format_for_python(value):
        mydict = dict(statefinders.get_scene_tags())
        return [mydict[v] for v in value]


class PaletteVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "palette"
    WIDGET_TYPE = varwidgets.PaletteEditorWidget

    def __init__(self, default_val=0, var_type=None, must_be_defined=False, **kwargs):
        try:
            if isinstance(default_val, list) and len(default_val) == 5 and all(
                    [issubclass(p, gears.color.GHGradient) for p in default_val]):
                self._default_val = default_val
            else:
                self._default_val = None
        except TypeError:
            self._default_val = None
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.data = kwargs.copy()
        self.must_be_defined = must_be_defined
        self.tooltip = None

    @property
    def default_val(self):
        if self._default_val:
            return self._default_val
        else:
            return [gears.SINGLETON_REVERSE[c] for c in gears.color.random_building_colors()]

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        mylist = part.raw_vars.get(key, "")
        # mylist = part.get_ultra_vars().get(key, "")
        if not isinstance(mylist, list):
            myerrors.append("Variable {} in {} is not a color list".format(key, part))
        elif len(mylist) < 5:
            myerrors.append("Variable {} in {} has wrong number of colors for a color list".format(key, part))
        elif not all([p in gears.SINGLETON_TYPES for p in mylist]):
            myerrors.append("Variable {} in {} has unknown colors: {}".format(key, part, mylist))

        return myerrors

    @staticmethod
    def format_for_python(value):
        return "(gears.color.{}, gears.color.{}, gears.color.{}, gears.color.{}, gears.color.{})".format(*value)


class MusicVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "music"
    WIDGET_TYPE = varwidgets.MusicEditorWidget

    @classmethod
    def format_for_python(cls, value):
        if value:
            return repr(value)


class ConditionalVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "conditional"

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()

        mylist.append(pbge.widgets.LabelWidget(0, 0, 300, pbge.SMALLFONT.get_linesize(), key, font=pbge.SMALLFONT))

        my_conditions = part.raw_vars.get(key, list())
        for t, item in enumerate(my_conditions):
            if isinstance(item, list):
                # This is an expression.
                mylist.append(varwidgets.ConditionalExpressionEditor(part, key, t, refresh_fun))
            else:
                # This must be a boolean operator.
                mylist.append(varwidgets.BooleanOperatorEditor(part, key, t, refresh_fun))

        mylist.append(pbge.widgets.LabelWidget(
            0, 0, 100, 0, "Add Expression", draw_border=True, on_click=self.add_expression,
            data={"part": part, "key": key, "refresh_fun": refresh_fun}
        ))

        return mylist

    def add_expression(self, wid, ev):
        part = wid.data["part"]
        key = wid.data["key"]
        refresh_fun = wid.data["refresh_fun"]
        my_conditions = part.raw_vars.get(key, list())
        if not isinstance(my_conditions, list):
            my_conditions = list()
            part.raw_vars[key] = my_conditions
        if my_conditions:
            my_conditions.append(conditionals.CONDITIONAL_BOOL_OPS[0])
        my_conditions.append(conditionals.generate_new_conditional_expression(
            conditionals.CONDITIONAL_EXPRESSION_OPS[2]
        ))
        refresh_fun()

    @staticmethod
    def format_for_python(value):
        return conditionals.build_conditional(value)


class DialogueDataVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "dialogue_data"
    WIDGET_TYPE = varwidgets.DialogueOfferDataWidget


class DialogueContextVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "dialogue_context"

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            varwidgets.DialogueContextWidget(
                part, key, lambda v: statefinders.CONTEXT_INFO[v].desc,
                refresh_fun=refresh_fun
            )
        )
        return mylist


class BooleanVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "boolean"
    WIDGET_TYPE = varwidgets.BoolEditorWidget

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            self.WIDGET_TYPE(part, key, bool(part.raw_vars.get(key)))
        )
        return mylist

    @staticmethod
    def format_for_python(value):
        try:
            return bool(value)
        except ValueError:
            print("Value error: not an bool")
            return False


class CampaignVariableVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "campaign_variable"
    WIDGET_TYPE = varwidgets.CampaignVarNameWidget

    @staticmethod
    def format_for_python(value):
        return repr(value)


class TextVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "text"
    WIDGET_TYPE = varwidgets.TextVarEditorWidget

    def get_widgets(self, part, key, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            self.WIDGET_TYPE(part, key, str(part.raw_vars.get(key)))
        )
        return mylist

    @staticmethod
    def format_for_python(value):
        return repr(value)


class WorldMapDataVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "world_map_data"

    def __init__(self, default_val, **kwargs):
        super().__init__(default_val, **kwargs)

    def get_default_val(self):
        return {"node": {"pos": [0, 0]}, "edges": []}

    def set_default_val(self, new_value):
        pass

    default_val = property(get_default_val, set_default_val)

    def get_widgets(self, part, key, editor=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        if part.raw_vars.get("entrance_world_map"):
            mylist.append(
                pbge.widgets.LabelWidget(0, 0, 350, 0, "Open World Map Editor", font=pbge.MEDIUMFONT, draw_border=True,
                                         on_click=self._open_world_map_editor, data=(part, key, editor))
            )
        return mylist

    def _open_world_map_editor(self, wid, ev):
        part, key, editor = wid.data
        map_bp = None
        for c in editor.mytree.children:
            if c.brick.name == "New World Map" and worldmapeditor.world_map_id(c) == part.raw_vars["entrance_world_map"]:
                map_bp = c
                break
        # We now have enough information to open up the world map editor.
        worldmapeditor.WorldMapEditor.create_and_invoke(pbge.my_state.view, editor, map_bp)

    def _node_parameters_ok(self, node_dict):
        if "pos" not in node_dict:
            return False
        for k,v in node_dict.items():
            if k == "pos":
                if not(isinstance(v, (list, tuple)) and len(v) == 2 and all([isinstance(a, int) for a in v])):
                    return False
            elif k == "image_file":
                if not(isinstance(v, str) and v.endswith(".png") and v in pbge.image.glob_images("wm_legend_*.png")):
                    return False
            elif k in ("visible", "discoverable"):
                if not isinstance(v, bool):
                    return False
            elif k in ("on_frame", "off_frame"):
                if not isinstance(v, int):
                    return False
            else:
                return False
        return True

    def _edge_parameters_ok(self, edge_dict, all_connections):
        if isinstance(edge_dict, dict):
            if "end_node" not in edge_dict:
                return False
            for k, v in edge_dict.items():
                if k == "end_node" and v not in all_connections:
                    return False
                elif k in ("visible", "discoverable"):
                    if not isinstance(v, bool):
                        return False
                elif k == "scenegen" and v not in statefinders.SINGULAR_TYPES["scene_generator"]:
                    return False
                elif k == "architecture" and v not in statefinders.SINGULAR_TYPES["architecture"]:
                    return False
                elif k in ("style", "encounter_chance") and not isinstance(v, int):
                    return False
        return True

    def _check_value(self, part, value):
        if isinstance(value, dict) and "node" in value and isinstance(value["node"], dict) and "edges" in value and isinstance(value["edges"], list):
            if self._node_parameters_ok(value["node"]):
                if not value["edges"]:
                    # Empty list is ok.
                    return True
                elif part:
                    all_blueprints = list(part.get_branch(part.get_root()))
                    all_connections = worldmapeditor.get_all_connections(all_blueprints, part.raw_vars.get("entrance_world_map"))
                    return all(self._edge_parameters_ok(ed, all_connections) for ed in value["edges"])
                else:
                    return True

    def get_errors(self, part, key):
        myerrors = list()
        if not self._check_value(part, part.raw_vars.get(key)):
            myerrors.append("ERROR: world_map_data dict {} is not valid.".format(part.raw_vars.get(key)))
        return myerrors

    class WorldMapDataDict(dict):
        def __init__(self, rawdict):
            super().__init__(rawdict)

        @property
        def node_params(self):
            mylist = list()
            mydict = self["node"]
            for k, v in mydict.items():
                if k == "image_file":
                    mylist.append("image_file=\"{}\"".format(v))

                elif k in ("visible", "discoverable", "on_frame", "off_frame"):
                    mylist.append("{}={}".format(k, v))

            return ", ".join(mylist)

        @property
        def node_pos(self):
            return "{}, {}".format(*self["node"]["pos"])

        @property
        def edge_params(self):
            edges_list = list()
            for edge_dict in self["edges"]:
                my_edge = list()
                end_node_id = edge_dict["end_node"]
                my_edge.append("end_entrance=nart.camp.campdata[THE_WORLD].get({})".format(end_node_id))
                for k, v in edge_dict.items():
                    if k in ("visible", "discoverable", "style", "encounter_chance", "scenegen", "architecture"):
                        my_edge.append("{}={}".format(k, v))
                edges_list.append("dict({})".format(", ".join(my_edge)))

            return "[{}]".format(", ".join(edges_list))

    @classmethod
    def format_for_python(cls, value):
        return cls.WorldMapDataDict(value)


def get_variable_definition(default_val=0, var_type="integer", **kwargs):
    if var_type == "text":
        return TextVariable(default_val, **kwargs)
    elif var_type == "literal":
        return StringLiteralVariable(default_val, **kwargs)
    elif var_type == "identifier":
        return StringIdentifierVariable(default_val, **kwargs)
    elif var_type == "campaign_variable":
        return CampaignVariableVariable(default_val, **kwargs)
    elif var_type in ("faction", "scene", "npc", "world_map"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type in statefinders.LIST_TYPES:
        return FiniteStateListVariable(default_val, var_type, **kwargs)
    elif var_type == "scene_tags":
        return SceneTagListVariable(default_val, var_type, **kwargs)
    elif var_type in statefinders.SINGULAR_TYPES:
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.startswith("physical:"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.startswith("terrain:"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.endswith(".png"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type == "boolean":
        return BooleanVariable(default_val, **kwargs)
    elif var_type == "dialogue_context":
        return DialogueContextVariable(default_val, **kwargs)
    elif var_type == "dialogue_data":
        return DialogueDataVariable(default_val, **kwargs)
    elif var_type == "conditional":
        return ConditionalVariable(default_val, **kwargs)
    elif var_type == "music":
        return MusicVariable(default_val, **kwargs)
    elif var_type == "palette":
        return PaletteVariable(default_val, **kwargs)
    elif var_type.startswith("list:"):
        return FiniteStateListVariable(default_val, var_type, **kwargs)
    elif var_type == "integer":
        return IntegerVariable(default_val, **kwargs)
    elif var_type == "world_map_data":
        return WorldMapDataVariable(default_val, **kwargs)
    else:
        if var_type != "string":
            print("Unknown variable type {}; defaulting to string.".format(var_type))
        return StringVariable(default_val, var_type, **kwargs)
