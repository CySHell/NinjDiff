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
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

        # function_callsites = {callsite_address: target_function_address, target_function_name, target_function_symbol}
        self.function_callsites: Dict = dict()

    def extract_attribute(self, base_object: BDFunction) -> Dict[str, Tuple[int, int, str, int]]:
        # Check if value already exists
        FunctionCallSiteTargets_value = base_object.get_attribute_value('FunctionCallSiteTargets')

        bv: BinaryView = base_object.underlying_obj.view

        if FunctionCallSiteTargets_value:
            pass
        else:
            for callsite_ref in base_object.underlying_obj.call_sites:
                for target_function_address in bv.get_code_refs_from(callsite_ref.address):
                    target_function: Function = bv.get_function_at(target_function_address)
                    if target_function:
                        target_function_symbol: types.Symbol = bv.get_symbol_at(target_function_address)
                        if target_function_symbol:
                            # If there is a known symbol here it might mean this is an IAT trampoline
                            target_function_name: str = target_function_symbol.name
                            target_function_symbol_type: int = target_function_symbol.type.value
                        else:
                            # No symbol, this means its just a non library function.
                            target_function_name = target_function.name
                            target_function_symbol_type: int = 0

                        self.function_callsites.update({f'addr_{str(callsite_ref.address)}':
                            [
                                str(target_function_address),
                                target_function_name,
                                str(target_function_symbol_type)
                            ]
                        })

            FunctionCallSiteTargets_value = self.function_callsites
            FunctionCallSiteTargets_value.update({'uuid': self.create_attribute_uuid(FunctionCallSiteTargets_value)})

            base_object.add_attribute_value('FunctionCallSiteTargets', self.function_callsites)

        return FunctionCallSiteTargets_value if FunctionCallSiteTargets_value else None
