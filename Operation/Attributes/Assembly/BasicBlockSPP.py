from ....Enums import bd_enums
from ....Operands.Assembly.BDFunction import BDFunction
from ....Operands.Assembly.BDBasicBlock import BDBasicBlock
from ....Abstracts.Attribute import Attribute
import hashlib
import pyprimesieve
from binaryninja import *
from typing import Dict, Optional
import Configuration


class BasicBlockSPP(Attribute):
    """
    Construct the Small Prime Product value of a given basic block.
    """

    # This dict caches all values discovered in order to make the extraction process faster.
    opcode_to_prime: Dict[str, int] = dict()
    modulu_value = Configuration.MAX_INT

    def __init__(self):
        super().__init__(name='BasicBlockSPP', value_type=bd_enums.AttrScope.InVariant,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)
        self.spp_value = 1

    def extract_attribute(self, base_object: BDBasicBlock) -> Optional[Dict]:
        # Check if value already exists
        BasicBlockSPP_value = base_object.get_attribute_value('BasicBlockSPP')

        if BasicBlockSPP_value:
            pass
        else:
            for instruction_tuple in base_object.underlying_obj:
                for instruction_text_token in instruction_tuple[0]:
                    try:
                        if instruction_text_token.type == InstructionTextTokenType.InstructionToken:
                            mapped_prime = self.get_mapped_prime(instruction_text_token.text.encode('utf8'))
                            self.spp_value = (self.spp_value * mapped_prime) % self.modulu_value
                    except TypeError:
                        pass

            BasicBlockSPP_value = {
                'bb_spp': self.spp_value
            }

            base_object.add_attribute_value('BasicBlockSPP', BasicBlockSPP_value)

        return BasicBlockSPP_value if BasicBlockSPP_value else None

    def get_mapped_prime(self, token: str):

        prime = self.opcode_to_prime.get(token)
        if prime:
            pass
        else:
            helper_hash = hashlib.blake2b(digest_size=3)
            helper_hash.update(token)
            prime = pyprimesieve.primes_nth(int(helper_hash.hexdigest(), 16))
            self.opcode_to_prime[token] = prime

        return prime
