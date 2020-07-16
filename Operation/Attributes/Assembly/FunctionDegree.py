from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from typing import Dict, Optional


class FunctionDegree(Attribute):
    """
    Retrieve the in and out degree (number of callers and number of calees) of the function.
    """

    def __init__(self):
        super().__init__(name='FunctionDegree', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:
        # Check if value already exists
        FunctionDegree_value = base_object.get_attribute_value('FunctionDegree')

        if FunctionDegree_value:
            pass
        else:

            FunctionDegree_value = {
                'in_degree': len(base_object.underlying_obj.callers),
                'out_degree': len(base_object.underlying_obj.callees)
            }
            FunctionDegree_value.update({'uuid': self.create_attribute_uuid(FunctionDegree_value)})

            base_object.add_attribute_value('FunctionDegree', FunctionDegree_value)

        return FunctionDegree_value if FunctionDegree_value else None
