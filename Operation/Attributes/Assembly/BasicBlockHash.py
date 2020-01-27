from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
import xxhash


class BasicBlockHash(Attribute):
    """
    Retrieve the hash of the instructions within the basic block.
    """

    def __init__(self):
        super().__init__(name='BasicBlockHash', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> int:
        # Check if value already exists
        BasicBlockHash_value = base_object.get_attribute_value('BasicBlockHash')

        if BasicBlockHash_value:
            pass
        else:
            hash_value = xxhash.xxh64()
            for instruction_expression in base_object.underlying_obj:
                for instruction in instruction_expression[0]:
                    hash_value.update(instruction.text)

            base_object.add_attribute_value('BasicBlockHash', {'hash': hash_value.intdigest()})
            BasicBlockHash_value = base_object.get_attribute_value('BasicBlockHash')

        return BasicBlockHash_value['hash'] if BasicBlockHash_value else None
