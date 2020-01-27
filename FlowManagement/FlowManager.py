from typing import Set, Tuple, Dict, List, NamedTuple, Optional, AnyStr, SupportsInt

from ..Operands.Assembly.BDBasicBlock import BDBasicBlockSet
from ..Abstracts.BDObject import BDObject
from ..Abstracts.Property import Property
from ..Abstracts.Selector import Selector
from ..Abstracts.Attribute import Attribute
from ..Abstracts.BDSet import BDSet
from ..FlowManagement import PluginManager
from binaryninja import *
from ..Enums import bd_enums
from .. import Configuration
import xxhash
from .FlowResults import FlowResults


class FlowManager:
    """
    This class is the main object within the application - it is composed of two BDSets to be compared,
    and runs all the main algorithmic logic for comparing the sets via properties and selectors.
    This class is responsible for representing three sets: Potentially Matching BDObjects, Matched BDObjects and
    Unmatched BDObjects.

    A FlowManager can be invoked on any two BDSets, and will output the matches it finds.
    """

    # A list of IR's for which plugins were already loaded for.
    plugins_loaded_for_IR: [List[bd_enums.IRType]] = list()

    loaded_properties: Dict[str, Property] = dict()
    loaded_attributes: Dict[str, Attribute] = dict()
    loaded_selectors: Dict[str, Selector] = dict()

    def __init__(self, flow_result):

        self.flow_result = flow_result
        for item in self.flow_result.unmatched_sets['SourceSet']:
            self.target_bd_obj = item.bd_obj_type
            self.target_bd_IR = item.bd_obj_IR

        self.verify_sets()

        self.load_plugins()

    def load_plugins(self):
        # For each new Flow Manager that uses a new type of IR (e.g Assembly, MLIL etc) update the loaded plugins with
        # the new IR matching plugins.
        if self.target_bd_IR not in self.plugins_loaded_for_IR:
            self.loaded_properties.update(PluginManager.import_properties(self.target_bd_IR))
            self.loaded_attributes.update(PluginManager.import_attributes(self.target_bd_IR))
            self.loaded_selectors.update(PluginManager.import_selectors(self.target_bd_IR))
            self.plugins_loaded_for_IR.append(self.target_bd_IR)

        log.log_debug(f'load_plugins: Loaded the following plugins for IR {self.target_bd_IR}: \n'
                      f'Properties: {self.loaded_properties} \n '
                      f'Selectors: {self.loaded_selectors} \n'
                      f'Attributes: {self.loaded_attributes} \n')

    def verify_sets(self):
        """
        Verify the BDSets supplied are of the same IR or Target Object types.
        :return: True if same, False otherwise.
        """
        if self.flow_result.unmatched_sets['SourceSet'].base_object_IR == \
                self.flow_result.unmatched_sets['TargetSet'].base_object_IR and \
                self.flow_result.unmatched_sets['SourceSet'].base_object_type == \
                self.flow_result.unmatched_sets['TargetSet'].base_object_type:
            return True
        else:
            log.log_debug(f'FlowManager: Set types do not match. '
                          f'IR: {self.flow_result.unmatched_sets["SourceSet"].base_object_IR} != '
                          f'{self.flow_result.unmatched_sets["TargetSet"].base_object_IR}'
                          f'Object Type: {self.flow_result.unmatched_sets["SourceSet"].base_object_type} != '
                          f'{self.flow_result.unmatched_sets["TargetSet"].base_object_type}')
            return False

    def run_diff_flow(self) -> FlowResults:
        """
        This is the main algorithm for finding matched BDObjects.
        The algorithm also invokes a diffing flow between basic blocks if matching functions, or a diffing flow
        between instructions if matching basic blocks - This is done in order to further refine the matching.
        """

        log.log_debug(f'run_diff_flow(): Started Processing.'
                      f'Object type: {self.target_bd_obj.name}, IR type: {self.target_bd_IR.name}')

        # This boolean indicates if a match was found, and is used as a stopping condition for the algorithm in case
        # no more matches can be iteratively found.
        found_match: bool = False

        for property_module in self.loaded_properties.values():
            current_property: Property = property_module(self.loaded_attributes)

            log.log_debug(f'Current Property is: {current_property.property_name}')
            # Only run plugins relevant for the object and IR this flow takes care of.
            log.log_debug(f'Property IR: {property_module.target_bd_IR}, Flow IR: {self.target_bd_IR} \n'
                          f'Property obj: {property_module.target_bd_object}, Flow obj: {self.target_bd_obj} \n')
            if property_module.target_bd_IR == self.target_bd_IR \
                    and property_module.target_bd_object == self.target_bd_obj:
                # Create the initial mapping according to the currently loaded property.
                # This will update the following class attributes:
                #   1. potential_matched_sets
                #   2. unmatched_sets

                log.log_debug(f'Creating initial mapping for property: {current_property.property_name}')
                self.create_initial_mapping(current_property)

                # Use Selectors to refine the search as much as possible.
                # Each selector will attempt to uniquely match objects in the
                for selector_module in self.loaded_selectors.values():
                    # Only run plugins relevant for the object and IR this flow takes care of.
                    if selector_module.target_bd_IR == self.target_bd_IR \
                            and selector_module.target_bd_object == self.target_bd_obj:
                        log.log_debug(f'Processing Selector {selector_module.selector_name}...')
                        current_selector: Selector = selector_module(self.loaded_attributes)

                        if current_selector.selector_comparison_result_type == \
                                bd_enums.SelectorComparisonResultType.Boolean:
                            self.match_by_boolean_selector(current_selector)
                        elif current_selector.selector_comparison_result_type == \
                                bd_enums.SelectorComparisonResultType.IntDistance:
                            self.match_by_distance_selector(current_selector)

                # After all property matches were "deep dive" matched by Selectors, remove the matched objects from the
                # potential and unmatched sets so that further properties will not run on them.
                log.log_debug(f'Finished processing Property {property_module}, running cleanup_match_sets().')
                self.cleanup_match_sets()
                log.log_debug(f'Finished cleanup.')

            if found_match:
                # All properties and selectors were ran, matches were found.
                # Run the algorithm again, this time using the matched objects' parents as the base matching sets.
                found_match = False

                source_set: BDSet = BDSet()
                source_set.base_object_type = self.target_bd_obj
                source_set.base_object_IR = self.target_bd_IR
                target_set: BDSet = BDSet()
                target_set.base_object_type = self.target_bd_obj
                target_set.base_object_IR = self.target_bd_IR

                # Run the diffing flow on the parents of matched functions
                for match_pair in self.flow_result.potentially_matched_bd_objects:
                    for parent_uuid in match_pair[2].get_parents():
                        for bd_object in self.flow_result.unmatched_sets['SourceSet']:
                            if bd_object.uuid == parent_uuid:
                                source_set.add(bd_object)
                                break
                    for parent_uuid in match_pair[3].get_parents():
                        for bd_object in self.flow_result.unmatched_sets['TargetSet']:
                            if bd_object.uuid == parent_uuid:
                                target_set.add(bd_object)
                                break
                    parent_flow_result: FlowResults = FlowResults(source_set, target_set)
                    parent_flow = FlowManager(parent_flow_result)
                    parent_flow.run_diff_flow()
                    # Merge the new results into the main results object
                    self.flow_result.merge_results(parent_flow_result)

                # Run the diffing flow on the children of matched functions
                source_set.clear()
                target_set.clear()
                for match_pair in self.flow_result.potentially_matched_bd_objects:
                    for child_uuid in match_pair[2].get_children():
                        for bd_object in self.flow_result.unmatched_sets['SourceSet']:
                            if bd_object.uuid == child_uuid:
                                source_set.add(bd_object)
                                break
                    for child_uuid in match_pair[3].get_children():
                        for bd_object in self.flow_result.unmatched_sets['TargetSet']:
                            if bd_object.uuid == child_uuid:
                                target_set.add(bd_object)
                                break
                    child_flow_results: FlowResults = FlowResults(source_set, target_set)
                    child_flow: FlowManager = FlowManager(child_flow_results)
                    child_flow.run_diff_flow()
                    # Merge the new results into the main results object
                    self.flow_result.merge_results(child_flow_results)

        log.log_debug(f'{"*" * 120} \n All Properties finished processing. Matched objects are: \n')
        for match_pair in self.flow_result.matched_bd_objects:
            log.log_debug(f'{"*" * 120} \n\n {match_pair[1]} <-> '
                          f'{match_pair[2]}'
                          f', Confidence: {match_pair[0]} \n'
                          )

        return self.flow_result

    def _refine_potential_matches(self):
        # Further refine the potential matches by applying a confidence score to the match based on the
        # amount and quality of selectors used to match them.
        # If a match is determined to be below the threshold defined in the Configuration file both BDObjects are
        # returned to the un-matched pool for further matching attempts.

        threshold = Configuration.DEFAULT_THRESHOLD
        if self.target_bd_obj == bd_enums.TargetType.Function:
            threshold = Configuration.FUNCTION_SELECTOR_THRESHOLD
        if self.target_bd_obj == bd_enums.TargetType.BasicBlock:
            threshold = Configuration.BASIC_BLOCK_SELECTOR_THRESHOLD
        if self.target_bd_obj == bd_enums.TargetType.Instruction:
            threshold = Configuration.INSTRUCTION_SELECTOR_THRESHOLD

        log.log_debug(f'_refine_potential_matches: Processing with threshold {threshold}')

        for potential_match in self.flow_result.potentially_matched_bd_objects:
            [_, selector_confidence, source_match_obj, target_match_obj] = potential_match
            if selector_confidence < threshold:
                # By removing the potential_match from the list, it will not be deleted from the un-matched sets and
                # thus further matching attempts will be made on the objects.
                self.flow_result.potentially_matched_bd_objects.remove(potential_match)
            else:
                self.flow_result.matched_bd_objects.append([selector_confidence, source_match_obj, target_match_obj])

    def cleanup_match_sets(self):
        """
        Responsible for removing all the matched BDObjects from the potential matches or unmatched sets.
        """

        # Remove matches with low confidence before performing cleanup
        self._refine_potential_matches()

        for [_, _, source_match_obj, target_match_obj] in self.flow_result.potentially_matched_bd_objects:
            if source_match_obj in self.flow_result.unmatched_sets['SourceSet']:
                self.flow_result.unmatched_sets['SourceSet'].remove(source_match_obj)
            if target_match_obj in self.flow_result.unmatched_sets['TargetSet']:
                self.flow_result.unmatched_sets['TargetSet'].remove(target_match_obj)

        # Clear the potential candidates list for the next Property diffing.
        self.flow_result.potentially_matched_bd_objects.clear()

    def create_initial_mapping(self, current_property: Property):
        """
        An initial "base" mapping is created by first dividing the sets into subsets of nodes that are coarsely related
        by using all Property objects found in the plugins directory, and later for each of the subset groups match
        them in a more refined way using the input selector.
        """

        log.log_debug(f'\nProcessing Property {current_property.__class__}\n')

        matched_sets: List[Tuple[BDSet, BDSet]] = current_property.exec_comparison_heuristic(
            self.flow_result.unmatched_sets["SourceSet"],
            self.flow_result.unmatched_sets["TargetSet"]
        )
        log.log_debug(f'Property {current_property.property_name} found {len(matched_sets)} matching sets.\n')

        # Re-initialize the potential_matched_sets as the new initial mapping
        self.potential_matched_sets = matched_sets

    def match_by_boolean_selector(self, selector: Selector):
        """
        Tries to uniquely match the objects in each source potential set to an object in target potential set using
        the given selector.
        This function only works on selectors that return a boolean value (meaning a True\False statement about the
        similarity of the objects).
        """
        for potential_source_set, potential_target_set in self.potential_matched_sets:
            log.log_info(f'Selector {selector.selector_name}: Started processing. \n')
            for source_obj in potential_source_set:
                # Only a unique match applies - i.e if the source matches more then 1 single destination object
                # then no match is recorded.
                match_count = 0
                matched_objs: Optional[Tuple[BDObject, BDObject]] = None
                for target_obj in potential_target_set:
                    if selector.exec_comparison_heuristic(source_obj, target_obj):
                        if match_count > 1:
                            # More then 1 match, no unique match found.
                            matched_objs = None
                            break
                        else:
                            match_count += 1
                            matched_objs = (source_obj, target_obj)

                if matched_objs:
                    # The Selector has found a unique match between the source and target objects.
                    matched_objs_uuid = xxhash.xxh64(str(matched_objs[0].uuid) + str(matched_objs[1].uuid)).intdigest()
                    existing_match = None
                    for potential_match in self.flow_result.potentially_matched_bd_objects:
                        if potential_match[0] == matched_objs_uuid:
                            existing_match = True
                            # Calculate the avarage selector quality
                            potential_match[1] = (potential_match[1] + selector.selector_quality.value) / 2
                            break
                    if not existing_match:
                        # If the pair of Objects has yet to be matched by a selector, enter the first entry for it
                        # in the potential table.
                        self.flow_result.potentially_matched_bd_objects.append([matched_objs_uuid,
                                                                                selector.selector_quality.value,
                                                                                matched_objs[0], matched_objs[1]])
                        log.log_debug(f'Selector {selector.selector_name} found a match: {matched_objs[0]} <-> '
                                      f'{matched_objs[1]}, '
                                      f'{selector.selector_quality.value}')

    def match_by_distance_selector(self, selector: Selector):
        """
        Tries to uniquely match the objects in each source potential set to an object in target potential set using
        the given selector as an int value indicating the similarity distance between the objects.
        This function only works on selectors that return an int value (meaning a similarity score between 2 objects).
        The match is made by finding the closest unique between the scores. (scores do NOT need to be equal, just close)
        """

        for potential_source_set, potential_target_set in self.potential_matched_sets:
            for source_obj in potential_source_set:
                # Only a unique match applies - i.e if the source matches more then 1 single destination object
                # then no match is recorded.
                minimal_match_score = pow(2, 32)
                matched_objs: Optional[Tuple[BDObject, BDObject]] = None
                for target_obj in potential_target_set:
                    current_match_score = selector.exec_comparison_heuristic(source_obj, target_obj)
                    if current_match_score == minimal_match_score:
                        minimal_match_score = pow(2, 32)
                        matched_objs = None
                    elif current_match_score < minimal_match_score:
                        minimal_match_score = current_match_score
                        matched_objs = (source_obj, target_obj)

                if matched_objs:
                    # A unique minimal match was found

                    matched_objs_uuid = xxhash.xxh64(str(matched_objs[0].uuid) + str(matched_objs[1].uuid)).intdigest()
                    existing_match = False
                    for potential_match in self.flow_result.potentially_matched_bd_objects:
                        if potential_match[0] == matched_objs_uuid:
                            existing_match = True
                            # Calculate the average selector quality
                            potential_match[1] = (potential_match[1] + selector.selector_quality.value) / 2
                            break
                    if not existing_match:
                        # If the pair of Objects has yet to be matched by a selector, enter the first entry for it
                        # in the potential table.
                        self.flow_result.potentially_matched_bd_objects.append([matched_objs_uuid,
                                                                                selector.selector_quality.value,
                                                                                matched_objs[0], matched_objs[1]])
                        log.log_debug(f'Selector {selector} found a match: {matched_objs[0]} <-> '
                                      f'{matched_objs[1]}, '
                                      f'{selector.selector_quality.value}')

