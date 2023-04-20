# synapse-webhook
[![Tests](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml) [![Release](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml) [![GitHub Release](https://img.shields.io/github/release/captainGeech42/synapse-webhook.svg?style=flat)](https://github.com/captainGeech42/synapse-webhook/releases)

Synapse Rapid Power-up for interacting with third-party services through webhooks 

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
storm> zw.webhook.add --help
```

example: sinkdb import and webhook notify of the new ones

## Administration

This package exposes two permissions:

* `zw.webhook.user`: Allows the use of this package
* `zw.webhook.admin`: Allows deleting anyone's webhooks

## Running the test suite

use the lib_stormhttp.py test code to make a fake http server
have a switch to hardcode the webhook type or autodetect. use that to force it to do certain things

```
$ pip install -r requirements.txt
$ python -m pytest test_synapse_webhook.py
```