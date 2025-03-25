#!/usr/bin/env python
import os
from functools import partial

import biothings
from biothings.hub import HubServer

# Import the DataBuilder and your new mapper
from biothings.hub.databuild.builder import DataBuilder
from biothings.utils.version import set_versions

import config
import hub.dataload.sources
from hub.databuild.mapper import (
    CanonicalIDMapper,  # ensure this file includes your mapper
)

app_folder, _src = os.path.split(os.path.split(
    os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config, app_folder)

# Create an instance of the CanonicalIDMapper
canonical_mapper = CanonicalIDMapper(name="canonical_id")

# Create a custom DataBuilder that includes your mapper.
# If you already have other mappers, combine them into the list.
CustomDataBuilder = partial(DataBuilder, mappers=[canonical_mapper])

# Pass the custom builder class into HubServer
server = HubServer(hub.dataload.sources, name=config.HUB_NAME,
                   builder_class=CustomDataBuilder)

if __name__ == "__main__":
    logging = config.logger
    logging.info("Hub DB backend: %s", biothings.config.HUB_DB_BACKEND)
    logging.info("Hub database: %s", biothings.config.DATA_HUB_DB_DATABASE)
    server.start()
