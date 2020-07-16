from abc import *
from ..Enums import bd_enums
from .BDObject import BDObject
from typing import *
import xxhash


class Attribute(ABC):
    """
    Base class for Attributes.
    An Attribute object represents the operation needed to "extract" (get) the relevant information from the inspected
    object in order to later perform the comparison.
    """

    @staticmethod
    def create_attribute_uuid(attribute_features: Dict) -> str:
        # a UUID value specific for this attribute.
        # This value is used to search the DB for an existing attribute that is identical to this one.
        # This UUID is used only for attributes with more then 1 property (which makes them hard to search in the DB),
        # and should be None if it only has 1 property (In which case the single property will act as the UUID).
        uuid_hash = xxhash.xxh32()
        for key, value in attribute_features.items():
            uuid_hash.update(key)
            uuid_hash.update(str(value))

        return uuid_hash.hexdigest()

    def __init__(self, name: str, value_type: bd_enums.AttrScope, ir_type: bd_enums.IRType,
                 target_type: bd_enums.TargetType, dependencies: List[AnyStr] = None):
        self.value_type = value_type
        self.IR = ir_type
        self.name = name
        self.attribute_target = target_type
        # dependencies is a list of strings, each string is a dependency attribute name.
        self.dependencies = dependencies



    @abstractmethod
    def extract_attribute(self, base_object: BDObject):
        """
        Extract the attribute from the base object, and store the value
        :param base_object: the BDObject to extract from
        :return: dict of {value_name: value}
        """
        pass
