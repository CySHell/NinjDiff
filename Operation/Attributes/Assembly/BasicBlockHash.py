from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
import xxhash
from typing import Optional, Dict


class BasicBlockHash(Attribute):
    """
    Retrieve the hash of the instructions within the basic block.
    """

    def __init__(self):
        super().__init__(name='BasicBlockHash', value_type=bd_enums.AttrScope.Contextual,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> Optional[Dict]:
        # Check if value already exists
        BasicBlockHash_value = base_object.get_attribute_value('BasicBlockHash')

        if BasicBlockHash_value:
            pass
        else:
            hash_value = xxhash.xxh32()
            for instruction_expression in base_object.underlying_obj:
                for instruction in instruction_expression[0]:
                    hash_value.update(instruction.text)

            BasicBlockHash_value = {
                'hash': hash_value.intdigest()
            }

            base_object.add_attribute_value('BasicBlockHash', BasicBlockHash_value)

        return BasicBlockHash_value if BasicBlockHash_value else None
