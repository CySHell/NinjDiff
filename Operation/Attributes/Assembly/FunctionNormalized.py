from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Abstracts.Attribute import Attribute
from binaryninja import *
from typing import Dict, Optional


class FunctionNormalized(Attribute):
    """
    Construct the Normalized form of a given Function.
    The normalization includes:
        * register name -> 'REG'
        * memory address -> 'MEM'
        * integer\char constant -> 'CST'
    This attribute produces a list of strings, representing the normalized disassembled code.
    """

    def __init__(self):
        super().__init__(name='FunctionNormalized', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)
        self.normalized_disassembly: List[str] = list()

    def extract_attribute(self, base_object: BDFunction) -> Optional[Dict]:
        # Check if value already exists
        FunctionNormalized_value = base_object.get_attribute_value('FunctionNormalized')

        if FunctionNormalized_value:
            pass
        else:
            for instruction_tuple in base_object.underlying_obj.instructions:
                for instruction_text_token in instruction_tuple[0]:
                    try:
                        if instruction_text_token.type == InstructionTextTokenType.RegisterToken:
                            self.normalized_disassembly.append('REG')
                        elif instruction_text_token.type in (InstructionTextTokenType.PossibleAddressToken,
                                                             InstructionTextTokenType.CodeRelativeAddressToken):
                            self.normalized_disassembly.append('MEM')
                        elif instruction_text_token.type in (InstructionTextTokenType.IntegerToken,
                                                             InstructionTextTokenType.CharacterConstantToken):
                            self.normalized_disassembly.append('CST')
                        else:
                            self.normalized_disassembly.append(instruction_text_token.text)
                    except TypeError as e:
                        log.log_debug(f'FunctionNormalized: Exception while trying to normalize - {e}')
                        pass

            FunctionNormalized_value = {
                'function_normalized': self.normalized_disassembly
            }
            FunctionNormalized_value.update({'uuid': self.create_attribute_uuid(FunctionNormalized_value)})

            base_object.add_attribute_value('FunctionNormalized', FunctionNormalized_value)

        return FunctionNormalized_value if FunctionNormalized_value else None
