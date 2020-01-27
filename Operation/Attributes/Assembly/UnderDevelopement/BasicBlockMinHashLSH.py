from Enums import bd_enums
from Operands.Assembly.BDBasicBlock import BDBasicBlock
from Abstracts.Attribute import Attribute
import hashlib
import pyprimesieve
from binaryninja import *
from typing import Dict
from datasketch import MinHashLSHEnsemble, MinHash
from .... import Configuration


class BasicBlockMinHashLSH(Attribute):
    """
    Caculate the MinHash of the basic block.
    This LSH can later be used by selectors to "fuzzy" match this basic block to others.
    See http://ekzhu.com/datasketch/lshensemble.html#minhash-lsh-ensemble for further information.
    """

    def __init__(self):
        super().__init__(name='BasicBlockMinHashLSH', value_type=bd_enums.AttrValueType.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.BasicBlock)

    def extract_attribute(self, base_object: BDBasicBlock) -> int:
        # Check if value already exists
        BasicBlockMinHashLSH_value = base_object.get_attribute_value('BasicBlockMinHashLSH')

        if BasicBlockMinHashLSH_value:
            pass
        else:
            normalized_instr_set: set = set(base_object.get_attribute_value('BasicBlockNormalized'))

            # Create MinHash object
            minhash = MinHash(num_perm=Configuration.MINHASH_PERMUTATIONS, seed=Configuration.MINHASH_SEED)
            for instr in normalized_instr_set:
                minhash.update(instr.encode('utf8'))

            base_object.add_attribute_value('BasicBlockMinHashLSH', {'bb_lsh': minhash.digest()})
            BasicBlockMinHashLSH_value = base_object.get_attribute_value('BasicBlockMinHashLSH')

        return BasicBlockMinHashLSH_value['bb_lsh'] if BasicBlockMinHashLSH_value else None

