import os
import json
import logging

import synapse.common as s_common
import synapse.cortex as s_cortex
import synapse.lib.httpapi as s_httpapi
import synapse.tests.utils as s_test
import synapse.tools.genpkg as s_genpkg


logger = logging.getLogger(__name__)

dirname = os.path.dirname(__file__)
pkgproto = s_common.genpath(dirname, "synapse-webhook.yaml")


class DiscordApiMock(s_httpapi.Handler):
    counter = 0

    async def head(self):
        raise NotImplementedError

    async def get(self):
        raise NotImplementedError

    async def post(self):
        if self.request.body:
            d = json.loads(self.request.body.decode())
            print(d)
            c = d.get("content")
            if c is not None:
                if "defang" in c:
                    c: str
                    if not (c.count("hxxp") > 2 and c.count("[.]") > 2):
                        raise ValueError("not properly defanged")
                
                DiscordApiMock.counter += 1
                return

        raise ValueError("bad discord webhook")

class SynapseWebhookTest(s_test.SynTest):
    async def _t_install_pkg(self, core: s_cortex.Cortex):
        """Install and configure the Storm package."""

        await s_genpkg.main((pkgproto, "--push", f"cell://{core.dirn}"))

    async def test_add(self):
        async with self.getTestCore() as core:
            await self._t_install_pkg(core)

            self.stormIsInPrint("Webhook added for service \"discord\"", await core.stormlist(f"zw.webhook.add asdf1 https://discord.com/api/webhooks/1111223423432/asdflkjsadlfkjadslfjlkfdsa-lkjczlknvznnmvxzc-oireoiwqrwoiuqroiweiuqorq"))
            self.stormIsInPrint("Webhook added for service \"slack\"", await core.stormlist(f"zw.webhook.add asdf2 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist(f"zw.webhook.add asdf3 https://asdfsafda.webhook.office.com/asdfasdfsafdsa/zxcvxzvxzvcxv/gdgfdsgfdsgfdg"))
            self.stormIsInErr("Failed to detect webhook service", await core.stormlist(f"zw.webhook.add asdf3 https://reddit.com"))
            self.stormIsInErr("Invalid service specified: zzz", await core.stormlist(f"zw.webhook.add --service zzz asdf4 https://reddit.com"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist(f"zw.webhook.add --service teams asdf4 https://reddit.com"))
            self.stormIsInErr("A webhook already exists", await core.stormlist(f"zw.webhook.add --service teams asdf4 https://reddit.com"))

    async def test_call(self):
        async with self.getTestCore() as core:
            await self._t_install_pkg(core)

            _, port = await core.addHttpsPort(0)
            root = await core.auth.getUserByName('root')
            await root.setPasswd('root')

            core.addHttpApi("/discord", DiscordApiMock, {"cell": core})

            await core.callStorm(f"zw.webhook.add --service discord d1 https://root:root@127.0.0.1:{port}/discord")
            await core.callStorm(f"zw.webhook.add --service slack s1 https://root:root@127.0.0.1:{port}/slack")
            await core.callStorm(f"zw.webhook.add --service teams t1 https://root:root@127.0.0.1:{port}/teams")

            # await core.callStorm(f"$lib.inet.http.post('https://root:root@127.0.0.1:{port}/discord', ssl_verify=$lib.false)")
            await core.callStorm(f"zw.webhook.send --no-verify d1 hello")
            self.eq(DiscordApiMock.counter, 1)

            await core.callStorm(f"[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify --defang d1 `defang {{$node.value()}}`")
            await core.callStorm(f"zw.webhook.send --no-verify d1 hi")
            self.eq(DiscordApiMock.counter, 3)