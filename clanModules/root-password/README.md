---
description = "Automatically generates and configures a password for the root user."
categories = ["System"]
features = ["inventory", "deprecated"]
---

This module is deprecated and will be removed in a future release. It's functionality has been replaced by the user-password service.

After the system was installed/deployed the following command can be used to display the root-password:

```bash
clan vars get [machine_name] root-password/root-password
```

See also: [Vars](../../guides/vars-backend.md)

To regenerate the password run:
```
clan vars generate --regenerate [machine_name] --generator root-password
```
