from typing import List, Dict
from ....Abstracts.Selector import Selector
from ....Abstracts.Attribute import Attribute
from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock


class basic_block_hash(Selector):
    """
    Compare the hash of all assembly instructions of 2 basic blocks.
    """

    needed_attributes: List[str] = ['BasicBlockHash']
    selector_name: str = 'basic_block_hash'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Perfect
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.BasicBlock
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly
    selector_comparison_result_type = bd_enums.SelectorComparisonResultType.Boolean

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_bb: BDBasicBlock, target_bb: BDBasicBlock) \
            -> bool:

        # Populate the attribute values
        source_hash = self.loaded_attributes['BasicBlockHash'].extract_attribute(source_bb)

        target_hash = self.loaded_attributes['BasicBlockHash'].extract_attribute(target_bb)

        if source_hash == target_hash:
            return True

        return False
