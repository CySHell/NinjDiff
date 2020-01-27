from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
import hashlib
import pyprimesieve
from binaryninja import *
from typing import Dict
import math


class FunctionStructuralIndex(Attribute):
    """
    This Attribute is inspired by the MD-INDEX attribute of bindiff.

    For each edge in the function CFG create a 6 tuple of integers
        1. is it a back edge? (1 if true, 1.1 if false)
        2. in-degree of the source basic block
        3. out-degree of the source basic block
        4. in-degree of the destination basic block
        5. out-degree of the destination basic block
        6. amount of dominator basic blocks of the source bb
        7. amount of post dominator basic blocks of the source bb
        8. amount of dominator basic blocks of the destination bb
        9. amount of post dominator basic blocks of the destination bb
    """

    def __init__(self):
        super().__init__(name='FunctionSPP', value_type=bd_enums.AttrValueType.FLOAT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> float:
        # Check if value already exists
        FunctionStructuralIndex_value = base_object.get_attribute_value('FunctionStructuralIndex')

        if FunctionStructuralIndex_value:
            pass
        else:
            function_index = 0
            # edge_cache is a set of strings in the form src_bb.index -> dst_bb.index .
            # The cache denotes the edges that were already traversed.
            edge_cache = set()
            for bb in base_object.underlying_obj.basic_blocks:
                for edge in bb.outgoing_edges:
                    cache = str(edge.source.index) + '-' + str(edge.target.index)
                    if cache in edge_cache:
                        continue
                    else:
                        edge_cache.add(cache)
                        function_index += 1 / math.sqrt(self.generate_single_bb_index(edge))

            base_object.add_attribute_value('FunctionStructuralIndex_value', {'function_index': function_index})
            FunctionStructuralIndex_value = base_object.get_attribute_value('FunctionStructuralIndex_value')

        return FunctionStructuralIndex_value['function_index'] if FunctionStructuralIndex_value else None

    def generate_single_bb_index(self, edge: BasicBlockEdge):
        src_bb: BasicBlock = edge.source
        dst_bb: BasicBlock = edge.target

        back_edge = 1 if edge.back_edge else 1.5
        in_degree_src = len(src_bb.incoming_edges) * math.sqrt(2)
        out_degree_src = len(src_bb.outgoing_edges) * math.sqrt(3)
        in_degree_dst = len(dst_bb.incoming_edges) * math.sqrt(5)
        out_degree_dst = len(dst_bb.outgoing_edges) * math.sqrt(7)
        src_dominator_count = len(src_bb.dominators) * math.sqrt(11)
        dst_dominator_count = len(dst_bb.dominators) * math.sqrt(13)
        src_post_dominator_count = len(src_bb.post_dominators) * math.sqrt(17)
        dst_post_dominator_count = len(dst_bb.post_dominators) * math.sqrt(19)

        return back_edge + in_degree_src + out_degree_src + in_degree_dst + out_degree_dst + src_dominator_count + \
               dst_dominator_count + src_post_dominator_count + dst_post_dominator_count
