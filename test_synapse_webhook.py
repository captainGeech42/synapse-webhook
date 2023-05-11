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

def check_defang(mesg: str):
    """Raise an exception if a message that should be defanged isn't properly defanged."""

    if "defang" in mesg:
        if not (
            mesg.count("hxxp") > 0 and
            mesg.count("[.]") > 0 and
            mesg.count("http") == 0
        ):
            raise ValueError("not properly defanged")

class DiscordApiMock(s_httpapi.Handler):
    """Mock implementation of a Discord webhook server."""

    counter = 0

    async def head(self):
        raise NotImplementedError

    async def get(self):
        raise NotImplementedError

    async def post(self):
        if self.request.body:
            d = json.loads(self.request.body.decode())
            m = d.get("content")
            if m is not None:
                check_defang(m)
                
                DiscordApiMock.counter += 1
                self.set_status(200)
                return

        raise ValueError("bad discord webhook")

class SlackApiMock(s_httpapi.Handler):
    """Mock implementation of a Slack webhook server."""

    counter = 0

    async def head(self):
        raise NotImplementedError

    async def get(self):
        raise NotImplementedError

    async def post(self):
        if self.request.body:
            d = json.loads(self.request.body.decode())
            m = d.get("text")
            if m is not None:
                check_defang(m)
                
                SlackApiMock.counter += 1
                self.set_status(200)
                return

        raise ValueError("bad slack webhook")

class TeamsApiMock(s_httpapi.Handler):
    """Mock implementation of a Teams webhook server."""

    counter = 0

    async def head(self):
        raise NotImplementedError

    async def get(self):
        raise NotImplementedError

    async def post(self):
        if self.request.body:
            d = json.loads(self.request.body.decode())
            m = d.get("text")
            if m is not None:
                check_defang(m)
                
                TeamsApiMock.counter += 1
                self.set_status(200)
                return

        raise ValueError("bad teams webhook")
    
class KeybaseApiMock(s_httpapi.Handler):
    """Mock implementation of a Keybase webhook server."""

    counter = 0

    async def head(self):
        raise NotImplementedError

    async def get(self):
        raise NotImplementedError

    async def post(self):
        if self.request.body:
            d = json.loads(self.request.body.decode())
            m = d.get("msg")
            if m is not None:
                check_defang(m)
                
                KeybaseApiMock.counter += 1
                self.set_status(200)
                return

        raise ValueError("bad keybase webhook")

