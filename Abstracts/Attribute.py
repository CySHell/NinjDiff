from abc import *
from ..Enums import bd_enums
from .BDObject import BDObject


class Attribute(ABC):
    """
    Base class for Attributes.
    An Attribute object represents the operation needed to "extract" (get) the relevant information from the inspected
    object in order to later perform the comparison.
    """

    def __init__(self, name: str, value_type: bd_enums.AttrScope, ir_type: bd_enums.IRType,
                 target_type: bd_enums.TargetType):

        self.value_type = value_type
        self.IR = ir_type
        self.name = name
        self.attribute_target = target_type

    @abstractmethod
    def extract_attribute(self, base_object: BDObject):
        """
        Extract the attribute from the base object, and store the value
        :param base_object: the BDObject to extract from
        :return: dict of {value_name: value}
        """
        pass

