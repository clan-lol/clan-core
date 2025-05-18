---
description = "Automatically generates and configures a password for the specified user account."
categories = ["System"]
features = ["inventory"]
---

If setting the option prompt to true, the user will be prompted to type in their desired password.

!!! Note
    This module will set `mutableUsers` to `false`, meaning you can not manage user passwords through `passwd` anymore.


After the system was installed/deployed the following command can be used to display the user-password:

```bash
clan vars get [machine_name] root-password/root-password
```

See also: [Vars](../../guides/vars-backend.md)

To regenerate the password run:
```
clan vars generate --regenerate [machine_name] --generator user-password
```
