from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from typing import Dict, Optional


class FunctionRecursion(Attribute):
    """
    Check if the function is recursive (calls itself) or not.
    """

    def __init__(self):
        super().__init__(name='FunctionRecursion', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:
        # Check if value already exists
        FunctionRecursion_value = base_object.get_attribute_value('FunctionRecursion')

        recursive = False
        if FunctionRecursion_value:
            pass
        else:
            for callee in base_object.underlying_obj.callees:
                if callee.start == base_object.underlying_obj.start:
                    recursive = True

            FunctionRecursion_value = {
                'recursive': recursive
            }

            base_object.add_attribute_value('FunctionRecursion', FunctionRecursion_value)

        return FunctionRecursion_value if FunctionRecursion_value else None
