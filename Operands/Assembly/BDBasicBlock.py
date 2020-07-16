from typing import Tuple

from ...Abstracts.BDObject import BDObject
from ...Abstracts.BDSet import BDSet
from ...Enums import bd_enums
import binaryninja
import xxhash


class BDBasicBlock(BDObject):
    """
    Represents a Basic Block operand for comparisons
    """

    bd_obj_type = bd_enums.TargetType.BasicBlock
    bd_obj_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, bn_basic_block: binaryninja.BasicBlock, parent_bd_function):
        self.underlying_obj: binaryninja.BasicBlock = bn_basic_block
        self.parent_bd_function = parent_bd_function
        super().__init__()
        self.uuid = self.generate_uuid(self.underlying_obj)

    def get_parents(self):
        children_list = list()
        for incoming_branch in self.underlying_obj.incoming_edges:
            children_list.append(self.generate_uuid(incoming_branch.target))
        return children_list

    def get_children(self):
        parents_list = list()
        for outgoing_branch in self.underlying_obj.outgoing_edges:
            parents_list.append(self.generate_uuid(outgoing_branch.target))
        return parents_list

    @staticmethod
    def generate_uuid(bn_basic_block: binaryninja.BasicBlock):
        uuid = xxhash.xxh32()
        uuid.update(str(bn_basic_block.disassembly_text))
        uuid.update(str(bn_basic_block.index))
        uuid.update(bn_basic_block.function.name)
        uuid.update(bn_basic_block.view.file.filename)

        return uuid.intdigest()

    def __hash__(self):
        return self.uuid

    def __repr__(self):
        return hex(self.underlying_obj.start) + '-' + str(self.underlying_obj.index)

    def __str__(self):
        return self.__repr__()


class BDBasicBlockEdge(BDObject):
    """
    Represents a Control Flow Graph edge - a directed link between 2 BDBasicBlock objects.
    """

    bd_obj_type = bd_enums.TargetType.BasicBlockEdge
    bd_obj_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, source_bd_bb: BDBasicBlock, target_bd_bb: BDBasicBlock):
        self.underlying_obj: Tuple = (source_bd_bb, target_bd_bb)
        super().__init__()
        self.uuid = self.generate_uuid(self.underlying_obj[0], self.underlying_obj[1])

    def get_parents(self) -> None:
        return None

    def get_children(self) -> None:
        return None

    @staticmethod
    def generate_uuid(source_bd_bb: BDBasicBlock, target_bd_bb: BDBasicBlock):
        uuid = xxhash.xxh32()
        uuid.update(str(source_bd_bb.uuid))
        uuid.update(str(target_bd_bb.uuid))
        return uuid.intdigest()

    def __hash__(self):
        return self.uuid

    def __repr__(self):
        return f'{self.underlying_obj[0]} -> {self.underlying_obj[1]}'

    def __str__(self):
        return f'{self.underlying_obj[0]} -> {self.underlying_obj[1]}'


class BDBasicBlockSet(BDSet):
    """
    A set of assembly Basic Blocks.
    """

    base_object_type: bd_enums.TargetType = bd_enums.TargetType.BasicBlock
    base_object_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self):
        super().__init__()
