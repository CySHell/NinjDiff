from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
import xxhash


class FunctionNameHash(Attribute):
    """
    Retrieve the name of the function.
    """

    def __init__(self):
        super().__init__(name='FunctionNameHash', value_type=bd_enums.AttrValueType.STR,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> dict:
        # Check if value already exists
        FunctionNameHash_value = base_object.get_attribute_value('FunctionNameHash')

        if FunctionNameHash_value:
            pass
        else:
            name: str = base_object.underlying_obj.name

            if name.startswith('sub_'):
                pass
            else:
                name_hash = xxhash.xxh32()
                name_hash.update(name)
                base_object.add_attribute_value('FunctionNameHash', {'name_hash': name_hash.hexdigest()})
                FunctionNameHash_value = base_object.get_attribute_value('FunctionNameHash')

        return FunctionNameHash_value['name_hash'] if FunctionNameHash_value else None
