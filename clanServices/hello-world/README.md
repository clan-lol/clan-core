!!! Danger "Experimental"
    This service is for demonstration purpose only and may change in the future.

The Hello-World Clan Service is a minimal example showing how to build and register your own service.

It serves as a reference implementation and is used in clan-core CI tests to ensure compatibility.

## What it demonstrates

- How to define a basic Clan-compatible service.
- How to structure your service for discovery and configuration.
- How Clan services interact with NixOS.

## Testing

This service demonstrates two levels of testing to ensure quality and stability across releases:

1. **Unit & Integration Testing** — via [`nix-unit`](https://github.com/nix-community/nix-unit)
2. **End-to-End Testing** — via **NixOS VM tests**, which we extended to support **container virtualization** for better performance.

We highly advocate following the [Practical Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html):

* Write **unit tests** for core logic and invariants.
* Add **one or two end-to-end (E2E)** tests to confirm your service starts and behaves correctly in a real NixOS environment.

NixOS is **untyped** and frequently changes; tests are the safest way to ensure long-term stability of services.

```
               / \
              /   \
             / E2E \
            /-------\
           /         \
          /Integration\
         /-------------\
        /               \
       /    Unit Tests   \
       -------------------
```

### nix-unit

We highly advocate the usage of

[nix-unit](https://github.com/nix-community/nix-unit)

Example in: tests/eval-tests.nix

If you use flake-parts you can use the [native integration](https://flake.parts/options/nix-unit.html)

If nix-unit succeeds, your NixOS evaluation should be mostly correct.

!!! Tip
    - Ensure most used 'settings' and variants are tested.
    - Think about some important edge-cases your system should handle.

### NixOS VM / Container Test

!!! Warning "Early Vars & clanTest"
    The testing system around vars is experimental

    `clanTest` is still experimental and enables container virtualization by default.
    This is still early and might have some limitations.

Some minimal boilerplate is needed to use `clanTest`

```nix
nixosLib = import (inputs.nixpkgs + "/nixos/lib") { }
nixosLib.runTest (
    { ... }:
    {
        imports = [
            self.modules.nixosTest.clanTest
            # Example in tests/vm/default.nix
            testModule
        ];
        hostPkgs = pkgs;

        # Uncomment if you don't want or cannot use containers
        # test.useContainers = false;
    }
)
```
