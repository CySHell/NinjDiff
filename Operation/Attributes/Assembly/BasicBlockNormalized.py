from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
import hashlib
import pyprimesieve
from binaryninja import *
from typing import Dict, Optional


class BasicBlockNormalized(Attribute):
    """
    Construct the Normalized form of a given basic block.
    The normalization includes:
        * register name -> 'REG'
        * memory address -> 'MEM'
        # integer\char constant -> 'CST'
    This attribute produces a list of strings, representing the normalized disassembled code.
    """

    def __init__(self):
        super().__init__(name='BasicBlockNormalized', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> Optional[Dict]:
        # Check if value already exists
        BasicBlockNormalized_value = base_object.get_attribute_value('BasicBlockNormalized')

        if BasicBlockNormalized_value:
            pass
        else:
            normalized_disassembly: List[str] = list()
            for instruction_tuple in base_object.underlying_obj:
                for instruction_text_token in instruction_tuple[0]:
                    try:
                        if instruction_text_token.type == InstructionTextTokenType.RegisterToken:
                            normalized_disassembly.append('REG')
                        elif instruction_text_token.type in (InstructionTextTokenType.PossibleAddressToken,
                                                             InstructionTextTokenType.CodeRelativeAddressToken):
                            normalized_disassembly.append('MEM')
                        elif instruction_text_token.type in (InstructionTextTokenType.IntegerToken,
                                                             InstructionTextTokenType.CharacterConstantToken):
                            normalized_disassembly.append('CST')
                        else:
                            normalized_disassembly.append(instruction_text_token.text)
                    except TypeError as e:
                        log.log_debug(f'BasicBlockNormalized: Exception while trying to normalize - {e}')
                        pass

            BasicBlockNormalized_value = {
                'bb_normalized': normalized_disassembly
            }

            BasicBlockNormalized_value.update({'uuid': self.create_attribute_uuid(BasicBlockNormalized_value)})
            base_object.add_attribute_value('BasicBlockNormalized', BasicBlockNormalized_value)

        return BasicBlockNormalized_value if BasicBlockNormalized_value else None
