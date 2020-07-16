from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
import xxhash
from typing import Dict, Optional

class FunctionNameHash(Attribute):
    """
    Retrieve the name of the function.
    """

    def __init__(self):
        super().__init__(name='FunctionNameHash', value_type=bd_enums.AttrScope.Contextual,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:
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

                FunctionNameHash_value = {
                    'name_hash': name_hash.hexdigest()
                }

                base_object.add_attribute_value('FunctionNameHash', FunctionNameHash_value)

        return FunctionNameHash_value if FunctionNameHash_value else None
