from typing import List, Tuple, Dict, Optional, Set
from binaryninja import *
from ....Abstracts.Property import Property
from ....Abstracts.Attribute import Attribute
from ....Abstracts.BDObject import BDObject
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunctionSet


class function_name_hash(Property):
    """
    Matches functions based on a hash of their names. Only real names are considered, names which have been
    auto-generated by the disassembler are not used. This is one of the few algorithms that can match imported
    functions, i.e. functions that do not have an actual body in the binary. False matches are highly unlikely.
    """

    needed_attributes: List[str] = ['FunctionNameHash']
    property_name: str = 'function_name_hash'
    property_quality: bd_enums.PropertyQuality = bd_enums.PropertyQuality.Good
    property_algorithm_performance: bd_enums.PropertyAlgoPerf = bd_enums.PropertyAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_set: BDFunctionSet, dest_set: BDFunctionSet) \
            -> List[Tuple[BDFunctionSet, BDFunctionSet]]:

        matched_functions: List[Tuple[BDFunctionSet, BDFunctionSet]] = list()

        # Feature vectors are dicts of the examined object and a str representing the name hash
        source_feature_vector: Dict[str, Set[Optional[BDObject]]] = dict()
        dest_feature_vector: Dict[str, Set[Optional[BDObject]]] = dict()

        # Populate the feature vectors with all the function information
        for source_bd_object in source_set:
            source_name_hash = self.loaded_attributes['FunctionNameHash'].extract_attribute(source_bd_object)

            if source_name_hash:
                if source_feature_vector.get(source_name_hash):
                    source_feature_vector[source_name_hash].add(source_bd_object)
                else:
                    source_feature_vector.update({source_name_hash: {source_bd_object}})

        for dest_bd_object in dest_set:
            dest_name_hash = self.loaded_attributes['FunctionNameHash'].extract_attribute(dest_bd_object)

            if dest_name_hash:
                if dest_feature_vector.get(dest_name_hash):
                    dest_feature_vector[dest_name_hash].add(dest_bd_object)
                else:
                    dest_feature_vector.update({dest_name_hash: {dest_bd_object}})

        for source_name, source_bd_object_set in source_feature_vector.items():

            dest_bd_object_set = dest_feature_vector.get(source_name)
            if dest_bd_object_set:
                source_bd_function_set = BDFunctionSet()
                for bd_obj in source_bd_object_set:
                    source_bd_function_set.add(bd_obj)

                dest_bd_function_set = BDFunctionSet()
                dest_bd_function_set.union(dest_bd_object_set)

                matched_functions.append((source_bd_function_set, dest_bd_function_set))

        log.log_debug(f'name_hash Property matched function: \n{matched_functions}')
        return matched_functions