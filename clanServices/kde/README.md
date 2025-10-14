This module sets up the [KDE Plasma](https://kde.org) Desktop environment.

!!! Note "Customisation"
    This service intentionally does not provide any settings or customisation
    options, as desktop preferences are highly subjective. Clan currently
    supports only this default desktop configuration. Any additional
    customisation can be done via the `extraModules` option. Furthermore, if you
    want to use a different desktop environment or compositor (e.g. Gnome or
    sway), we encourage you to to build your own
    [Clan Service](https://docs.clan.lol/guides/services/community/) or have a
    look at the [Community Services](https://docs.clan.lol/services/community/).

## Example Usage

```nix
inventory = {
  instances = {
    kde = {

      # Deploy on all machines
      roles.default.tags.all = { };

      # Or individual hosts
      roles.default.machines.laptop = { };
    };
  };
};
```
