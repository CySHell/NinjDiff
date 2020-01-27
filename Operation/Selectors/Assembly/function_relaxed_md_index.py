from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction


class function_relaxed_md_index(Selector):
    """
    Compare the relaxed MD-INDEX of 2 functions.
    Relaxed MD-INDEX is calculated the same as the MD-INDEX, but without taking into account the topological order.
    """

    needed_attributes: List[str] = ['FunctionMDIndex', 'FunctionTopologicalSort']
    selector_name: str = 'function_relaxed_md_index'
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
        self.loaded_attributes['FunctionTopologicalSort'].extract_attribute(source_func)

        source_md_index = self.loaded_attributes['FunctionMDIndex'].extract_attribute(source_func)['relaxed_md_index']

        self.loaded_attributes['FunctionTopologicalSort'].extract_attribute(target_func)

        target_md_index = self.loaded_attributes['FunctionMDIndex'].extract_attribute(target_func)['relaxed_md_index']

        if source_md_index == target_md_index:
            return True

        return False
