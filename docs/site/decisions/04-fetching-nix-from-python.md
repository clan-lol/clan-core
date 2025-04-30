## Status

accepted

## Context

In our clan-cli we need to get a lot of values from nix into the python runtime. This is used to determine the hostname, the target ips address, scripts to generate vars, file locations and many more.

Currently we use two different accessing methods:

### Method 1: deployment.json

A json file that serializes some predefined values into a JSON file as build-time artifact.

Downsides:

* no access to flake level values
* all or nothing:
  * values are either cached via deployment.json or not. So we can only put cheap values into there,
  * in the past var generation script were added here, which added a huge build time overhead for every time we wanted to do any action
* duplicated nix code
  * values need duplicated nix code, once to define them at the correct place in the module system (clan.core.vars.generators) and code to accumulate them again for the deployment.json (system.clan.deployment.data)
  * This duality adds unnecessary dependencies to the nixos module system.

Benefits:

* Utilize `nix build` for caching the file.
* Caching mechanism is very simple.


### Method 2: Direct access:

Directly calling the evaluator / build sandbox via `nix build` and `nix eval`within the Python code


Downsides:

* Access is not cached: Static overhead (see below: \~1.5s) is present every time, if we invoke `nix commands`
  * The static overhead depends obviously which value we need to retrieve, since the `evalModules` overhead depends, whether we evaluate some attribute inside a machine or a flake attribute
  * Accessing more and more attributes with this method increases the static overhead, which leads to a linear decrease in performance.
* Boilerplate for interacting with the CLI and Error handling code is repeated every time.

Benefits:

* Simple and native interaction with the `nix commands`is rather intuitive
* Custom error handling for each attribute is easy

This sytem could be enhanced with custom nix expressions, which could be used in places where we don't want to put values into deployment.json or want to fetch flake level values. This also has some downsides:

* technical debt
  * we have to maintain custom nix expressions inside python code, embedding code is error prone and the language linters won't help you here, so errors are common and harder to debug.
  * we need custom error reporting code in case something goes wrong, either the value doesn't exist or there is an reported build error
* no caching/custom caching logic
  * currently there is no infrastructure to cache those extra values, so we would need to store them somewhere, we could either enhance one of the many classes we have or don't cache them at all
  * even if we implement caching for extra nix expressions, there can be no sharing between extra nix expressions. for example we have 2 nix expressions, one fetches paths and values for all generators and the second one fetches only the values, we still need to execute both of them in both contexts although the second one could be skipped if the first one is already cached

### Method 3: nix select

Move all code that extracts nix values into a common class:

Downsides:
* added complexity for maintaining our own DSL

Benefits:
* we can implement an API (select DSL) to get those values from nix without writing complex nix expressions.
* we can implement caching of those values beyond the runtime of the CLI
* we can use precaching at different endpoints to eliminate most of multiple nix evaluations (except in cases where we have to break the cache or we don't know if we need the value in the value later and getting it is expensive).



## Decision

Use Method 3 (nix select) for extracting values out of nix.

This adds the Flake class in flake.py with a select method, which takes a selector string and returns a python dict.

Example:
```python
from clan_lib.flake import Flake
flake = Flake("github:lassulus/superconfig")
flake.select("nixosConfigurations.*.config.networking.hostName)
```
returns:
```
{
  "ignavia": "ignavia",
  "mors": "mors",
  ...
}
```

## Consequences

* Faster execution due to caching most things beyond a single execution, if no cache break happens execution is basically instant, because we don't need to run nix again.
* Better error reporting, since all nix values go through one chokepoint, we can parse error messages in that chokepoint and report them in a more user friendly way, for example if a value is missing at the expected location inside the module system.
* less embedded nix code inside python code
* more portable CLI, since we need to import less modules into the module system and most things can be extracted by the python code directly
