from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from typing import Dict, Optional

class FunctionEdgeCount(Attribute):
    """
    Retrieve the number of basic blocks within an Assembly Function.
    """

    def __init__(self):
        super().__init__(name='FunctionEdgeCount', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:
        # Check if value already exists
        FunctionEdgeCount_value = base_object.get_attribute_value('FunctionEdgeCount')

        if FunctionEdgeCount_value:
            pass
        else:
            i = 0
            for bb in base_object.underlying_obj.basic_blocks:
                i += len(bb.outgoing_edges)
            edge_count = i

            FunctionEdgeCount_value = {
                'edge_count': edge_count
            }

            base_object.add_attribute_value('FunctionEdgeCount', FunctionEdgeCount_value)

        return FunctionEdgeCount_value if FunctionEdgeCount_value else None
