from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
from typing import Dict, Optional
import xxhash
from binaryninja import *


class BasicBlockCallees(Attribute):
    """
    Get the hash of the names of the callees in the basic block.
    Un-documented function are not considered for this Attribute.
    """

    def __init__(self):
        super().__init__(name='BasicBlockCallees', value_type=bd_enums.AttrScope.Contextual,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> Optional[Dict]:
        # Check if value already exists
        BasicBlockCallees_value = base_object.get_attribute_value('BasicBlockCallees')

        if BasicBlockCallees_value:
            pass
        else:
            names_hash = xxhash.xxh32()
            bb_start = base_object.underlying_obj.start
            bb_end = base_object.underlying_obj.end

            for call_site in base_object.underlying_obj.function.call_sites:
                if call_site.address in range(bb_start, bb_end):
                    bv: BinaryView = base_object.underlying_obj.view
                    for callee in bv.get_callees(call_site.address):
                        callee_name: str = bv.get_function_at(callee).name
                        if callee_name and not callee_name.startswith('sub_'):
                            names_hash.update(callee_name)

            BasicBlockCallees_value = {
                'callee_names_hash': names_hash.intdigest()
            }
            base_object.add_attribute_value('BasicBlockCallees', BasicBlockCallees_value)

            if names_hash.intdigest() == 0:
                log.log_debug(f'BasicBlockCallees: No names to extract, names_hash is 0')

        return BasicBlockCallees_value if BasicBlockCallees_value else None
