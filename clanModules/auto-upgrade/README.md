---
description = "Set up automatic upgrades"
categories = ["System"]
features = [ "inventory", "deprecated" ]
---

Whether to periodically upgrade NixOS to the latest version. If enabled, a
systemd timer will run `nixos-rebuild switch --upgrade` once a day.
