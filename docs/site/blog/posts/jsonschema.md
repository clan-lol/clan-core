---
title: "Dev Report: Introducing the NixOS to JSON Schema Converter"
description: "Discover our new library designed to extract JSON schema interfaces from NixOS modules, streamlining frontend development"
authors:
  - DavHau
date: 2024-05-25
slug: jsonschema-converter
---

## Overview

We’ve developed a new library designed to extract interfaces from NixOS modules and convert them into JSON schemas, paving the way for effortless GUI generation. This blog post outlines the motivations behind this development, demonstrates the capabilities of the library, and guides you through leveraging it to create GUIs seamlessly.

## Motivation

In recent months, our team has been exploring various graphical user interfaces (GUIs) to streamline NixOS machine configuration. While our opinionated Clan modules simplify NixOS configurations, there's a need to configure these modules from diverse frontends, such as:

- Command-line interfaces (CLIs)
- Web-based UIs
- Desktop applications
- Mobile applications
- Large Language Models (LLMs)

Given this need, a universal format like JSON is a natural choice. It is already possible as of now, to import json based NixOS configurations, as illustrated below:

`configuration.json`:
```json
{ "networking": { "hostName": "my-machine" } }
```

This configuration can be then imported inside a classic NixOS config:
```nix
{config, lib, pkgs, ...}: {
  imports = [
    (lib.importJSON ./configuration.json)
  ];
}
```

This straightforward approach allows us to build a frontend that generates JSON, enabling the configuration of NixOS machines. But, two critical questions arise:

1. How does the frontend learn about existing configuration options?
2. How can it verify user input without running Nix?

Introducing [JSON schema](https://json-schema.org/), a widely supported standard that defines interfaces in JSON and validates input against them.

Example schema for `networking.hostName`:
```json
{
  "type": "object",
  "properties": {
    "networking": {
      "type": "object",
      "properties": {
        "hostName": {
          "type": "string",
          "pattern": "^$|^[a-z0-9]([a-z0-9_-]{0,61}[a-z0-9])?$"
        }
      }
    }
  }
}
```

## Client-Side Input Validation

Validating input against JSON schemas is both efficient and well-supported across numerous programming languages. Using JSON schema validators, you can accurately check configurations like our `configuration.json`.

Validation example:

```shell
$ nix-shell -p check-jsonschema
$ jsonschema -o pretty ./schema.json -i ./configuration.json
===[SUCCESS]===(./configuration.json)===
```

In case of invalid input, schema validators provide explicit error messages:

```shell
$ echo '{ "networking": { "hostName": "my/machine" } }' > configuration.json
$ jsonschema -o pretty ./schema.json -i ./configuration.json
===[ValidationError]===(./configuration.json)===

'my/machine' does not match '^$|^[a-z0-9]([a-z0-9_-]{0,61}[a-z0-9])?$'

Failed validating 'pattern' in schema['properties']['networking']['properties']['hostName']:
    {'pattern': '^$|^[a-z0-9]([a-z0-9_-]{0,61}[a-z0-9])?$',
     'type': 'string'}

On instance['networking']['hostName']:
    'my/machine'
```

## Automatic GUI Generation

Certain libraries facilitate straightforward GUI generation from JSON schemas. For instance, the [react-jsonschema-form playground](https://rjsf-team.github.io/react-jsonschema-form/) auto-generates a form for any given schema.

## NixOS Module to JSON Schema Converter

To enable the development of responsive frontends, our library allows the extraction of interfaces from NixOS modules to JSON schemas. Open-sourced for community collaboration, this library supports building sophisticated user interfaces for NixOS.

Here’s a preview of our library's functions exposed through the [clan-core](https://git.clan.lol/clan/clan-core) flake:

- `lib.jsonschema.parseModule` - Generates a schema for a NixOS module.
- `lib.jsonschema.parseOption` - Generates a schema for a single NixOS option.
- `lib.jsonschema.parseOptions` - Generates a schema from an attrset of NixOS options.

Example:
`module.nix`:
```nix
{lib, config, pkgs, ...}: {
  # a simple service with two options
  options.services.example-web-service = {
    enable = lib.mkEnableOption "Example web service";
    port = lib.mkOption {
      type = lib.types.int;
      description = "Port used to serve the content";
    };
  };
}
```

Converted, using the `parseModule` function:
```shell
$ cd clan-core
$ nix eval --json --impure --expr \
  '(import ./lib/jsonschema {}).parseModule ./module.nix' | jq | head
{
  "properties": {
    "services": {
      "properties": {
        "example-web-service": {
          "properties": {
            "enable": {
              "default": false,
              "description": "Whether to enable Example web service.",
              "examples": [
...
```

This utility can also generate interfaces for existing NixOS modules or options.

## GUI for NGINX in Under a Minute

Creating a prototype GUI for the NGINX module using our library and [react-jsonschema-form playground](https://rjsf-team.github.io/react-jsonschema-form/) can be done quickly:

1. Export all NGINX options into a JSON schema using a Nix expression:

```nix
# export.nix
let
  pkgs = import <nixpkgs> {};
  clan-core = builtins.getFlake "git+https://git.clan.lol/clan/clan-core";
  options = (pkgs.nixos {}).options.services.nginx;
in
  clan-core.lib.jsonschema.parseOption options
```

2. Write the schema into a file:
```shell
$ nix eval --json -f ./export.nix | jq > nginx.json
```

3. Open the [react-jsonschema-form playground](https://rjsf-team.github.io/react-jsonschema-form/), select `Blank` and paste the `nginx.json` contents.

This provides a quick look at a potential GUI (screenshot is cropped).

![Image title](https://clan.lol/static/blog-post-jsonschema/nginx-gui.jpg)

## Limitations

### Laziness

JSON schema mandates the declaration of all required fields upfront, which might be configured implicitly or remain unused. For instance, `services.nginx.virtualHosts.<name>.sslCertificate` must be specified even if SSL isn’t enabled.

### Limited Types

Certain NixOS module types, like `types.functionTo` and `types.package`, do not map straightforwardly to JSON. For full compatibility, adjustments to NixOS modules might be necessary, such as substituting `listOf package` with `listOf str`.

### Parsing NixOS Modules

Currently, our converter relies on the `options` attribute of evaluated NixOS modules, extracting information from the `type.name` attribute, which is suboptimal. Enhanced introspection capabilities within the NixOS module system would be beneficial.

## Future Prospects

We hope these experiments inspire the community, encourage contributions and further development in this space. Share your ideas and contributions through our issue tracker or matrix channel!

## Links

- [Comments on NixOS Discourse](https://discourse.nixos.org/t/introducing-the-nixos-to-json-schema-converter/45948)
- [Source Code of the JSON Schema Library](https://git.clan.lol/clan/clan-core/src/branch/main/lib/jsonschema)
- [Our Issue Tracker](https://git.clan.lol/clan/clan-core/issues)
- [Our Matrix Channel](https://matrix.to/#/#clan:clan.lol)
- [react-jsonschema-form Playground](https://rjsf-team.github.io/react-jsonschema-form/)
