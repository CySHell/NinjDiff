from typing import List, Tuple, Dict, Optional, Set
from binaryninja import *
from ....Abstracts.Property import Property
from ....Abstracts.Attribute import Attribute
from ....Abstracts.BDObject import BDObject
from ....Enums import bd_enums
from ....Operands.Assembly.BDBasicBlock import BDBasicBlockSet, BDBasicBlock
from .... import Configuration


class basic_block_same_callees(Property):
    """
    Matches basic blocks based on the function calls within the block.
    Does not count un-documented functions (names starting with 'sub_').
    """

    needed_attributes: List[str] = ['BasicBlockCallees']
    property_name: str = 'basic_block_same_callees'
    property_quality: bd_enums.PropertyQuality = bd_enums.PropertyQuality.Medium
    property_algorithm_performance: bd_enums.PropertyAlgoPerf = bd_enums.PropertyAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.BasicBlock
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_set: BDBasicBlockSet, target_set: BDBasicBlockSet) \
            -> List[Tuple[BDBasicBlockSet, BDBasicBlockSet]]:

        matched_basic_blocks: List[Tuple[BDBasicBlockSet, BDBasicBlockSet]] = list()

        # Feature vectors are dicts of the examined object and a str representing the callee names hash
        source_feature_vector: Dict[int, Set[Optional[BDBasicBlock]]] = dict()
        target_feature_vector: Dict[int, Set[Optional[BDBasicBlock]]] = dict()

        # Populate the feature vectors with all the basic block information
        for source_bd_obj in source_set:
            source_callee_names_hash = self.loaded_attributes['BasicBlockCallees'].extract_attribute(source_bd_obj)

            if source_callee_names_hash:
                if source_feature_vector.get(source_callee_names_hash):
                    source_feature_vector[source_callee_names_hash].add(source_bd_obj)
                else:
                    source_feature_vector.update({source_callee_names_hash: {source_bd_obj}})

        for target_bd_obj in target_set:
            target_callee_names_hash = self.loaded_attributes['BasicBlockCallees'].extract_attribute(target_bd_obj)

            if target_callee_names_hash:
                if target_feature_vector.get(target_callee_names_hash):
                    target_feature_vector[target_callee_names_hash].add(target_bd_obj)
                else:
                    target_feature_vector.update({target_callee_names_hash: {target_bd_obj}})

        for source_callee_names_hash, source_bd_object_set in source_feature_vector.items():

            target_bd_object_set = target_feature_vector.get(source_callee_names_hash)
            if target_bd_object_set:
                source_bd_bb_set = BDBasicBlockSet()
                source_bd_bb_set.union(source_bd_object_set)

                target_bd_bb_set = BDBasicBlockSet()
                target_bd_bb_set.union(target_bd_object_set)

                matched_basic_blocks.append((source_bd_bb_set, target_bd_bb_set))

        log.log_debug(f'basic_block_same_callees Property matched basic blocks: \n{matched_basic_blocks}')
        return matched_basic_blocks
