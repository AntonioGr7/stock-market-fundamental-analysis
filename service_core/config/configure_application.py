from service_core.containers.containers import Application
import importlib
from service_core.config.load_env_config import load_yamlenv


def configure_application(config_path='../settings/config.yaml',additional_modules=[]):
    load_yamlenv(config_path)
    modules = import_default_modules() + import_additional_modules(additional_modules)
    application = Application()
    application.config.from_yaml(config_path)
    application.init_resources()
    application.wire(modules=modules)
    return application

def import_default_modules():
    return [
        importlib.import_module("service_core.config.log_configuration"),
        importlib.import_module("service_core.server.server"),
        importlib.import_module("service_core.server.security")
    ]


def import_additional_modules(paths):
    modules_to_import = []
    for path in paths:
        modules_to_import.append(importlib.import_module(path))
    return modules_to_import
