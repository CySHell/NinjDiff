from typing import List, Tuple, Dict, Optional, Set
from ....Abstracts.Property import Property
from ....Abstracts.Attribute import Attribute
from ....Abstracts.BDObject import BDObject
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunctionSet
from binaryninja import *


class function_is_recursive(Property):
    """
    Matches recursive functions.
    """

    needed_attributes: List[str] = ['FunctionRecursion']
    property_name: str = 'function_is_recursive'
    property_quality: bd_enums.PropertyQuality = bd_enums.PropertyQuality.Poor
    property_algorithm_performance: bd_enums.PropertyAlgoPerf = bd_enums.PropertyAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_set: BDFunctionSet, dest_set: BDFunctionSet) \
            -> List[Tuple[BDFunctionSet, BDFunctionSet]]:

        matched_functions: List[Tuple[BDFunctionSet, BDFunctionSet]] = list()

        # Feature vectors are dicts of the examined object and a bool representing the recursion of the function
        source_feature_vector: Dict[bool, Set[Optional[BDObject]]] = dict()
        target_feature_vector: Dict[bool, Set[Optional[BDObject]]] = dict()

        # Populate the feature vectors with all the function information
        for source_bd_object in source_set:
            source_is_recursive = self.loaded_attributes['FunctionRecursion'].extract_attribute(source_bd_object)

            if source_is_recursive is not None:
                if source_feature_vector.get(source_is_recursive):
                    source_feature_vector[source_is_recursive].add(source_bd_object)
                else:
                    source_feature_vector.update({source_is_recursive: {source_bd_object}})

        for dest_bd_object in dest_set:
            target_is_recursive = self.loaded_attributes['FunctionRecursion'].extract_attribute(dest_bd_object)

            if target_is_recursive is not None:
                if target_feature_vector.get(target_is_recursive):
                    target_feature_vector[target_is_recursive].add(dest_bd_object)
                else:
                    target_feature_vector.update({target_is_recursive: {dest_bd_object}})

        for source_is_recursive, source_bd_object_set in source_feature_vector.items():

            target_bd_object_set = target_feature_vector.get(source_is_recursive)
            if target_bd_object_set:
                source_bd_function_set = BDFunctionSet()
                for bd_obj in source_bd_object_set:
                    source_bd_function_set.add(bd_obj)

                target_bd_function_set = BDFunctionSet()
                target_bd_function_set.union(target_bd_object_set)

                matched_functions.append((source_bd_function_set, target_bd_function_set))

        return matched_functions
