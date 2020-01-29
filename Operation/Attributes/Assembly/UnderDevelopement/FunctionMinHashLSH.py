from Enums import bd_enums
from Operands.Assembly.BDFunction import BDFunction
from Abstracts.Attribute import Attribute
import hashlib
import pyprimesieve
from binaryninja import *
from typing import Dict
from datasketch import MinHashLSHEnsemble, MinHash
from .... import Configuration


class FunctionMinHashLSH(Attribute):
    """
    Caculate the MinHash of the function (over all its normalized instructions).
    This LSH can later be used by selectors to "fuzzy" match this function to others.
    See http://ekzhu.com/datasketch/lshensemble.html#minhash-lsh-ensemble for further information.
    """

    def __init__(self):
        super().__init__(name='FunctionMinHashLSH', value_type=bd_enums.AttrScope.INT,
                         ir_type=bd_enums.IRType.Assembly, target_type=bd_enums.TargetType.Function)

    def extract_attribute(self, base_object: BDFunction) -> int:
        # Check if value already exists
        FunctionMinHashLSH_value = base_object.get_attribute_value('FunctionMinHashLSH')

        if FunctionMinHashLSH_value:
            pass
        else:
            normalized_instr_set: set = set(base_object.get_attribute_value('FunctionNormalized'))

            # Create MinHash object
            minhash = MinHash(num_perm=Configuration.MINHASH_PERMUTATIONS, seed=Configuration.MINHASH_SEED)
            for instr in normalized_instr_set:
                minhash.update(instr.encode('utf8'))

            base_object.add_attribute_value('FunctionMinHashLSH', {'function_lsh': minhash.digest()})
            FunctionMinHashLSH_value = base_object.get_attribute_value('FunctionMinHashLSH')

        return FunctionMinHashLSH_value['function_lsh'] if FunctionMinHashLSH_value else None

