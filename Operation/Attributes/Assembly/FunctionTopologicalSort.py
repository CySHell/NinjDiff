from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from binaryninja import *
from typing import Dict, List, SupportsInt, Tuple
from ....Utility import TarjanSort


class FunctionTopologicalSort(Attribute):
    """
    Generate a topological sort of all basic blocks in the function.
    As a side effect, also returns the natural loop count in the function.
    """

    def __init__(self):
        super().__init__(name='FunctionTopologicalSort', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Dict:
        # Check if value already exists
        FunctionTopologicalSort_value = base_object.get_attribute_value('FunctionTopologicalSort')

        if FunctionTopologicalSort_value:
            pass
        else:
            # graph is a mapping between basic block names (the name is its index) to its children
            graph: Dict[SupportsInt, List[SupportsInt]] = dict()

            # sorted_mapping is a mapping between the index of a basic block and its position in the order.
            sorted_mapping: Dict[SupportsInt, SupportsInt] = dict()

            for bb in base_object.underlying_obj.basic_blocks:
                graph[bb.index] = []
                for edge in bb.outgoing_edges:
                    graph[bb.index].append(edge.target.index)

            # sorted_order is a sorted list of the basic block indexes
            sorted_order: List[Tuple[SupportsInt]] = TarjanSort.robust_topological_sort(graph)

            # Each strongly connected tuple with 2 or more nodes counts as a natural loop
            natural_loop_count = 0

            order_index = 0
            for index in range(len(sorted_order)):

                # Check if this strongly connected component is a loop
                if len(sorted_order[index]) > 1:
                    natural_loop_count += 1
                elif len(sorted_order[index]) == 1:
                    # Check if the node has a self loop
                    bb_index = sorted_order[index][0]
                    for outgoing_edge in base_object.underlying_obj[bb_index].outgoing_edges:
                        if outgoing_edge.back_edge:
                            natural_loop_count += 1

                # Create a sorted list of the bb indexes within a strongly connected component
                sorted_order_set = sorted(sorted_order[index])
                # For each bb index, update the mapping of it to its position in the order
                for bb_index in sorted_order_set:
                    sorted_mapping.update({bb_index: order_index})
                    order_index += 1

            base_object.add_attribute_value('FunctionTopologicalSort',
                                            {'topological_sort': sorted_mapping,
                                             'natural_loop_count': natural_loop_count})
            FunctionTopologicalSort_value = base_object.get_attribute_value('FunctionTopologicalSort')

        return FunctionTopologicalSort_value if FunctionTopologicalSort_value else None
