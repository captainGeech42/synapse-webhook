# synapse-webhook
[![Tests](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml) [![Release](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml) [![GitHub Release](https://img.shields.io/github/release/captainGeech42/synapse-webhook.svg)](https://github.com/captainGeech42/synapse-webhook/releases)

Synapse Rapid Power-up for interacting with third-party services through webhooks.

Currently supports Discord, Slack, and Microsoft Teams.

## Install

To install the latest release, run the following Storm command

```
storm> pkg.load --raw https://github.com/captainGeech42/synapse-webhook/releases/latest/download/synapse_webhook.json
```

You can also clone this repo, and install via the telepath API:

```
$ python -m synapse.tools.genpkg --push aha://mycortex synapse-webhook.yaml
```

## Usage

```
storm> help zw.webhook
package: zw-webhook
zw.webhook.add   : Add a new webhook
zw.webhook.delete: Delete a webhook. Requires zw.webhook.admin if the webhook isn't yours.
zw.webhook.list  : List the configured webhooks
zw.webhook.send  : Send a message using the webhook

For detailed help on any command, use <cmd> --help
```

First, add a webhook. Names are unique across the entire cortex.
```
storm> zw.webhook.add myslack https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Webhook added for service "slack": myslack

// You can add --global to make it available for anyone to use
storm> zw.webhook.add --global globalslack https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Webhook added for service "slack": globalslack

// You can override the service detection with --service
storm> zw.webhook.add --service teams notslack https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Webhook added for service "teams": notslack
```

Then, you can send messages to it:
```
storm> zw.webhook.send myslack "hello from synapse!"

// You can pipeline in nodes as well
storm> [inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send myslack `Sus url to investigate! {$node.value()}` | spin
```

![Slack example](/imgs/slack.png)

You can also defang URLs:
```
storm> [inet:url=http://google.com inet:url=http://bing.com] | zw.webhook.send --defang myslack `Sus url to investigate! {$node.value()}` | spin
```

![Slack defanged example](/imgs/slack_defanged.png)

You can list the accessible webhooks (yours + global), or all of them with admin:
```
storm> zw.webhook.list
Webhook: myslack
    Owner: geech
    Service: slack
    Global: False
    URL: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

storm> zw.webhook.list --all
Webhook: myslack
    Owner: geech
    Service: slack
    Global: False
    URL: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

Webhook: secretslack
    Owner: admin123
    Service: slack
    Global: False
    URL: https://hooks.slack.com/services/T11112321213/B98989898989/YYYYYYYYYYYYYYYYYY

```

Finally, you can delete your own webhooks, or with admin privs you can delete anyone's:
```
storm> zw.webhook.delete myslack
Webhook deleted: myslack
```

## Example: New Sinkholes

Leveraging another package I wrote, [synapse-sinkdb](https://github.com/captainGeech42/synapse-sinkdb), you can automatically model new sinkholes and notify a webhook of new entries:

```
// add the webhook
zw.webhook.add sinkdb <webhook url>

// add the cronjob
cron.add --day +7 --name "Model sinkholes and send new ones to a webhook" {
    init { $mint=$lib.cast(time, -7days) }

    // download new sinkholes
    zw.sinkdb.import --asof -7days --yield |

    // filter for only sinkholes that were first created in the last 7 days
    +#rep.sinkdb.sinkhole@=($mint,now) +$((#rep.sinkdb.sinkhole).0 > $mint)
    
    // filter out IP addresses that were modeled from a network range
    -(inet:ipv4 and #rep.sinkdb.type.ipv4_range)
    -(inet:ipv6 and #rep.sinkdb.type.ipv6_range) |
    
    // send the sinkhole to the webhook
    zw.webhook.send sinkdb `New sinkhole observed! {$node.repr()}`
}
```

## Administration

This package exposes two permissions:

* `zw.webhook.user`: Allows the use of this package
* `zw.webhook.admin`: Allows deleting anyone's webhooks and listing all webhooks.

## Running the test suite

```
$ pip install -r requirements.txt
$ python -m pytest test_synapse_webhook.py
```