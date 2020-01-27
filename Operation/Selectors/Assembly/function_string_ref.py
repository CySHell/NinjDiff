from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction


class function_string_ref(Selector):
    """
    Compare the strings referenced by the functions.
    """

    needed_attributes: List[str] = ['FunctionStringReferences']
    selector_name: str = 'function_string_ref'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.VeryGood
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly
    selector_comparison_result_type = bd_enums.SelectorComparisonResultType.Boolean

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> bool:

        # Populate the attribute values
        source_strings_hash = self.loaded_attributes['FunctionStringReferences'].extract_attribute(source_func)

        target_strings_hash = self.loaded_attributes['FunctionStringReferences'].extract_attribute(target_func)

        if source_strings_hash == target_strings_hash:
            return True

        return False
