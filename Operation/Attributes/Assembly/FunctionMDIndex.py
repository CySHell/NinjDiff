from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from binaryninja import *
from typing import Dict, List, Tuple, SupportsFloat
import math


class FunctionMDIndex(Attribute):
    """
    Generate a topological sort of all basic blocks in the function.

    see http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.661.9484&rep=rep1&type=pdf , Section 5.
    """

    def __init__(self):
        super().__init__(name='FunctionMDIndex', value_type=bd_enums.AttrValueType.DICT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> Dict:
        # Check if value already exists
        FunctionMDIndex_value = base_object.get_attribute_value('FunctionMDIndex')

        if FunctionMDIndex_value:
            pass
        else:
            # Mapping between basic block index and its position in the order
            topological_order = base_object.get_attribute_value('FunctionTopologicalSort')['topological_sort']

            md_index: SupportsFloat = 0
            relaxed_md_index: SupportsFloat = 0
            for bb in base_object.underlying_obj.basic_blocks:
                for edge in bb.outgoing_edges:
                    source_bb: BasicBlock = edge.source
                    destination_bb: BasicBlock = edge.target

                    source_topological_position = topological_order[source_bb.index]
                    tup: Tuple = (source_topological_position,
                                  len(source_bb.incoming_edges),
                                  len(source_bb.outgoing_edges),
                                  len(destination_bb.incoming_edges),
                                  len(destination_bb.outgoing_edges)
                                  )

                    # sqrt(2) = 1.4142135623730951 , sqrt(3) = 1.7320508075688772 , sqrt(5) = 2.23606797749979
                    # sqrt(7) = 2.6457513110645907
                    relaxed_emb: float = tup[1] * 1.4142135623730951 + \
                                         tup[2] * 1.7320508075688772 + \
                                         tup[3] * 2.23606797749979 + \
                                         tup[4] * 2.6457513110645907

                    emb: float = relaxed_emb + tup[0]

                    relaxed_md_index += 1 / math.sqrt(relaxed_emb)
                    md_index += 1 / math.sqrt(emb)

            base_object.add_attribute_value('FunctionMDIndex_value', {'md_index': md_index,
                                                                      'relaxed_md_index': relaxed_md_index})
            FunctionMDIndex_value = base_object.get_attribute_value('FunctionMDIndex_value')

        return FunctionMDIndex_value if FunctionMDIndex_value else None
