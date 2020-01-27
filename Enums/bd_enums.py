from enum import *


@unique
class TargetType(Enum):
    File = 1
    Function = 2
    FunctionEdge = 3
    BasicBlock = 4
    BasicBlockEdge = 5
    Instruction = 6
    InstructionSeries = 7



@unique
class AttrValueType(IntEnum):
    Boolean = 1
    INT = 2
    STR = 3
    DICT = 4
    LIST = 5


@unique
class SelectorComparisonResultType(IntEnum):
    Boolean = 1
    IntDistance = 2


@unique
class IRType(Enum):
    Assembly = 'Assembly'
    LLIL = 'LLIL'
    MLIL = 'MLIL'
    HLIL = 'HLIL'


@unique
class AttrValueType(IntEnum):
    Boolean = 1
    INT = 2
    STR = 3
    DICT = 4
    LIST = 5
    FLOAT = 6

@unique
class SelectorAlgoPerf(IntEnum):
    # The performance estimation of the selector algorithm
    VeryPoor = 1
    Poor = 2
    Medium = 3
    Good = 4
    VeryGood = 5


@unique
class SelectorQuality(IntEnum):
    # Quality of the selector result, used to calculate the match confidence
    VeryPoor = 10
    Poor = 20
    Medium = 30
    Good = 40
    VeryGood = 50
    Perfect = 100

@unique
class PropertyQuality(IntEnum):
    # Quality of the selector result
    VeryPoor = 1
    Poor = 2
    Medium = 3
    Good = 4
    VeryGood = 5


@unique
class PropertyAlgoPerf(IntEnum):
    # The performance estimation of the selector algorithm
    VeryPoor = 1
    Poor = 2
    Medium = 3
    Good = 4
    VeryGood = 5