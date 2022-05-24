from . import varwidgets, conditionals, statefinders
import pbge
import gears


class BaseVariableDefinition(object):
    WIDGET_TYPE = None
    DEFAULT_VAR_TYPE = "integer"

    def __init__(self, default_val=0, var_type=None, must_be_defined=False, **kwargs):
        # if must_be_defined is True, this scenario won't compile if the variable is undefined.
        if isinstance(default_val, dict):
            self.default_val = dict()
            self.default_val.update(default_val)
        else:
            self.default_val = default_val
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.must_be_defined = must_be_defined
        self.data = kwargs.copy()

    def get_widgets(self, part, key, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(self.WIDGET_TYPE(part, key, **kwargs))
        return mylist

    def has_valid_value(self, part, key):
        # Return True if this variable has a valid value, or False otherwise.
        uvals = part.get_ultra_vars()
        if key in uvals:
            return key or not self.must_be_defined

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

    def has_valid_value(self, part, key):
        # Return True if this variable has a valid value, or False otherwise.
        uvals = part.get_ultra_vars()
        if key and key in uvals and uvals[key]:
            return uvals[key].isidentifier or not self.must_be_defined


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


class FiniteStateVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget


class FiniteStateListVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.AddRemoveFSOptionsWidget


class PaletteVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "palette"
    WIDGET_TYPE = varwidgets.PaletteEditorWidget

    def __init__(self, default_val=0, var_type=None, **kwargs):
        try:
            if isinstance(default_val, list) and len(default_val) == 5 and all([issubclass(p, gears.color.GHGradient) for p in default_val]):
                self._default_val = default_val
            else:
                self._default_val = None
        except TypeError:
            self._default_val = None
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.data = kwargs.copy()

    @property
    def default_val(self):
        if self._default_val:
            return self._default_val
        else:
            return [gears.SINGLETON_REVERSE[c] for c in gears.color.random_building_colors()]


class MusicVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "music"
    WIDGET_TYPE = varwidgets.MusicEditorWidget


class ConditionalVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "conditional"

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()

        mylist.append(pbge.widgets.LabelWidget(0,0,300,pbge.SMALLFONT.get_linesize(), key, font=pbge.SMALLFONT))

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


def get_variable_definition(default_val=0, var_type="integer", **kwargs):
    if var_type == "text":
        return TextVariable(default_val, **kwargs)
    elif var_type == "literal":
        return StringLiteralVariable(default_val, **kwargs)
    elif var_type == "identifier":
        return StringIdentifierVariable(default_val, **kwargs)
    elif var_type == "campaign_variable":
        return CampaignVariableVariable(default_val, **kwargs)
    elif var_type in ("faction", "scene", "npc"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type in statefinders.LIST_TYPES:
        return FiniteStateListVariable(default_val, var_type, **kwargs)
    elif var_type.startswith("physical:"):
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
    else:
        if var_type != "string":
            print("Unknown variable type {}; defaulting to string.".format(var_type))
        return StringVariable(default_val, var_type, **kwargs)
