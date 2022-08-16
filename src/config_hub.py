# ######### #
# HUB VARS  #
# ######### #

# Refer to biothings.hub.default_config for all configurable settings

# Pre-prod/test ES definitions
INDEX_CONFIG = {
    #"build_config_key" : None, # used to select proper idxr/syncer
    "indexer_select": {
        # default
        #None : "path.to.special.Indexer",
    },
    "env": {
        "test": {
            "host": "localhost:9200",
            "indexer": {
                "args": {
                    "timeout": 300,
                    "retry_on_timeout": True,
                    "max_retries": 10
                }
            },
            "index": []
        }
    }
}

# Snapshot environment configuration
SNAPSHOT_CONFIG = {}
RELEASE_CONFIG = {}

# Hub name/icon url/version, for display purpose
HUB_NAME = "MyDisease.info API (backend)"
HUB_ICON = "https://biothings.io/static/img/mydisease-logo-shiny.svg"
HUB_VERSION = "master"

TORNADO_SETTINGS = {
    # max 10GiB upload
    "max_buffer_size" : 10*1024*1024*1024,
}

STANDALONE_VERSION = {"branch": "standalone_v3"}

# List of versions.json URLs, Hub will handle these as sources for data releases
VERSION_URLS = []

RELEASE_KEEP_N_RECENT_INDICES = 1

########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The other hub-specific senstive variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_hub import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#
