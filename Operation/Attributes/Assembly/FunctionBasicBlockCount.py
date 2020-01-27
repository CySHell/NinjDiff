from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute


class FunctionBasicBlockCount(Attribute):
    """
    Retrieve the number of basic blocks within an Assembly Function.
    """

    def __init__(self):
        super().__init__(name='FunctionBasicBlockCount', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> int:

        # Check if value already exists
        functionBasicBlockCount_value = base_object.get_attribute_value('FunctionBasicBlockCount')

        if functionBasicBlockCount_value:
            pass
        else:
            bb_count = len(base_object.underlying_obj.basic_blocks)
            base_object.add_attribute_value('FunctionBasicBlockCount', {'bb_count': bb_count})
            functionBasicBlockCount_value = base_object.get_attribute_value('FunctionBasicBlockCount')

        return functionBasicBlockCount_value['bb_count']
