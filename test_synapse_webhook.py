import os
import logging

import synapse.common as s_common
import synapse.cortex as s_cortex
import synapse.tests.utils as s_test
import synapse.tools.genpkg as s_genpkg


logger = logging.getLogger(__name__)

dirname = os.path.dirname(__file__)
pkgproto = s_common.genpath(dirname, "synapse-webhook.yaml")


class SynapseWebhookTest(s_test.SynTest):
    async def _t_install_pkg(self, core: s_cortex.Cortex):
        """Install and configure the Storm package."""

        await s_genpkg.main((pkgproto, "--push", f"cell://{core.dirn}"))

    async def test_lookups(self):

        async with self.getTestCore() as core:
            await self._t_install_pkg(core)
            await self._t_seed_cortex(core)

            await self._t_check_lookup_type(core, "domain_soa", ["class.listed", "expose.vendor", "has_operator", "sinkhole", "type.domain_soa"])
            await self._t_check_lookup_type(core, "ipv4", ["class.listed", "expose.vendor", "has_operator", "sinkhole", "type.ipv4"])
            await self._t_check_lookup_type(core, "ipv4_range", ["class.listed", "sinkhole", "type.ipv4_range"])
            await self._t_check_lookup_type(core, "nameserver", ["class.query_only", "has_operator", "sinkhole", "type.nameserver"])
            await self._t_check_lookup_type(core, "whois_email", ["class.listed", "has_operator", "sinkhole", "type.domain_soa", "type.whois_email"])

            msgs = await core.stormlist("[it:dev:str=asdf] | zw.sinkdb.lookup --debug")
            self.stormIsInWarn("unsupported form received", msgs)