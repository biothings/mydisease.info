#!/usr/bin/env python

import os
from functools import partial

import biothings.hub.databuild.builder as builder
from biothings.hub import HubServer
from biothings.hub.databuild.syncer import (
    SyncerManager,
    ThrottledESJsonDiffSelfContainedSyncer,
    ThrottledESJsonDiffSyncer,
)
from biothings.utils.version import set_versions

import config
import plugins
from hub.databuild.builder import CanonicalDataBuilder
from hub.databuild.mapper import CanonicalIDMapper

app_folder, _src = os.path.split(os.path.split(
    os.path.split(os.path.abspath(__file__))[0])[0])
del _src

set_versions(config, app_folder)


class MyCanonicalHubServer(HubServer):

    def configure_build_manager(self):
        # Instantiate the canonical mapper
        canonical_mapper = CanonicalIDMapper(name="canonical")
        # Create a custom builder that includes the canonical mapper
        pbuilder = partial(CanonicalDataBuilder, mappers=[canonical_mapper])
        build_manager = builder.BuilderManager(
            job_manager=self.managers["job_manager"],
            builder_class=pbuilder,
            poll_schedule="* * * * * */10"
        )
        build_manager.configure()
        build_manager.poll()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s", CanonicalDataBuilder)

    def configure_sync_manager(self):
        # Production sync manager with throttled syncers.
        sync_manager_prod = SyncerManager(
            job_manager=self.managers["job_manager"])
        sync_manager_prod.configure(klasses=[
            partial(ThrottledESJsonDiffSyncer, config.MAX_SYNC_WORKERS),
            partial(ThrottledESJsonDiffSelfContainedSyncer,
                    config.MAX_SYNC_WORKERS)
        ])
        self.managers["sync_manager"] = sync_manager_prod

        # Test sync manager (typically for localhost ES)
        sync_manager_test = SyncerManager(
            job_manager=self.managers["job_manager"])
        sync_manager_test.configure()
        self.managers["sync_manager_test"] = sync_manager_test
        self.logger.info("Using custom syncer, prod(throttled): %s, test: %s",
                         sync_manager_prod, sync_manager_test)


# Pass explicit list of datasources
server = MyCanonicalHubServer(plugins.__sources__, name=config.HUB_NAME)

if __name__ == "__main__":
    server.start()
