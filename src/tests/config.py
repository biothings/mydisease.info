"""
    Config file to run tests for MyDisease.info
"""
import importlib.util as _imp_util
import os
from os.path import pardir

CONFIG_FILE_NAME = "config_web.py"

cfg_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), pardir, CONFIG_FILE_NAME))

# Check if the configuration file exists.
if not os.path.exists(cfg_path):
    raise Exception(f"No config file {CONFIG_FILE_NAME} found at {cfg_path}")

# Load the configuration module from the specified path.
spec = _imp_util.spec_from_file_location("config", cfg_path)
config = _imp_util.module_from_spec(spec)
spec.loader.exec_module(config)

# put the config variables into the module namespace
for _k, _v in config.__dict__.items():
    if not _k.startswith('_'):
        globals()[_k] = _v

# cleanup
del CONFIG_FILE_NAME

# override default
ES_HOST = 'http://localhost:9200'
#ES_INDEX = 'mydisease_test'
ES_INDICES = dict(disease='mydisease_test')
