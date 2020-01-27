from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
import xxhash


class FunctionHash(Attribute):
    """
    Retrieve the hash of the instructions within the function.
    """

    def __init__(self):
        super().__init__(name='FunctionHash', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> int:
        # Check if value already exists
        FunctionHash_value = base_object.get_attribute_value('FunctionHash')

        if FunctionHash_value:
            pass
        else:
            hash_value = xxhash.xxh32()
            for instruction_expression in base_object.underlying_obj.instructions:
                for instruction in instruction_expression[0]:
                    hash_value.update(instruction.text)

            base_object.add_attribute_value('FunctionHash', {'hash': hash_value.intdigest()})
            FunctionHash_value = base_object.get_attribute_value('FunctionHash')

        return FunctionHash_value['hash'] if FunctionHash_value else None
