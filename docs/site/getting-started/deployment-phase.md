## Summary

It is time: We will finally deploy the machines now!


## Virtual Machines

Careful - This command is destructive! It will format your traget device's disk and install NixOS on it!

```shell-session
$ clan machines install [MACHINE] --target-host root@<IP>
```

After the installation completes, your machine will reboot into the newly installed NixOS system.
