from .Enums import bd_enums

user1 = 'user'
user2 = 'rowr1'
current_user = user2

operation_folder_path = f'C:\\Users\\{current_user}\\AppData\\Roaming\\Binary Ninja\\plugins\\NinjDiff\\Operation\\'
debug_file_path = f'C:\\Users\\{current_user}\\AppData\\Roaming\\Binary Ninja\\plugins\\NinjDiff\\debug_log.log'

default_selector_path = [(operation_folder_path + 'Selectors\\' + target_ir.name) for target_ir in bd_enums.IRType]
default_property_path = [(operation_folder_path + 'Properties\\' + target_ir.name) for target_ir in bd_enums.IRType]
default_attributes_path = [(operation_folder_path + 'Attributes\\' + target_ir.name) for target_ir in bd_enums.IRType]

# Minimum amount of assembly instructions does a function need to have in order to be considered for matching
MIN_FUNCTION_LENGTH: int = 4

# Thresholds
# Determines the minimum confidence score of a potential match. Matches below this minimum will be marked
# as unmatched and will be returned to the unmatched pool.
# This threshold should be VERY low as to not miss single weak matches within a huge set of matched objects (for
# instance a basic block that is weakly matched inside a function who matched all its other basic blocks).
FUNCTION_SELECTOR_THRESHOLD: int = 20

BASIC_BLOCK_SELECTOR_THRESHOLD: int = 20

INSTRUCTION_SELECTOR_THRESHOLD: int = 20

DEFAULT_THRESHOLD: int = 20


MINHASH_PERMUTATIONS: int = 128
MINHASH_SEED: int = 1
MINHASH_LSH_ENSEMBLE_THRESHOLD: float = 0.9
MINHASH_LSH_ENSEMBLE_PARTITIONS: int = 32



# Function Similarity weights
# Weight ~25%: quota of matched flow graph edges to total edges
#
# Weight ~25%: quota of matched basic blocks to total basic blocks
#
# Weight ~0%: quota of matched instructions to total instructions
#
# Weight ~50%: difference in flow graph MD index

