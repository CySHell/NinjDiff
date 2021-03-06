from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from typing import Dict, Optional


class FunctionCallsiteCount(Attribute):
    """
    Retrieve the number of basic blocks within an Assembly Function.
    """

    def __init__(self):
        super().__init__(name='FunctionCallsiteCount', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:

        # Check if value already exists
        FunctionCallsiteCount_value = base_object.get_attribute_value('FunctionCallsiteCount')

        if FunctionCallsiteCount_value:
            pass
        else:
            FunctionCallsiteCount_value = {
                'callsite_count': len(base_object.underlying_obj.call_sites)
            }

            base_object.add_attribute_value('FunctionCallsiteCount', FunctionCallsiteCount_value)

        return FunctionCallsiteCount_value if FunctionCallsiteCount_value else None
