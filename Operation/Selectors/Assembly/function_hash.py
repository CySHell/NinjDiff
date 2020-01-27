from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction


class function_hash(Selector):
    """
    Compare the hash of all assembly instructions of 2 functions.
    """

    needed_attributes: List[str] = ['FunctionHash']
    selector_name: str = 'function_hash'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Perfect
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly
    selector_comparison_result_type = bd_enums.SelectorComparisonResultType.Boolean

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> bool:

        # Populate the attribute values
        source_hash = self.loaded_attributes['FunctionHash'].extract_attribute(source_func)

        target_hash = self.loaded_attributes['FunctionHash'].extract_attribute(target_func)

        if source_hash == target_hash:
            return True

        return False
