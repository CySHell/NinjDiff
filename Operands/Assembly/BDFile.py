from Abstracts.BDObject import BDObject
from Abstracts.BDSet import BDSet
from typing import Set
import binaryninja
from Enums import bd_enums


class BDFile(BDObject):
    """
    Represents a File operand for comparisons
    """

    bd_obj_type = bd_enums.TargetType.File
    bd_obj_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, bv: binaryninja.BinaryView):
        super().__init__()
        self.bv: binaryninja.BinaryView = bv
        self.uuid = self.bv.name
        self.name = self.bv.name

    def get_parents(self):
        pass

    def get_children(self):
        pass


class BDFileSet(BDSet):
    """
    A set of binary ninja BinaryViews.
    """

    base_object_type: bd_enums.TargetType = bd_enums.TargetType.File
    base_object_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, bv: binaryninja.BinaryView):
        super().__init__()
        self.underlying_object: binaryninja.BinaryView = bv
        self.bd_set: Set[BDFile] = self.create_set()

    def create_set(self) -> Set[BDFile]:
        bv_set = set()
        bv_set.add(BDFile(self.underlying_object))
        return bv_set
