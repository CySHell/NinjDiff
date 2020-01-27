from binaryninja import *
from neo4j import GraphDatabase, StatementResult, Session
from .. import Configuration
from typing import Optional
import xxhash
from ..Operands.Assembly.BDFunction import BDFunction
from ..Operands.Assembly.BDBasicBlock import BDBasicBlock
from . import PluginManager
from ..Abstracts.Attribute import Attribute
from ..Enums import bd_enums
from typing import *


class DBManager:
    """
    Responsible for populating a Neo4j graph with all the attributes of the functions it receives from BinaryNinja.
    The default DBManager will only populate Assembly form of the function, but other IR forms (LLIL \ MLIL \ HLIL)
    will be possible in the future.
    """
    loaded_attributes: Dict[str, Attribute] = dict()

    ocb: str = '{'
    ccb: str = '}'

    def __init__(self, bv: BinaryView):
        self.bv: BinaryView = bv
        self.driver = GraphDatabase.driver(Configuration.neo4j_uri, auth=(Configuration.neo4j_username,
                                                                          Configuration.neo4j_password))
        self.function_collection_uuid: int = self.calc_bv_uuid()

        # Load up all attribute plugins for all plugins
        for ir in bd_enums.IRType:
            self.loaded_attributes.update(PluginManager.import_attributes(ir))

    def calc_bv_uuid(self) -> int:
        file_hash = xxhash.xxh32()
        file_hash.update(self.bv.read(0, self.bv.end))
        return file_hash.intdigest()

    @staticmethod
    def exists_in_db(uuid: int, node_label: str, session: Session) -> bool:
        """
        Check if node with the given uuid exists in the DB, return True or False accordingly.
        """

        cypher_str = 'MATCH (n:' + node_label + ' {uuid: "' + str(uuid) + '"}) ' \
                     'RETURN COUNT(n) as exists'
        log.log_info(f'exists_in_db: cypher string is {cypher_str}')
        result: StatementResult = session.run(cypher_str)
        log.log_info(f'exists_in_db: UUID {str(uuid)} with label {node_label} found in DB {result.peek()["exists"]} times.')
        if result.single()['exists']:
            return True
        else:
            return False

    def populate_x86_assembly(self):
        # Start by creating a function collection, representing the file\binary view that contains all the functions
        with self.driver.session() as session:
            if not self.exists_in_db(self.function_collection_uuid, 'FunctionCollection', session):
                # The function collection doesn't yet exist in the DB, continue with population
                session.run('CREATE (:FunctionCollection {uuid: ' + str(self.function_collection_uuid) + '}) ')

            for func in self.bv.functions:
                func: Function
                log.log_info(f'populate_x86_assembly: Function uuid {BDFunction.generate_uuid(func)}')
                if not self.exists_in_db(BDFunction.generate_uuid(func), 'Function', session):
                    bd_func: BDFunction = self.populate_assembly_function(func)

                    if bd_func and self.insert_func_into_db(bd_func):
                        log.log_info(f'populate_x86_assembly: Successfully inserted function {bd_func.uuid} into DB.')
                    else:
                        log.log_info(f'populate_x86_assembly: Failed to insert function {func.name}.')

    def populate_assembly_function(self, func: Function) -> Optional[BDFunction]:
        """
        Create a BDFunction object and populate it with all available attributes.
        """
        if len(list(func.instructions)) >= Configuration.MIN_FUNCTION_INSTRUCTION_LENGTH:
            bd_func = BDFunction(func)
            for attribute in self.loaded_attributes:
                attribute: Attribute
                if attribute.attribute_target == bd_func.bd_obj_type and attribute.IR == bd_func.bd_obj_IR:
                    # Populate the attribute values
                    if self.loaded_attributes['FunctionHash'].extract_attribute(bd_func):
                        pass
                    else:
                        log.log_info(f'Failed to extracts attribute {attribute.name} from function {bd_func}')
            if self.populate_assembly_basic_block(bd_func):
                return bd_func
            else:
                log.log_info(f'Failed to populate basic block attributes for function {bd_func}')
                return None
        else:
            log.log_info(f'Function {func.name} is too small for matching.')
            return None

    def populate_assembly_basic_block(self, bd_func: BDFunction) -> bool:
        """
        Create all Basic Block objects and populate them with all attributes.
        """
        # Create all BDBasicBlock objects for the given function.
        bd_func.populate_basic_blocks()

        with self.driver.session() as session:
            for bb_uuid, bd_basic_block in bd_func.bd_basic_blocks.items():
                bd_basic_block: BDBasicBlock
                log.log_info(f'populate_assembly_basic_block: Checking bb uuid {bb_uuid}')
                if not self.exists_in_db(bb_uuid, 'BasicBlock', session):
                    if bd_basic_block.underlying_obj.instruction_count >= Configuration.MIN_FUNCTION_INSTRUCTION_LENGTH:
                        for attribute in self.loaded_attributes:
                            attribute: Attribute
                            if attribute.attribute_target == bd_basic_block.bd_obj_type \
                                    and attribute.IR == bd_basic_block.bd_obj_IR:
                                # Populate the attribute values
                                if self.loaded_attributes['FunctionHash'].extract_attribute(bd_basic_block):
                                    pass
                                else:
                                    log.log_info(f'Failed to extracts attribute {attribute.name} from '
                                                 f'basic block {bd_basic_block}')
                                    return False
        return True

    def insert_func_into_db(self, bd_func: BDFunction) -> bool:
        """
        Insert a BDFunction into the DB, including all its BDBasicBlock object and associated attributes.
        """

        log.log_info(f'insert_func_into_db: Function uuid {bd_func.uuid}')
        with self.driver.session() as session:
            # Create the function node
            session.run('CALL apoc.create.nodes(["Function"], [{uuid: {uuid}}])',
                        uuid=str(bd_func.uuid))

            # Create the basic block nodes
            uuid_list: List = list()
            for bb_uuid in bd_func.bd_basic_blocks:
                uuid_list.append({'uuid': str(bb_uuid)})
            cypher_str = 'WITH {uuid_list} as ul ' \
                         'CALL apoc.create.nodes(["BasicBlock"], ul) yield node ' \
                         'RETURN COUNT(node.uuid) as exists'
            result = session.run(cypher_str, uuid_list=uuid_list)

            log.log_info(f'insert_func_into_db: Number of created BasicBlocks - {result.peek()["exists"]}.')
            if result.single()['exists']:
                return True
            else:
                return False
