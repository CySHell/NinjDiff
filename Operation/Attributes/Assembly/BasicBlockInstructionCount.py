from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
from typing import List


class BasicBlockInstructionCount(Attribute):
    """
    Get the number of instruction in the basic block.
    """

    def __init__(self):
        super().__init__(name='BasicBlockInstructionCount', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> List:
        # Check if value already exists
        BasicBlockInstructionCount_value = base_object.get_attribute_value('BasicBlockInstructionCount')

        if BasicBlockInstructionCount_value:
            pass
        else:
            base_object.add_attribute_value('BasicBlockInstructionCount', {'bb_instr_count':
                                                                           base_object.underlying_obj.instruction_count}
                                            )
            BasicBlockInstructionCount_value = base_object.get_attribute_value('BasicBlockInstructionCount')

        return BasicBlockInstructionCount_value['bb_instr_count'] if BasicBlockInstructionCount_value else None
