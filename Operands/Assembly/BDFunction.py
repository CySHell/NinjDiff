from ...Abstracts.BDObject import BDObject
from ...Abstracts.BDSet import BDSet
from .BDBasicBlock import BDBasicBlock
from ...Enums import bd_enums
import binaryninja
import xxhash
from typing import Dict
from ... import Configuration

class BDFunction(BDObject):
    """
    Represents a Function operand for comparisons
    """

    bd_obj_type = bd_enums.TargetType.Function
    bd_obj_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, bn_func: binaryninja.Function):
        self.underlying_obj: binaryninja.Function = bn_func
        super().__init__()
        self.uuid = self.generate_uuid(self.underlying_obj)

        # bd_basic_blocks {BDBasicBlock.uuid: BDBasicBlock
        self.bd_basic_blocks: Dict[int, BDBasicBlock] = dict()

    def get_parents(self):
        parents_list = list()
        for func in self.underlying_obj.callers:
            parents_list.append(self.generate_uuid(func))
        return parents_list

    def get_children(self):
        children_list = list()
        for func in self.underlying_obj.callees:
            children_list.append(self.generate_uuid(func))
        return children_list

    @staticmethod
    def generate_uuid(underlying_function_object: binaryninja.Function):
        uuid = xxhash.xxh32()
        uuid.update(underlying_function_object.name)
        uuid.update(underlying_function_object.view.file.filename)

        return uuid.intdigest()

    def populate_basic_blocks(self):
        if self.bd_basic_blocks:
            # Basic Blocks are already populated
            pass
        else:
            for bb in self.underlying_obj.basic_blocks:
                if bb.instruction_count >= Configuration.MIN_BASIC_BLOCK_INSTRUCTION_LENGTH:
                    bd_basic_block = BDBasicBlock(bb, self)
                    self.bd_basic_blocks.update({bd_basic_block.uuid: bd_basic_block})

    def __hash__(self):
        return self.uuid

    def __repr__(self):
        return self.underlying_obj.name

    def __str__(self):
        return self.underlying_obj.name


class BDFunctionSet(BDSet):
    """
    A set of assembly Functions.
    """

    base_object_type: bd_enums.TargetType = bd_enums.TargetType.Function
    base_object_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self):
        super().__init__()
