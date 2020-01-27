from typing import List, Tuple, Dict, Optional, Set
from binaryninja import *
from ....Abstracts.Property import Property
from ....Abstracts.Attribute import Attribute
from ....Abstracts.BDObject import BDObject
from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlockSet, BDBasicBlock
from .... import Configuration


class basic_block_instruction_count(Property):
    """
    Matches basic blocks based on their instruction count, with a deviation of a certain percentage (configurable via
    the Configuration file).
    """

    needed_attributes: List[str] = ['BasicBlockInstructionCount']
    property_name: str = 'basic_block_instruction_count'
    property_quality: bd_enums.PropertyQuality = bd_enums.PropertyQuality.Poor
    property_algorithm_performance: bd_enums.PropertyAlgoPerf = bd_enums.PropertyAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.BasicBlock
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_set: BDBasicBlockSet, target_set: BDBasicBlockSet) \
            -> List[Tuple[BDBasicBlockSet, BDBasicBlockSet]]:

        matched_basic_blocks: List[Tuple[BDBasicBlockSet, BDBasicBlockSet]] = list()

        # Feature vectors are dicts of the examined object and a str representing the instruction count
        source_feature_vector: Dict[str, Set[Optional[BDBasicBlock]]] = dict()
        target_feature_vector: Dict[str, Set[Optional[BDBasicBlock]]] = dict()

        # Populate the feature vectors with all the basic block information
        for source_bd_obj in source_set:
            source_instr_count = self.loaded_attributes['BasicBlockInstructionCount'].extract_attribute(source_bd_obj)

            if source_instr_count:
                if source_feature_vector.get(source_instr_count):
                    source_feature_vector[source_instr_count].add(source_bd_obj)
                else:
                    source_feature_vector.update({source_instr_count: {source_bd_obj}})

        for target_bd_obj in target_set:
            target_instr_count = self.loaded_attributes['BasicBlockInstructionCount'].extract_attribute(target_bd_obj)

            if target_instr_count:
                if target_feature_vector.get(target_instr_count):
                    target_feature_vector[target_instr_count].add(target_bd_obj)
                else:
                    target_feature_vector.update({target_instr_count: {target_bd_obj}})

        for source_instr_count, source_bd_object_set in source_feature_vector.items():

            target_bd_object_set = target_feature_vector.get(source_instr_count)
            if target_bd_object_set:
                source_bd_bb_set = BDBasicBlockSet()
                source_bd_bb_set.union(source_bd_object_set)

                target_bd_bb_set = BDBasicBlockSet()
                target_bd_bb_set.union(target_bd_object_set)

                matched_basic_blocks.append((source_bd_bb_set, target_bd_bb_set))

        log.log_debug(f'basic_block_instruction_count Property matched basic blocks: \n{matched_basic_blocks}')
        return matched_basic_blocks
