from typing import List, Tuple, Dict, Optional, Set, AnyStr, SupportsInt
from binaryninja import *
from ....Abstracts.Property import Property
from ....Abstracts.Attribute import Attribute
from ....Abstracts.BDObject import BDObject
from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunctionSet
import hashlib


class function_in_out_degree(Property):
    """
    Matches functions with either of the following criteria:
        1. same indegree
        or
        2. same outdegree
    """

    needed_attributes: List[str] = ['FunctionDegree']
    property_name: str = 'function_in_out_degree'
    property_quality: bd_enums.PropertyQuality = bd_enums.PropertyQuality.Medium
    property_algorithm_performance: bd_enums.PropertyAlgoPerf = bd_enums.PropertyAlgoPerf.VeryGood
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_set: BDFunctionSet, target_set: BDFunctionSet) \
            -> List[Tuple[BDFunctionSet, BDFunctionSet]]:

        matched_functions: List[Tuple[BDFunctionSet, BDFunctionSet]] = list()

        # Feature vectors are dicts of the examined object and its indegree and outdegree values.
        # The key in the dict is a hash of the above values.
        source_feature_vector: Dict[SupportsInt, Tuple[SupportsInt, SupportsInt,
                                                       Set[Optional[BDObject]]]] = dict()
        target_feature_vector: Dict[SupportsInt, Tuple[SupportsInt, SupportsInt,
                                                       Set[Optional[BDObject]]]] = dict()

        # Populate the feature vectors with all the function information
        for source_bd_object in source_set:
            source_degree: Dict = self.loaded_attributes['FunctionDegree'].extract_attribute(source_bd_object)
            source_indegree: SupportsInt = source_degree['in_degree']
            source_outdegree: SupportsInt = source_degree['out_degree']

            cache_uuid_generator = hashlib.blake2b(digest_size=4)
            cache_uuid_generator.update(
                (str(source_indegree) + str(source_outdegree)).encode('utf-8')
            )

            cache_uuid: SupportsInt = int(cache_uuid_generator.hexdigest(), 16)
            if source_feature_vector.get(cache_uuid):
                source_feature_vector[cache_uuid][2].add(source_bd_object)
            else:
                source_feature_vector.update(
                    {cache_uuid: (
                        source_indegree,
                        source_outdegree,
                        {source_bd_object, }
                    )
                    }
                )

        for target_bd_object in target_set:
            target_degree = self.loaded_attributes['FunctionDegree'].extract_attribute(target_bd_object)
            target_indegree = target_degree['in_degree']
            target_outdegree = target_degree['out_degree']

            cache_uuid_generator = hashlib.blake2b(digest_size=4)
            cache_uuid_generator.update(
                (str(target_indegree) + str(target_outdegree)).encode('utf-8')
            )

            cache_uuid: SupportsInt = int(cache_uuid_generator.hexdigest(), 16)
            if target_feature_vector.get(cache_uuid):
                target_feature_vector[cache_uuid][2].add(target_bd_object)
            else:
                target_feature_vector.update(
                    {cache_uuid: (
                        target_indegree,
                        target_outdegree,
                        {target_bd_object}
                    )
                    }
                )

        for source_cache_uuid, (source_indegree, source_outdegree, source_bd_object_set) \
                in source_feature_vector.items():
            result_tuple = target_feature_vector.get(source_cache_uuid)
            if result_tuple:
                # The functions have the same attributes, they match this property.
                source_bd_function_set = BDFunctionSet()
                for bd_obj in source_bd_object_set:
                    source_bd_function_set.add(bd_obj)

                target_bd_function_set = BDFunctionSet()
                for bd_obj in target_feature_vector[source_cache_uuid][2]:
                    target_bd_function_set.add(bd_obj)

                matched_functions.append((source_bd_function_set, target_bd_function_set))

        log.log_debug(f'function_in_out_degree Property matched function: \n{matched_functions}')
        return matched_functions
