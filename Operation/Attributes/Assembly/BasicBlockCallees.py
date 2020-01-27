from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
from typing import List
import xxhash
from binaryninja import *


class BasicBlockCallees(Attribute):
    """
    Get the hash of the names of the callees in the basic block.
    Un-documented function are not considered for this Attribute.
    """

    def __init__(self):
        super().__init__(name='BasicBlockCallees', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> List:
        # Check if value already exists
        BasicBlockCallees_value = base_object.get_attribute_value('BasicBlockCallees')

        if BasicBlockCallees_value:
            pass
        else:
            names_hash = xxhash.xxh64()
            bb_start = base_object.underlying_obj.start
            bb_end = base_object.underlying_obj.end

            for call_site in base_object.underlying_obj.function.call_sites:
                if call_site.address in range(bb_start, bb_end):
                    bv: BinaryView = base_object.underlying_obj.view
                    for callee in bv.get_callees(call_site.address):
                        callee_name: str = bv.get_function_at(callee).name
                        if callee_name and not callee_name.startswith('sub_'):
                            names_hash.update(callee_name)

            if names_hash.intdigest() != 0:
                base_object.add_attribute_value('BasicBlockCallees', {'callee_names_hash': names_hash.intdigest()})

            BasicBlockCallees_value = base_object.get_attribute_value('BasicBlockCallees')

        return BasicBlockCallees_value['callee_names_hash'] if BasicBlockCallees_value else None