class SynapseWebhookTest(s_test.SynTest):
    async def _t_install_pkg(self, core: s_cortex.Cortex, prox: s_cortex.CoreApi | None = None):
        """Install and configure the Storm package."""

        await s_genpkg.main((pkgproto, "--push", f"cell://{core.dirn}"))

        if prox is not None:
            nopriv = await prox.addUser("nopriv")
            self.assertIsNotNone(nopriv)
            await prox.addUserRule(nopriv["iden"], (True, ("zw", "webhook", "user")))
            
            hipriv = await prox.addUser("hipriv")
            self.assertIsNotNone(hipriv)
            await prox.addUserRule(hipriv["iden"], (True, ("zw", "webhook", "user")))
            await prox.addUserRule(hipriv["iden"], (True, ("zw", "webhook", "admin")))

    async def test_add(self):
        async with self.getTestCore() as core:
            await self._t_install_pkg(core)

            self.stormIsInPrint("Webhook added for service \"discord\"", await core.stormlist("zw.webhook.add asdf1 https://discord.com/api/webhooks/1111223423432/asdflkjsadlfkjadslfjlkfdsa-lkjczlknvznnmvxzc-oireoiwqrwoiuqroiweiuqorq"))
            self.stormIsInPrint("Webhook added for service \"slack\"", await core.stormlist("zw.webhook.add asdf2 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist("zw.webhook.add asdf3 https://asdfsafda.webhook.office.com/asdfasdfsafdsa/zxcvxzvxzvcxv/gdgfdsgfdsgfdg"))
            self.stormIsInPrint("Webhook added for service \"keybase\"", await core.stormlist("zw.webhook.add asdf4 https://bots.keybase.io/webhookbot/asdasdasdasda_asdasdasdasda"))
            self.stormIsInErr("Failed to detect webhook service", await core.stormlist("zw.webhook.add asdf3 https://reddit.com"))
            self.stormIsInErr("Invalid service specified: zzz", await core.stormlist("zw.webhook.add --service zzz asdf5 https://reddit.com"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist("zw.webhook.add --service teams asdf5 https://reddit.com"))
            self.stormIsInErr("A webhook already exists", await core.stormlist("zw.webhook.add --service teams asdf5 https://reddit.com"))

    async def test_call(self):
        async with self.getTestCoreAndProxy() as (core, prox):
            await self._t_install_pkg(core, prox)

            _, port = await core.addHttpsPort(0)

            root = await core.auth.getUserByName("root")
            await root.setPasswd("root")

            core.addHttpApi("/discord", DiscordApiMock, {"cell": core})
            core.addHttpApi("/slack", SlackApiMock, {"cell": core})
            core.addHttpApi("/teams", TeamsApiMock, {"cell": core})
            core.addHttpApi("/keybase", KeybaseApiMock, {"cell": core})

            await core.callStorm(f"zw.webhook.add --service discord d1 https://root:root@127.0.0.1:{port}/discord")
            await core.callStorm(f"zw.webhook.add --service slack --global s1 https://root:root@127.0.0.1:{port}/slack")
            await core.callStorm(f"zw.webhook.add --service teams t1 https://root:root@127.0.0.1:{port}/teams")
            await core.callStorm(f"zw.webhook.add --service keybase k1 https://root:root@127.0.0.1:{port}/keybase")

            self.stormHasNoWarnErr(await core.stormlist("zw.webhook.send --no-verify d1 hello"))
            self.eq(DiscordApiMock.counter, 1)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify d1 `{$node.value()}`"))
            self.eq(DiscordApiMock.counter, 3)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify --defang d1 `defang {$node.value()}`"))
            self.eq(DiscordApiMock.counter, 5)

            self.stormHasNoWarnErr(await core.stormlist("zw.webhook.send --no-verify s1 hello"))
            self.eq(SlackApiMock.counter, 1)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify s1 `{$node.value()}`"))
            self.eq(SlackApiMock.counter, 3)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify --defang s1 `defang {$node.value()}`"))
            self.eq(SlackApiMock.counter, 5)

            self.stormHasNoWarnErr(await core.stormlist("zw.webhook.send --no-verify t1 hello"))
            self.eq(TeamsApiMock.counter, 1)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify t1 `{$node.value()}`"))
            self.eq(TeamsApiMock.counter, 3)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify --defang t1 `defang {$node.value()}`"))
            self.eq(TeamsApiMock.counter, 5)

            self.stormHasNoWarnErr(await core.stormlist("zw.webhook.send --no-verify k1 hello"))
            self.eq(KeybaseApiMock.counter, 1)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify k1 `{$node.value()}`"))
            self.eq(KeybaseApiMock.counter, 3)
            self.stormHasNoWarnErr(await core.stormlist("[inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --no-verify --defang k1 `defang {$node.value()}`"))
            self.eq(KeybaseApiMock.counter, 5)

            async with core.getLocalProxy(user="nopriv") as noprivcore:
                self.stormIsInErr("Not authorized to use", [m async for m in noprivcore.storm("zw.webhook.send --no-verify d1 yeet")])
                self.stormHasNoWarnErr([m async for m in noprivcore.storm("zw.webhook.send --no-verify s1 yeet")])

            async with core.getLocalProxy(user="hipriv") as hiprivcore:
                self.stormIsInErr("Not authorized to use", [m async for m in hiprivcore.storm("zw.webhook.send --no-verify d1 yeet")])
                self.stormHasNoWarnErr([m async for m in hiprivcore.storm("zw.webhook.send --no-verify s1 yeet")])

    async def test_list(self):
        async with self.getTestCoreAndProxy() as (core, prox):
            await self._t_install_pkg(core, prox)

            self.stormIsInPrint("Webhook added for service \"discord\"", await core.stormlist("zw.webhook.add asdf1 https://discord.com/api/webhooks/1111223423432/asdflkjsadlfkjadslfjlkfdsa-lkjczlknvznnmvxzc-oireoiwqrwoiuqroiweiuqorq"))
            self.stormIsInPrint("Webhook added for service \"slack\"", await core.stormlist("zw.webhook.add asdf2 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist("zw.webhook.add asdf3 https://asdfsafda.webhook.office.com/asdfasdfsafdsa/zxcvxzvxzvcxv/gdgfdsgfdsgfdg"))
            self.stormIsInPrint("Webhook added for service \"keybase\"", await core.stormlist("zw.webhook.add asdf4 https://bots.keybase.io/webhookbot/asdasdasdasda_asdasdasdasda"))

            mesgs = await core.stormlist("zw.webhook.list")
            self.stormHasNoWarnErr(mesgs)
            self.stormIsInPrint("Webhook: asdf1", mesgs)
            self.stormIsInPrint("Webhook: asdf2", mesgs)
            self.stormIsInPrint("Webhook: asdf3", mesgs)
            self.stormIsInPrint("Webhook: asdf4", mesgs)
            
            async with core.getLocalProxy(user="nopriv") as noprivcore:
                self.stormIsInErr("Not allowed to list", [m async for m in noprivcore.storm("zw.webhook.list --all")])
            
            async with core.getLocalProxy(user="hipriv") as hiprivcore:
                self.stormHasNoWarnErr([m async for m in hiprivcore.storm("zw.webhook.list --all")])
    
    async def test_delete(self):
        async with self.getTestCoreAndProxy() as (core, prox):
            await self._t_install_pkg(core, prox)

            self.stormIsInPrint("Webhook added for service \"discord\"", await core.stormlist("zw.webhook.add asdf1 https://discord.com/api/webhooks/1111223423432/asdflkjsadlfkjadslfjlkfdsa-lkjczlknvznnmvxzc-oireoiwqrwoiuqroiweiuqorq"))
            self.stormIsInPrint("Webhook added for service \"slack\"", await core.stormlist("zw.webhook.add asdf2 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"))
            self.stormIsInPrint("Webhook added for service \"teams\"", await core.stormlist("zw.webhook.add asdf3 https://asdfsafda.webhook.office.com/asdfasdfsafdsa/zxcvxzvxzvcxv/gdgfdsgfdsgfdg"))
            self.stormIsInPrint("Webhook added for service \"keybase\"", await core.stormlist("zw.webhook.add asdf4 https://bots.keybase.io/webhookbot/asdasdasdasda_asdasdasdasda"))

            self.stormIsInPrint("Webhook deleted: asdf1", await core.stormlist("zw.webhook.delete asdf1"))
            
            async with core.getLocalProxy(user="nopriv") as noprivcore:
                self.stormIsInErr("Not allowed to delete", [m async for m in noprivcore.storm("zw.webhook.delete asdf2")])
            
            async with core.getLocalProxy(user="hipriv") as hiprivcore:
                self.stormIsInPrint("Webhook deleted", [m async for m in hiprivcore.storm("zw.webhook.delete asdf2")])