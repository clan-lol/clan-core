---
description = "Automatically generates and configures a password for the root user."
categories = ["System"]
features = [ "inventory" ]
---

After the system was installed/deployed the following command can be used to display the root-password:

```bash
clan vars get [machine_name] root-password/root-password
```

See also: [Vars](../../manual/vars-backend.md)

To regenerate the password run:
```
clan vars generate --regenerate [machine_name] --generator root-password
```
