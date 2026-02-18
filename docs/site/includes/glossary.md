*[vars]: System for declaratively generating and deploying secrets, credentials, and dynamic configuration files.
*[generator]: Declaration defining how to create vars, including prompts, scripts, dependencies, and output files.
*[role]: Function assigned to a machine within a service (e.g., client, server).
*[tag]: Grouping mechanism to assign multiple machines to a role at once.
*[instance]: A specific instantiation of a service in the inventory with assigned roles and machines.
*[Nix]: Purely functional package manager providing reproducible, declarative builds.
*[NixOS]: Linux distribution built on the Nix package manager using a declarative configuration model.
*[flake]: Nix packaging standard providing reproducible builds with locked dependencies.
*[flake.lock]: Lock file pinning exact versions and hashes of all flake inputs for reproducibility.
*[flake-parts]: Framework for modular Nix flake organization using the module system.
*[nixpkgs]: Official Nix package collection providing packages and NixOS modules.
*[disko]: Declarative disk partitioning tool defining disk layouts in Nix.
*[age]: File encryption format used by sops for encrypting secrets.
*[nixos-anywhere]: Tool for remote NixOS installation via SSH kexec-based deployment.
*[kexec]: Technique to boot a new kernel without full reboot; used for remote installation.
*[initrd]: Initial ramdisk loaded during boot before the main root filesystem.
*[buildHost]: Machine that performs Nix evaluation and builds for deployment.
*[targetHost]: Machine where the configuration is deployed and activated.
*[Git]: Distributed version control system for tracking changes in source code.
*[SSH]: Secure Shell; cryptographic protocol for remote access.
*[PKI]: Public Key Infrastructure; system for managing cryptographic keys and certificates.
*[DNS]: Domain Name System; translates domain names to IP addresses.
*[VPN]: Virtual Private Network; encrypted tunnel for secure communication between machines.
*[TLD]: Top-Level Domain; the last segment of a domain name (e.g., .com, .lol).
*[ADR]: Architecture Decision Record; documents a major design decision for the project.
