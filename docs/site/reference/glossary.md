# :material-api: Glossary

## clan
Collection of machines interconnected in a network.

## clan-app
Graphical interface for managing clans. Simpler to use than the `clan-cli`.

## clan-cli
Command-line tool for managing clans.

## clanModule
Module that enables configuration via the inventory.
Legacy `clanModules` also support configuration outside the inventory.

## clanService
Service defined and managed through a clan configuration.

## clanURL
Flake URL-like syntax used to link to clans.
Required to connect the `url-open` application to the `clan-app`.

## facts *(deprecated)*
System for creating secrets and public files in a declarative way.  
**Note:** Deprecated, use `vars` instead.

## inventory
JSON-like structure used to configure multiple machines.

## machine
A physical computer or virtual machine.

## role
Specific function assigned to a machine within a service.
Allows assignment of sane default configurations in multi-machine services.

## vars
System for creating secrets and public files in a declarative way.
