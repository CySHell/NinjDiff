from .. import Configuration
import pkgutil, importlib
from ..Abstracts import Attribute, Selector, Property
from typing import Dict
from binaryninja import *
from ..Enums import bd_enums


def import_attributes(target_ir: bd_enums.IRType):
    loaded_attributes: Dict[str, Attribute] = dict()
    for module in pkgutil.iter_modules(path=Configuration.default_attributes_path):
        module_name = module.name
        attribute_module = importlib.import_module('.' + module_name,
                                                   package='NinjDiff.Operation.Attributes.' + target_ir.value)
        attribute_class_obj: Attribute = getattr(attribute_module, module_name)
        loaded_attributes.update({module_name: attribute_class_obj})

    log.log_debug(f'Loaded the following Attribute plugins: \n {loaded_attributes}')

    return loaded_attributes


def import_properties(target_ir: bd_enums.IRType):
    loaded_properties: Dict[str, Property] = dict()
    for module in pkgutil.iter_modules(path=Configuration.default_property_path):
        module_name = module.name
        property_module = importlib.import_module('.' + module_name,
                                                 package='NinjDiff.Operation.Properties.' + target_ir.value)
        property_class_obj: Property = getattr(property_module, module_name)
        loaded_properties.update({module_name: property_class_obj})

    log.log_debug(f'Loaded the following Property plugins: \n {loaded_properties}')

    return loaded_properties


def import_selectors(target_ir: bd_enums.IRType):
    loaded_selectors: Dict[str, Selector] = dict()
    for module in pkgutil.iter_modules(path=Configuration.default_selector_path):
        module_name = module.name
        selector_module = importlib.import_module('.' + module_name,
                                                  package='NinjDiff.Operation.Selectors.' + target_ir.value)
        selector_class_obj: Selector = getattr(selector_module, module_name)
        loaded_selectors.update({module_name: selector_class_obj})

    log.log_debug(f'Loaded the following Selector plugins: \n {loaded_selectors}')

    return loaded_selectors
