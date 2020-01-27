from typing import *
from ..Abstracts import BDObject, BDSet


class FlowResults:
    """
    Each FlowManager instance holds a FlowResults class as a means of returning results to the diffing manager for
    aggregation.
    """

    def __init__(self, source_base_set: BDSet, target_base_set: BDSet):

        # Main containers for facilitating the FlowManagers' algorithm

        # matched_bd_objects: Contains the BDObjects that passed the similarity thresh hold defined in the Configuration
        #                     file, along with the average selector confidence for the pair.
        #                     Each matched pair of objects may also contain the FlowResults object for the
        #                     sub-BDObjects that compose it (e.g a BDFunction entry will contain the FlowResults
        #                     of its matched BDBasicBlock).
        self.matched_bd_objects: List[List[AnyStr, BDObject, BDObject, FlowResults]] = list()
        # potentially_matched_bd_objects: A list containing objects that were matched by different Selectors. The
        #                                 selector quality is added to the overall match quality in each tuple in
        #                                 order to calculate the confidence score for this match.
        #                                 If the confidence score is higher then the threshold defined in the Config
        #                                 file, the BDObjects are moved to the matched_bd_objects list.
        #                                 The first item in the tuple represents the uuid of the 2 BDObjects in order
        #                                 to quickly evaluate if the pair has already been matched by another Selector.
        self.potentially_matched_bd_objects: List[List[AnyStr, SupportsInt, BDObject, BDObject]] = list()
        # potential_matched_sets: A list containing tuples of sets that contain BDObjects that were detected by a
        #                         Property to be similar.
        #                         The sets will be further refined by running Selectors on them.
        self.potential_matched_sets: List[Tuple[BDSet, BDSet]] = list()
        # unmatched_sets: This dictionary contains all the unmatched BDObjects.
        #                 Property objects will run on these BDObjects and find potential matches that will be further
        #                 refined by Selectors.
        self.unmatched_sets: Dict[AnyStr, BDSet, AnyStr, BDSet] = {'SourceSet': source_base_set,
                                                                   'TargetSet': target_base_set}

    def merge_results(self, result_to_merge):
        # Add each new matched BDObject pair to matched list, and remove the pair from the unmatched list
        for matched_bd_object in result_to_merge.matched_bd_objects:
            if matched_bd_object not in self.matched_bd_objects:
                self.matched_bd_objects.append(matched_bd_object)
            if matched_bd_object[1] in self.unmatched_sets['SourceSet']:
                self.unmatched_sets['SourceSet'].remove(matched_bd_object[1])
            if matched_bd_object[2] in self.unmatched_sets['TargetSet']:
                self.unmatched_sets['TargetSet'].remove(matched_bd_object[1])

    def get_average_quality(self) -> int:
        """
        :return: The average confidence of all the matched results combined.
        """
        average_quality = 0
        for match in self.matched_bd_objects:
            average_quality = (average_quality + match[0]) / 2

        return average_quality

    def get_matched_obj_count(self):
        """
        :return: Amount of matched objects.
        """
        return len(self.matched_bd_objects)

    def __repr__(self):
        repr_str = '*' * 60
        for match in self.matched_bd_objects:
            repr_str += str(match[1]) + "<->" + str(match[2]) + " -- Confidence: " + str(match[0]) + "\n"
            # If a FlowResult exists for the sub-BDObjects comprising this match exists, print it too
            if len(match) == 4:
                repr_str += f'Sub-Objects flow result for this match: \n {match[3]}'
        repr_str += '*' * 60 + '\n'
        return repr_str

    def __str__(self):
        return self.__repr__()
