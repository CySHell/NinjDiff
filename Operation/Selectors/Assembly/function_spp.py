from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction


class function_spp(Selector):
    """
    Compare the Small Primes Product of 2 functions.
    """

    needed_attributes: List[str] = ['FunctionSPP']
    selector_name: str = 'function_spp'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Medium
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.Medium
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly
    selector_comparison_result_type = bd_enums.SelectorComparisonResultType.Boolean

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> bool:

        # Populate the attribute values
        source_spp = self.loaded_attributes['FunctionSPP'].extract_attribute(source_func)

        target_spp = self.loaded_attributes['FunctionSPP'].extract_attribute(target_func)

        if source_spp == target_spp:
            return True

        return False
