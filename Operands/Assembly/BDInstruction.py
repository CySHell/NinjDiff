from Abstracts.BDObject import BDObject
from Abstracts.BDSet import BDSet
from Enums import bd_enums
import binaryninja
from typing import Set


class BDInstruction(BDObject):
    """
    Represents an Instruction operand for comparisons
    """

    bd_obj_type = bd_enums.TargetType.Instruction
    bd_obj_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, instr: binaryninja.MediumLevelILInstruction):
        super().__init__()
        self.underlying_obj: binaryninja.MediumLevelILInstruction = instr
        self.uuid = self.underlying_obj.instr_index

    def get_parents(self):
        pass

    def get_children(self):
        pass


class BDInstructionSet(BDSet):
    """
    A set of assembly basic blocks.
    """

    base_object_type: bd_enums.TargetType = bd_enums.TargetType.Instruction
    base_object_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, bb: binaryninja.MediumLevelILBasicBlock):
        super().__init__()
        self.underlying_object: binaryninja.MediumLevelILBasicBlock = bb
        self.bd_set: Set[BDInstruction] = self.create_set()

    def create_set(self) -> Set[BDInstruction]:
        instr_set = set()
        containing_function: binaryninja.MediumLevelILFunction = self.underlying_object.function.mlil
        for instr_index in range(self.underlying_object.start, self.underlying_object.end):
            instr_set.add(BDInstruction(containing_function[instr_index]))

        return instr_set
