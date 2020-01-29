from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from binaryninja import *
from typing import Dict, Tuple


class FunctionCallSiteTargets(Attribute):
    """
    Get all callsite addresses within the function, and extract their target function including its symbol (e.g regular
    function, imported function etc).
    """

    def __init__(self):
        super().__init__(name='FunctionCallSiteTargets', value_type=bd_enums.AttrScope.Contextual,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

        # function_callsites = {callsite_address: target_function_address, target_function_name, target_function_symbol}
        self.function_callsites: Dict[str, Tuple[int, int, str, int]] = dict()

    def extract_attribute(self, base_object: BDFunction) -> Dict[str, Tuple[int, int, str, int]]:
        # Check if value already exists
        FunctionCallSiteTargets_value = base_object.get_attribute_value('FunctionCallSiteTargets')

        bv: BinaryView = base_object.underlying_obj.view

        if FunctionCallSiteTargets_value:
            pass
        else:
            for callsite_ref in base_object.underlying_obj.call_sites:
                target_function_address: int = bv.get_code_refs_from(callsite_ref.address)[0]
                target_function_symbol: types.Symbol = bv.get_symbol_at(target_function_address)
                if target_function_symbol:
                    # If there is a known symbol here it might mean this is an IAT trampoline
                    target_function_name: str = target_function_symbol.name
                    target_function_symbol_type: int = target_function_symbol.type.value
                else:
                    # No symbol, this means its just a non library function.
                    target_function: Function = bv.get_function_at(target_function_address)
                    target_function_name = target_function.name
                    target_function_symbol_type: int = target_function.symbol.value

                self.function_callsites.update({callsite_ref.address: (target_function_address, target_function_name,
                                                                       target_function_symbol_type)})

            base_object.add_attribute_value('FunctionCallSiteTargets', {'function_callsites': self.function_callsites})
            FunctionCallSiteTargets_value = base_object.get_attribute_value('FunctionCallSiteTargets')

        return FunctionCallSiteTargets_value['function_callsites'] if FunctionCallSiteTargets_value else None
