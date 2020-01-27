import abc
from typing import List, Dict, Optional
from ..Enums import bd_enums
from ..Abstracts.Attribute import Attribute
from ..Abstracts.BDObject import BDObject

class Selector(abc.ABC):
    """
    A Selector is essentially just a mapping that, given a node A[i] ∈ An of a graph and a set of nodes in another graph
    returns either one element from the given set or the empty set, e.g.
    s : An × P(Bn) → Bn ∪ ∅
    The selector’s job is to select a single node from a set of given nodes that is most ”similar” to A[i], or, if more
    than one candidates with the same ”similarity” exists, to select nothing at all.
    """

    # The following class attributes define the needed input and general properties of the selection algorithm
    needed_attributes: List[str]
    selector_name: str
    selector_quality: bd_enums.SelectorQuality
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf
    target_bd_object: bd_enums.TargetType
    target_bd_IR: bd_enums.IRType
    loaded_attributes: Dict[str, Attribute] = dict()
    selector_comparison_result_type: bd_enums.SelectorComparisonResultType

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
    def exec_comparison_heuristic(self, source_object: BDObject,
                                  target_object: BDObject):
        """
        Calculate the matching between the src and target BDObjects.
        Each selector has its own logic for calculating this match.
        """
        pass

    def add_attribute(self, attr_name: str, attr_class_obj: Attribute):
        self.loaded_attributes.update({attr_name: attr_class_obj})

    def extract_all_attributes(self):
        pass
