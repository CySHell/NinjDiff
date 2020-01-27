from ..Enums import bd_enums
import abc
from typing import List, Dict, Tuple
from ..Abstracts.Attribute import Attribute
from ..Abstracts.BDSet import BDSet


class PropertyFeatureVector(dict):
    pass


class Property(abc.ABC):
    """
    A Property π is defined as a mapping that maps two graphs A and B to subsets of their node sets:
    π(A, B) → (A', B') with A' ⊂ A and B'n ⊂ B
    The purpose of such a mapping is reducing the size of the sets used by a selector in order to improve the
    probability for the selector to return a non-empty result.
    """
    # The following class attributes define the needed input and general properties of the selection algorithm
    needed_attributes: List[str]
    property_name: str
    property_quality: bd_enums.SelectorQuality
    property_algorithm_performance: bd_enums.SelectorAlgoPerf
    target_bd_object: bd_enums.TargetType
    target_bd_IR: bd_enums.IRType
    loaded_attributes: Dict[str, Attribute] = dict()

    def __init__(self, globally_loaded_attributes: Dict[str, Attribute]):
        """
        A Selector init should not contain anything related to external arguments.
        """

        # loaded_attributes contains the modules for all attribute plugins loaded from disk.
        # In order to use the module we need to instantiate the class itself.
        for attr_name, attr_module in globally_loaded_attributes.items():
            if not self.loaded_attributes.get(attr_name):
                self.add_attribute(attr_name, attr_module())

    @abc.abstractmethod
    def exec_comparison_heuristic(self, source_set: BDSet, dest_set: BDSet) -> List[Tuple[BDSet, BDSet]]:
        """
        Calculate the matching between the src and dest sets.
        Each property has its own logic for calculating this match.
        :returns A list of tuple, each tuple represents a subset of source set and a subset of dest set that contain
                 nodes that are matched by the given property.
        """
        pass

    def add_attribute(self, attr_name: str, attr_class_obj: Attribute):
        self.loaded_attributes.update({attr_name: attr_class_obj})

    def extract_all_attributes(self):
        pass
