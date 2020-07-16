from typing import *

import xxhash
from binaryninja import *
from neo4j import GraphDatabase, StatementResult, Session, Transaction

from . import PluginManager
from .. import Configuration
from ..Abstracts.Attribute import Attribute
from ..Enums import bd_enums
from ..Operands.Assembly.BDBasicBlock import BDBasicBlock
from ..Operands.Assembly.BDFunction import BDFunction

"""
                    IMPORTANT INFORMATION - RULES FOR CREATING ATTRIBUTES
    Neo4j enforces the following limitations on nodes and relationships:
        
        1. Only primitive types or arrays of primitive types are supported as properties (int, str, dict, list)
        2. NO NESTING of types supported
        3. lists must be homogeneous (same type for all list objects, no type mixing)
          
"""


class DBManager:
    """
    Responsible for populating a Neo4j graph with all the attributes of the functions it receives from BinaryNinja.
    The default DBManager will only populate Assembly form of the function, but other IR forms (LLIL, MLIL, HLIL etc)
    will be possible in the future.
    """
    loaded_attributes: Dict[str, Attribute] = dict()

    def __init__(self, bv: BinaryView):
        self.bv: BinaryView = bv
        self.driver = GraphDatabase.driver(Configuration.neo4j_uri, auth=(Configuration.neo4j_username,
                                                                          Configuration.neo4j_password))
        self.function_collection_uuid: int = self.calc_bv_uuid()

        # Load up all attribute plugins for all plugins
        for ir in bd_enums.IRType:
            self.loaded_attributes.update(PluginManager.import_attributes(ir))

    def calc_bv_uuid(self) -> int:
        # BV UUID is the hash of all the bytes in the file.
        file_hash = xxhash.xxh32()
        file_hash.update(self.bv.read(0, self.bv.end))
        return file_hash.intdigest()

    @staticmethod
    def exists_in_db(uuid: int, node_label: str, session: Session) -> bool:
        """
        Check if node with the given uuid exists in the DB, return True or False accordingly.
        """

        cypher_str = f'MATCH (n:{node_label} {{uuid: {uuid}}}) ' \
                     'RETURN n.uuid as uuid'
        result: StatementResult = session.run(cypher_str)
        if result.single():
            return True
        else:
            return False

    def populate_assembly_function_collection(self):
        # Start by creating a function collection, representing the file\binary view that contains all the functions
        with self.driver.session() as session:
            if not self.exists_in_db(self.function_collection_uuid, 'FunctionCollection', session):
                # The function collection doesn't yet exist in the DB, continue with population
                session.run(f'CREATE (:FunctionCollection {{'
                            f'uuid: {self.function_collection_uuid}, '
                            f'filename: "{self.bv.file.filename.split("/")[-1]}",'
                            f'arch: "{str(self.bv.arch.name)}" '
                            f'}})')

            for func in self.bv.functions:
                func: Function
                log.log_info(f'populate_assembly_function_collection: Function uuid {BDFunction.generate_uuid(func)}')
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
        bd_func = BDFunction(func)
        for attribute_name, attribute in self.loaded_attributes.items():
            attribute: Attribute
            attribute_name: str
            if attribute.dependencies:
                # Make sure to load the dependencies before the attribute itself.
                for depend_attr_name in attribute.dependencies:
                    # TODO: Handle a case where a dependency has a dependency of its own
                    depend_attr: Attribute = self.loaded_attributes[depend_attr_name]
                    if depend_attr.extract_attribute(bd_func):
                        pass
                    else:
                        log.log_info(f'Failed to extract dependant attribute {depend_attr_name} from function '
                                     f'{bd_func}')
            if attribute.attribute_target == bd_func.bd_obj_type and attribute.IR == bd_func.bd_obj_IR:
                # Populate the attribute values. extract_attribute takes care of storing the attribute value
                # inside the bd_func object.
                if attribute.extract_attribute(bd_func):
                    pass
                else:
                    log.log_info(f'Failed to extract attribute {attribute.name} from function {bd_func}')
        if self.populate_assembly_basic_block(bd_func):
            # If populate_assembly_basic_block is successfull, then all basic blocks and instructions were
            # added to the bd_func object and their attribute values were added to the respective objects.
            return bd_func
        else:
            log.log_info(f'Failed to populate basic block attributes for function {bd_func}')
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
                log.log_info(f'Checking bb uuid {bb_uuid}')
                if not self.exists_in_db(bb_uuid, 'BasicBlock', session):
                    for attribute_name, attribute in self.loaded_attributes.items():
                        attribute: Attribute
                        if attribute.attribute_target == bd_basic_block.bd_obj_type \
                                and attribute.IR == bd_basic_block.bd_obj_IR:
                            # Populate the attribute values
                            if attribute.extract_attribute(bd_basic_block):
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

        # Create the attribute dictionary to insert into the DB
        func_attributes = bd_func.get_all_attribute_values()

        log.log_info(f'Inserting Function uuid {bd_func.uuid} into DB...')
        with self.driver.session() as session:
            # Create the function node
            result = session.run('CALL apoc.create.nodes(["Function"], [{uuid: {uuid}}]) yield node '
                                 'RETURN node',
                                 uuid=bd_func.uuid)
            if result.single()['node']:
                if session.write_transaction(self.link_attribute, bd_func.uuid, func_attributes):
                    log.log_debug(f'Successfully linked all attribute for Function with uuid: {bd_func.uuid}')
                    for bb_uuid, bd_bb_obj in bd_func.bd_basic_blocks.items():
                        if self.insert_bb_into_db(bd_bb_obj):
                            continue
                        else:
                            log_debug(f'Failed to insert bb with uuid {bb_uuid} into the DB.')
                    log.log_debug(f'Successfully linked all attributes for all basic blocks inside function with'
                                  f'uuid {bd_func.uuid}')
                    return True
                else:
                    log.log_debug(f'Failed to link all attributes for function with uuid: {bd_func.uuid}')
            else:
                log.log_debug(f'Unable to create a Function node for uuid: {str(bd_func.uuid)}')
        return False

    def insert_bb_into_db(self, bd_basic_block: BDBasicBlock) -> bool:
        """
        Insert a BDBasicBlock into the DB, including all its Instruction object and associated attributes.
        """
        # Create the attribute dictionary to insert into the DB
        bb_attributes = bd_basic_block.get_all_attribute_values()

        log.log_info(f'Inserting Basic Block uuid {bd_basic_block.uuid} into DB...')
        with self.driver.session() as session:
            # Create the basic block node
            result = session.run('CALL apoc.create.nodes(["BasicBlock"], [{uuid: {uuid}}]) yield node '
                                 'RETURN node',
                                 uuid=bd_basic_block.uuid)
            if result.single()['node']:
                if session.write_transaction(self.link_attribute, bd_basic_block.uuid, bb_attributes):
                    log.log_debug(f'Successfully linked all attribute for Basic block with uuid: {bd_basic_block.uuid}')

                    # TODO: add insertion of BDInstruction here
                    return True
                else:
                    log.log_debug(f'Failed to link all attributes for basic block with uuid: {bd_basic_block.uuid}')
            else:
                log.log_debug(f'Unable to create a BasicBlock node for uuid: {str(bd_basic_block.uuid)}')
        return False

    @staticmethod
    def link_attribute(tx: Transaction,
                       origin_uuid: int,
                       attributes: Dict
                       ) -> bool:
        """
        After creating a node describing the current BDObject (e.g BDFunction, BDBasicBlock, BDInstruction etc)
        we link the node to the various attributes describing it.
        :param tx: a neo4j tx Transaction object used to communicate with DB.
        :param origin_uuid: uuid of the node describing the current BDObject.
        :param attributes: a dict containing attributes in the form of {attr_name: attr_features}
        :return: success or failure (if one attr fails to link, the function fails)
        """

        for attr_name, attr_features in attributes.items():
            attr_name: str
            attr_features: dict

            # ident_features is used to identify an existing attribute node in order to speed up the merge process
            attribute_uuid = attr_features.pop('uuid', None)

            if attribute_uuid:
                ident_features = {'uuid': attribute_uuid}
            else:
                ident_features = attr_features

            cypher_statement = f'CALL apoc.merge.node({{attr_name}}, ' \
                               f'{{ident_features}}, ' \
                               f'{{attr_features}} ' \
                               f') ' \
                               f'yield node '
            cypher_statement += f'MATCH (origin {{uuid: $origin_uuid}}) '
            cypher_statement += f'CREATE (origin)-[r:Attribute]->(node) ' \
                                f'RETURN r'

            r = tx.run(cypher_statement, attr_name=[attr_name], attr_features=attr_features,
                       ident_features=ident_features, origin_uuid=origin_uuid).single()

            if r:
                continue
            else:
                log.log_debug(f'Failed to link attribute {attr_name} to node with uuid {origin_uuid}')
                return False

        log.log_debug(f'successfully linked all attributes to node with uuid {origin_uuid}')
        return True
