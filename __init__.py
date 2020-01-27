import time
from binaryninja import *
from .FlowManagement.DiffManager import AssemblyFunctionDiffManager
from .Operands.Assembly import BDFunction
from . import Configuration
from typing import Optional
from .Operands.Assembly.BDFunction import BDFunction, BDFunctionSet


def load_bv(path: str, view_type: str) -> Optional[BinaryView]:
    target_bv: BinaryView = BinaryViewType[view_type].open(path)
    target_bv.update_analysis_and_wait()

    if target_bv:
        log.log_debug(f'Successfully loaded BinaryView {target_bv}')
        return target_bv
    else:
        log.log_debug(f'Failed to load BinaryView {path}')
        return None


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

        # TODO: Target bv should be an input from the user.
        target_bv = load_bv('C:\\Users\\' + Configuration.current_user + '\\Downloads\\7z1604-x64.exe', 'PE')

        source = BDFunctionSet()
        target = BDFunctionSet()
        for source_func in self.bv.functions:
            if len(list(source_func.instructions)) >= Configuration.MIN_FUNCTION_LENGTH:
                bd_func = BDFunction(source_func)
                source.add(bd_func)
        for target_func in target_bv.functions:
            if len(list(target_func.instructions)) >= Configuration.MIN_FUNCTION_LENGTH:
                bd_func = BDFunction(target_func)
                target.add(bd_func)
        diff_manager = AssemblyFunctionDiffManager(source, target)
        diff_manager.diff_functions()
        end_time = time.time()
        log.log_info(f"Operation done in {end_time - start_time} seconds")


log.log_to_file(0, Configuration.debug_file_path)
PluginCommand.register("NinjDiff", "BinDiff implementation", run_diff)
