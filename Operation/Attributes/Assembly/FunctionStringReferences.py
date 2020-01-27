from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from typing import Dict
import xxhash
from binaryninja import *


class FunctionStringReferences(Attribute):
    """
    Retrieve all the individual string references in a function, as well as a combined hash of all of them.
    """

    def __init__(self):
        super().__init__(name='FunctionStringReferences', value_type=bd_enums.AttrValueType.DICT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Dict:
        # Check if value already exists
        FunctionStringReferences_value = base_object.get_attribute_value('FunctionStringReferences')

        if FunctionStringReferences_value:
            pass

        else:
            strings_hash = xxhash.xxh64()
            current_function: Function = base_object.underlying_obj

            for addr in range(current_function.lowest_address, current_function.highest_address):
                const_refs = current_function.get_constants_referenced_by(addr)
                for ref in const_refs:
                    string = current_function.view.get_string_at(ref.value)
                    if string:
                        strings_hash.update(string.value.encode('utf8'))

            base_object.add_attribute_value('FunctionStringReferences', {'strings_hash': strings_hash.intdigest()})
            FunctionStringReferences_value = base_object.get_attribute_value('FunctionStringReferences')

        return FunctionStringReferences_value['strings_hash'] if FunctionStringReferences_value else None
