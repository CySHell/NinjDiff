from ..Enums import bd_enums
from typing import Set
from ..Abstracts.BDObject import BDObject


class BDSet(set):
    """
    This class represents a single set of BDObjects.
    The set objects are extracted from an underlying layer, such as binary ninja or some other disassembler (the
     specific implementation of the data extraction and BDObject creation is handled by subclasses to this class.
    """

    # Declare what the underlying binary ninja type of the BDObject in the set is (i.e Function, BasicBlock etc)
    base_object_type: bd_enums.TargetType
    # Declare what the underlying binary ninja IR type of the BDObject in the set is (i.e MLIL, ASM, LLIL etc)
    base_object_IR: bd_enums.IRType

    def __init__(self):
        super().__init__()

    def add(self, bd_object: BDObject):
        """
        Add a BDObject to the set
        """
        if (bd_object.bd_obj_type == self.base_object_type) and (bd_object.bd_obj_IR == self.base_object_IR):
            super().add(bd_object)
        else:
            print(f'BDObject provided does not match the Sets\' base object type\\IR')

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__repr__()