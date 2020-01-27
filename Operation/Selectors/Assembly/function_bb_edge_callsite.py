from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction


class function_bb_edge_callsite(Selector):
    """
    This simple Selector retrieves the following information from each Assembly Function object:
        1. BasicBlock count within the function.
        2. Edge ("lines" between basic blocks) count within the function.
        3. Amount of function calls within the function.
    This information is treated as a vector is a 3D euclidean space - The Selector will try to find the closest
    functions, assuming the distance between them is unique in the examined set. (This is done from
    """

    needed_attributes: List[str] = ['FunctionBasicBlockCount', 'FunctionEdgeCount', 'FunctionCallsiteCount']
    selector_name: str = 'function_bb_edge_callsite'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Poor
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly
    selector_comparison_result_type = bd_enums.SelectorComparisonResultType.IntDistance

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> int:

        # Populate the attribute values
        source_bb_count = self.loaded_attributes['FunctionBasicBlockCount'].extract_attribute(source_func)
        source_edge_count = self.loaded_attributes['FunctionEdgeCount'].extract_attribute(source_func)
        source_callsite_count = self.loaded_attributes['FunctionCallsiteCount'].extract_attribute(source_func)

        target_bb_count = self.loaded_attributes['FunctionBasicBlockCount'].extract_attribute(target_func)
        target_edge_count = self.loaded_attributes['FunctionEdgeCount'].extract_attribute(target_func)
        target_callsite_count = self.loaded_attributes['FunctionCallsiteCount'].extract_attribute(target_func)

        if source_bb_count == target_bb_count and source_edge_count == target_edge_count \
                and source_callsite_count == target_callsite_count:
            return True

        return False
