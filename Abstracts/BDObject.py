from abc import *
from typing import List, Dict
from ..Enums import bd_enums
import xxhash


class BDObject(ABC):
    """
    Base class for all operands (file, function, basic block, instruction etc)
    BD = Binary Diff
    """

    bd_obj_type: bd_enums.TargetType
    bd_obj_IR: bd_enums.IRType

    def __init__(self):
        self.registered_attributes = List[str]  # attributes to extract from this object
        self.underlying_obj: object             # The actual object represented by this BDObject
                                                # (i.e BinaryView, BasicBlock etc)
        self.uuid: int = 0                      # The uuid of the object, this can mean different things for different
                                                # objects.
                                                # Obtained by the self.generate_uuid() static method.
                                                # (i.e index of a bb, address of an instruction etc)
        self.parents: List[str] = self.get_parents()
        self.children: List[str] = self.get_children()
        self.extracted_attributes: Dict[str, dict] = dict()

    @abstractmethod
    def get_parents(self) -> List[str]:
        """
        :return: list containing uuid of each parent BDObject
        """
        pass

    @abstractmethod
    def get_children(self) -> List[str]:
        """
        :return: list containing uuid of each child BDObject
        """
        pass

    def add_attribute_value(self, attr_name: str, attr_results: dict):
        self.extracted_attributes.update({attr_name: attr_results})

    def get_attribute_value(self, attr_name: str):
        return self.extracted_attributes.get(attr_name)

    def get_all_attribute_values(self):
        return self.extracted_attributes

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __eq__(self, target_obj):
        if self.bd_obj_type == target_obj.bd_obj_type:
            if self.uuid == target_obj.uuid:
                return True
        return False

    @staticmethod
    @abstractmethod
    def generate_uuid(**kwargs):
        pass

    @abstractmethod
    def __hash__(self):
        return self.uuid
