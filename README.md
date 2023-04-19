# synapse-webhook
[![Tests](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/test.yml) [![Release](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml/badge.svg)](https://github.com/captainGeech42/synapse-webhook/actions/workflows/release.yml) [![GitHub Release](https://img.shields.io/github/release/captainGeech42/synapse-webhook.svg?style=flat)](https://github.com/captainGeech42/synapse-webhook/releases)

Synapse Rapid Power-up foro interacting with third-party services through webhooks 

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

## Administration

This package exposes two permissions:

* `zw.webhook.user`: Intended for general analyst use, allows the invocation of `zw.webhook.lookup`
* `zw.webhook.admin`: Intended for administrative/automation use, allows the invocation of `zw.webhook.import` and changing of global configuration items

This package uses a `meta:source` node with the GUID `a9fc8fc6af73f0bf2dda26961f50cfe6`. All observed nodes are edged with `seen` to the `meta:source`. The created `ps:contact` nodes to track the operators use the type `zw.webhook.operator`.


## Running the test suite

use the lib_stormhttp.py test code to make a fake http server
have a switch to hardcode the webhook type or autodetect. use that to force it to do certain things
might have to do a dmon that consumes from a queue to handle rate limiting?

```
$ pip install -r requirements.txt
$ python -m pytest test_synapse_webhook.py
```