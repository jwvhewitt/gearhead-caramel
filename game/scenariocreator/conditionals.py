# conditional format: [expression], boolop, [expression]...
from . import statefinders


CONDITIONAL_BOOL_OPS = ("and", "or", "and not", "or not")
CONDITIONAL_EXPRESSION_OPS = ("<", "<=", "==", "!=", ">=", ">")
CONDITIONAL_VALUE_TYPES = ("integer", "campaign variable")


class CVFParam:
    def __init__(self, pname, ptype="integer"):
        self.pname = pname
        self.ptype = ptype

    def validate_value(self, part, value):
        if self.ptype == "integer":
            return isinstance(value, int)
        else:
            return statefinders.is_legal_state(part, self.ptype, value)


class ConditionalValueFunction:
    def __init__(self, fun_pattern, fun_params=()):
        self.fun_pattern = fun_pattern
        self.fun_params = tuple(fun_params)

    def build(self, *args):
        return self.fun_pattern.format(*args)


CONDITIONAL_VALUE_FUNCTIONS = {
    "credits": ConditionalValueFunction("camp.credits")
}


class ConditionalFunctionDefinition(object):
    def __init__(self, script="True", param_types=()):
        self.script = script
        self.param_types = param_types

    def build(self, vallist):
        return self.script.format(vallist)


CONDITIONAL_FUNCTIONS = {
    "can_add_lancemate": ConditionalFunctionDefinition("camp.can_add_lancemate()")
}


def get_conditional_value(vallist):
    # Parse a value list, returning the Python code for the value.
    val_type = vallist[0]
    if val_type == "integer":
        return str(vallist[1])
    elif val_type == "campaign variable":
        return "camp.campdata.get({}, 0)".format(repr(vallist[1]))
    elif val_type in CONDITIONAL_VALUE_FUNCTIONS:
        return CONDITIONAL_VALUE_FUNCTIONS[val_type].build(*vallist)


def build_conditional(rawlist):
    # Given a conditional list, build the Python code it represents.
    formatted_list = list()
    for t in rawlist:
        if isinstance(t, list):
            # This must be an expression.
            expop = t[0]
            if expop in CONDITIONAL_EXPRESSION_OPS:
                a,b = get_conditional_value(t[1]), get_conditional_value(t[2])
                formatted_list.append("{} {} {}".format(a, expop, b))
            elif expop in CONDITIONAL_FUNCTIONS:
                formatted_list.append(CONDITIONAL_FUNCTIONS[expop].build(t))

        elif t in CONDITIONAL_BOOL_OPS:
            # This must be a boolean operation.
            formatted_list.append(t)

    if not formatted_list:
        return "True"
    else:
        return " ".join(formatted_list)


def generate_new_conditional_expression(exp):
    # exp is the expression operator.
    if exp in CONDITIONAL_EXPRESSION_OPS:
        return [exp, ["integer",1], ["integer",1]]
    elif exp in CONDITIONAL_FUNCTIONS:
        myvars = [None for v in CONDITIONAL_FUNCTIONS[exp].param_types]
        return [exp,] + myvars


