from typing import List, Dict
from Abstracts.Selector import Selector
from Abstracts.Attribute import Attribute
from Enums import bd_enums
from Operands.Assembly.BDFunction import BDFunction


class function_structural_index(Selector):
    """
    Compare the hash of all assembly instructions of 2 functions.
    """

    needed_attributes: List[str] = ['FunctionStructuralIndex']
    selector_name: str = 'function_structural_index'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Good
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.Medium
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> bool:
        # Populate the attribute values
        source_index = self.loaded_attributes['FunctionStructuralIndex'].extract_attribute(source_func)

        target_index = self.loaded_attributes['FunctionStructuralIndex'].extract_attribute(target_func)

        if source_index == target_index:
            return True

        return False
