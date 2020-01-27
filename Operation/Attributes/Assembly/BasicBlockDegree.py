from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
from typing import Dict


class BasicBlockDegree(Attribute):
    """
    Retrieve the in and out degree (number of incoming and outgoing edges) of the basic block.
    """

    def __init__(self):
        super().__init__(name='BasicBlockDegree', value_type=bd_enums.AttrValueType.DICT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> Dict:
        # Check if value already exists
        BasicBlockDegree_value = base_object.get_attribute_value('BasicBlockDegree')

        if BasicBlockDegree_value:
            pass
        else:
            base_object.add_attribute_value('BasicBlockDegree',
                                            {'in_degree': len(base_object.underlying_obj.incoming_edges),
                                             'out_degree': len(base_object.underlying_obj.outgoing_edges)
                                             }
                                            )
            BasicBlockDegree_value = base_object.get_attribute_value('BasicBlockDegree')

        return BasicBlockDegree_value if BasicBlockDegree_value else None