from typing import List, Dict
from Abstracts.Selector import Selector
from Abstracts.Attribute import Attribute
from Enums import bd_enums
from Operands.Assembly.BDFunction import BDFunction
from datasketch import MinHashLSHEnsemble, MinHash
from .... import Configuration

class function_lsh_ensemble(Selector):
    """
    Compare the fuzzy hash (lsh - Locality Sensitive Hashing) of all assembly instructions of 2 functions, mainly
    looking for intersection between the instruction sets.
    This Attribute currently uses the MinHash LSH function.
    See http://ekzhu.com/datasketch/lshensemble.html#minhash-lsh-ensemble for further information.
    """

    needed_attributes: List[str] = ['FunctionMinHashLSH', 'FunctionNormalized']
    selector_name: str = 'function_lsh_ensemble'
    selector_quality: bd_enums.SelectorQuality = bd_enums.SelectorQuality.Medium
    selector_algorithm_performance: bd_enums.SelectorAlgoPerf = bd_enums.SelectorAlgoPerf.Poor
    target_bd_object: bd_enums.TargetType = bd_enums.TargetType.Function
    target_bd_IR: bd_enums.IRType = bd_enums.IRType.Assembly

    def __init__(self, loaded_attributes: Dict[str, Attribute]):
        super().__init__(loaded_attributes)

    def exec_comparison_heuristic(self, source_func: BDFunction, target_func: BDFunction) \
            -> bool:

        # Populate the attribute values
        source_hash = self.loaded_attributes['FunctionMinHashLSH'].extract_attribute(source_func)

        target_hash = self.loaded_attributes['FunctionMinHashLSH'].extract_attribute(target_func)

        # Create an LSH Ensemble index with threshold and number of partition
        # settings.
        lshensemble = MinHashLSHEnsemble(threshold=Configuration.MINHASH_LSH_ENSEMBLE_THRESHOLD,
                                         num_perm=Configuration.MINHASH_PERMUTATIONS,
                                         num_part=Configuration.MINHASH_LSH_ENSEMBLE_PARTITIONS)

        lshensemble.index([("source_function", source_hash, len()), ("m3", m3, len(set3))])


        if source_hash == target_hash:
            return True

        return False
