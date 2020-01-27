from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute


class FunctionDegree(Attribute):
    """
    Retrieve the in and out degree (number of callers and number of calees) of the function.
    """

    def __init__(self):
        super().__init__(name='FunctionDegree', value_type=bd_enums.AttrValueType.DICT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> dict:
        # Check if value already exists
        FunctionDegree_value = base_object.get_attribute_value('FunctionDegree')

        if FunctionDegree_value:
            pass
        else:
            base_object.add_attribute_value('FunctionDegree', {'in_degree': len(base_object.underlying_obj.callers),
                                                               'out_degree': len(base_object.underlying_obj.callees)})
            FunctionDegree_value = base_object.get_attribute_value('FunctionDegree')

        return FunctionDegree_value if FunctionDegree_value else None
