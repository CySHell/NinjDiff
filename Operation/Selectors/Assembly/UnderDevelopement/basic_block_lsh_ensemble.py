# Create an LSH Ensemble index with threshold and number of partition
# settings.
lshensemble = MinHashLSHEnsemble(threshold=Configuration.MINHASH_LSH_ENSEMBLE_THRESHOLD,
                                 num_perm=Configuration.MINHASH_PERMUTATIONS,
                                 num_part=Configuration.MINHASH_LSH_ENSEMBLE_PARTITIONS)