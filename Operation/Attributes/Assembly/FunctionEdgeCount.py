from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute


class FunctionEdgeCount(Attribute):
    """
    Retrieve the number of basic blocks within an Assembly Function.
    """

    def __init__(self):
        super().__init__(name='FunctionEdgeCount', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> int:
        # Check if value already exists
        FunctionEdgeCount_value = base_object.get_attribute_value('FunctionEdgeCount')

        if FunctionEdgeCount_value:
            pass
        else:
            i = 0
            for bb in base_object.underlying_obj.basic_blocks:
                i += len(bb.outgoing_edges)
            edge_count = i
            base_object.add_attribute_value('FunctionEdgeCount', {'edge_count': edge_count})
            FunctionEdgeCount_value = base_object.get_attribute_value('FunctionEdgeCount')

        return FunctionEdgeCount_value['edge_count']
