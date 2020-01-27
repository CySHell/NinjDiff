from typing import *
from ..Operands.Assembly.BDBasicBlock import BDBasicBlockSet
from ..Operands.Assembly.BDFunction import BDFunction, BDFunctionSet
from ..Abstracts.BDObject import BDObject
from ..Abstracts.Property import Property
from ..Abstracts.Selector import Selector
from ..Abstracts.Attribute import Attribute
from ..Abstracts.BDSet import BDSet
from ..FlowManagement.FlowManager import FlowManager
from ..FlowManagement.FlowResults import FlowResults
from binaryninja import *
from ..Enums import bd_enums
from .. import Configuration
import xxhash
from .FlowResults import FlowResults


class AssemblyFunctionDiffManager:
    """
    The AssemblyFunctionDiffManager is responsible for handling the entire diffing flow.
    This is done through a curated work flow that instantiates FlowManager instances to handle each point in the flow.
    Currently, the AssemblyFunctionDiffManager receives a pair of BDFunctionSets to compare (in the future there might
    be DiffManagers with other scopes).
    """

    def __init__(self, source: BDSet, target: BDSet):
        self.flow_result = FlowResults(source, target)

    def diff_functions(self):

        func_flow_manager: FlowManager = FlowManager(self.flow_result)
        func_similarity_result: FlowResults = func_flow_manager.run_diff_flow()

        log.log_info(f'Function similarity results: \n {func_similarity_result}')

        # After Function properties and selectors have reasonably matched functions, a drill down is made into the
        # basic block and instruction level in order to further increase confidence in the match.
        self.diff_basic_blocks(func_similarity_result)

        # self.diff_basic_block_edges(func_similarity_result)
        log.log_info(f'Function similarity results: \n {func_similarity_result}')

        # TODO implement instruction level diffing

        # self.calculate_function_similarity_score()

    def diff_basic_blocks(self, func_similarity_result):
        log.log_debug(f'diff_basic_blocks: Started Processing.')
        for match in func_similarity_result.matched_bd_objects:

            confidence = match[0]
            source_match_func = match[1]
            target_match_func = match[2]
            source_match_func.populate_basic_blocks()
            target_match_func.populate_basic_blocks()

            source_bb_set: BDBasicBlockSet = BDBasicBlockSet()
            target_bb_set: BDBasicBlockSet = BDBasicBlockSet()

            for bb in source_match_func.bd_basic_blocks.values():
                source_bb_set.add(bb)
            for bb in target_match_func.bd_basic_blocks.values():
                target_bb_set.add(bb)

            log.log_info('source_bb_set: ' + str(source_bb_set))
            log.log_info('target_bb_set: ' + str(target_bb_set))

            # Create a FlowManager to handle the matching flow for basic blocks.
            if source_bb_set and target_bb_set:
                bb_flow_result = FlowResults(source_bb_set, target_bb_set)
                bb_flow_manager = FlowManager(bb_flow_result)
                bb_flow_manager.run_diff_flow()

                # Add the FlowResult object for the basic blocks comprising the BDFunctions matched.
                match.append(bb_flow_result)

                log.log_info(f'BasicBlock similarity results: \n {bb_flow_result.matched_bd_objects} \n')

    def diff_basic_block_edges(self, func_similarity_result):
        log.log_debug(f'diff_basic_block_edges: Started Processing.')
        for function_match in func_similarity_result.matched_bd_objects:
            confidence = function_match[0]
            source_match_func: BDFunction = function_match[1]
            target_match_func: BDFunction = function_match[2]
            flow_results_basic_blocks: FlowResults = function_match[3]

            for bb_match in flow_results_basic_blocks.matched_bd_objects:
                source_basic_block = bb_match[1]
                target_basic_block = bb_match[2]





    def calculate_function_similarity_score(self, confidence: int, bb_flow_result: FlowResults):
        """
        :param confidence: int - The avarage quality of all call graph level matching algorithms used to match the
                                 examined functions.
        :param bb_flow_result: - The matching results on the basic blocks of the matched functions.
        :return: function_similarity_score: int - A weighted avarage score representing the similarity of the functions.
        """
        bb_match_count = bb_flow_result.get_matched_obj_count()
        bb_avarage_confidence = bb_flow_result.get_average_quality()
