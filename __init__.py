import time
from binaryninja import *
from .FlowManagement.DiffManager import AssemblyFunctionDiffManager
from .FlowManagement.DBManager import DBManager
from .Operands.Assembly import BDFunction
from . import Configuration
from typing import Optional
from .Operands.Assembly.BDFunction import BDFunction, BDFunctionSet





def run_diff(bv: BinaryView):
    log.log_info(f'Starting Diffing Process.')
    BinJdiff(bv).start()


class BinJdiff(BackgroundTaskThread):

    def __init__(self, bv: BinaryView):
        super().__init__("", True)
        self.bv = bv

    def run(self):
        self.binjdiff()

    def binjdiff(self):
        start_time = time.time()
        self.bv.update_analysis_and_wait()

        db_mgr = DBManager(self.bv)
        db_mgr.populate_x86_assembly()

        end_time = time.time()
        log.log_info(f"Operation done in {end_time - start_time} seconds")


log.log_to_file(0, Configuration.debug_file_path)
PluginCommand.register("NinjDiff", "BinDiff implementation", run_diff)
