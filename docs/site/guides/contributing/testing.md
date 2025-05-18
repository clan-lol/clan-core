# Testing your contributions

Each feature added to clan should be tested extensively via automated tests.

This document covers different methods of automated testing, including creating, running and debugging such tests.

In order to test the behavior of clan, different testing frameworks are used depending on the concern:

- NixOS VM tests: for high level integration
- NixOS container tests: for high level integration
- Python tests via pytest: for unit tests and integration tests
- Nix eval tests: for nix functions, libraries, modules, etc.

## NixOS VM Tests

The [NixOS VM Testing Framework](https://nixos.org/manual/nixos/stable/index.html#sec-nixos-tests) is used to create high level integration tests, by running one or more VMs generated from a specified config. Commands can be executed on the booted machine(s) to verify a deployment of a service works as expected. All machines within a test are connected by a virtual network. Internet access is not available.

### When to use VM tests

- testing that a service defined through a clan module works as expected after deployment
- testing clan-cli subcommands which require accessing a remote machine

### When not to use VM tests

NixOS VM Tests are slow and expensive. They should only be used for testing high level integration of components.
VM tests should be avoided wherever it is possible to implement a cheaper unit test instead.

- testing detailed behavior of a certain clan-cli command -> use unit testing via pytest instead
- regression testing -> add a unit test

### Finding examples for VM tests

Existing nixos vm tests in clan-core can be found by using ripgrep:
```shellSession
rg self.clanLib.test.baseTest
```

### Locating definitions of failing VM tests

All nixos vm tests in clan are exported as individual flake outputs under `checks.x86_64-linux.{test-attr-name}`.
If a test fails in CI:

  - look for the job name of the test near the top if the CI Job page, like, for example `gitea:clan/clan-core#checks.x86_64-linux.borgbackup/1242`
  - in this case `checks.x86_64-linux.borgbackup` is the attribute path
  - note the last element of that attribute path, in this case `borgbackup`
  - search for the attribute name inside the `/checks` directory via ripgrep

example: locating the vm test named `borgbackup`:

```shellSession
$ rg "borgbackup =" ./checks
./checks/flake-module.nix
44-            wayland-proxy-virtwl = self.clanLib.test.baseTest ./wayland-proxy-virtwl nixosTestArgs;
```

-> the location of that test is `/checks/flake-module.nix` line `41`.

### Adding vm tests

Create a nixos test module under `/checks/{name}/default.nix` and import it in `/checks/flake-module.nix`.


### Running VM tests

```shellSession
nix build .#checks.x86_64-linux.{test-attr-name}
```
(replace `{test-attr-name}` with the name of the test)

### Debugging VM tests

The following techniques can be used to debug a VM test:

#### Print Statements

Locate the definition (see above) and add print statements, like, for example `print(client.succeed("systemctl --failed"))`, then re-run the test via `nix build` (see above)

#### Interactive Shell

- Execute the vm test outside the nix Sandbox via the following command:
`nix run .#checks.x86_64-linux.{test-attr-name}.driver -- --interactive`
- Then run the commands in the machines manually, like for example:
  ```python3
    start_all()
    machine1.succeed("echo hello")
  ```

#### Breakpoints

To get an interactive shell at a specific line in the VM test script, add a `breakpoint()` call before the line to debug, then run the test outside of the sandbox via:
`nix run .#checks.x86_64-linux.{test-attr-name}.driver`


## NixOS Container Tests

Those are very similar to NixOS VM tests, as in they run virtualized nixos machines, but instead of using VMs, they use containers which are much cheaper to launch.
As of now the container test driver is a downstream development in clan-core.
Basically everything stated under the NixOS VM tests sections applies here, except some limitations.

Limitations:

- Cannot run in interactive mode, however while the container test runs, it logs a nsenter command that can be used to log into each of the container.
- setuid binaries don't work

### Where to find examples for NixOS container tests

Existing nixos container tests in clan-core can be found by using ripgrep:

```shellSession
rg self.clanLib.test.containerTest
```


## Python tests via pytest

Since the clan cli is written in python, the `pytest` framework is used to define unit tests and integration tests via python

Due to superior efficiency,

### When to use python tests

- writing unit tests for python functions and modules, or bugfixes of such
- all integrations tests that do not require building or running a nixos machine
- impure integrations tests that require internet access (very rare, try to avoid)


### When not to use python tests

- integrations tests that require building or running a nixos machine (use NixOS VM or container tests instead)
- testing behavior of a nix function or library (use nix eval tests instead)

### Finding examples of python tests

Existing python tests in clan-core can be found by using ripgrep:
```shellSession
rg "import pytest"
```

### Locating definitions of failing python tests

If any python test fails in the CI pipeline, an error message like this can be found at the end of the log:
```
...
FAILED tests/test_machines_cli.py::test_machine_delete - clan_lib.errors.ClanError: Template 'new-machine' not in 'inputs.clan-core
...
```

In this case the test is defined in the file `/tests/test_machines_cli.py` via the test function `test_machine_delete`.

### Adding python tests

If a specific python module is tested, the test should be located near the tested module in a subdirectory called `./tests`
If the test is not clearly related to a specific module, put it in the top-level `./tests` directory of the tested python package. For `clan-cli` this would be `/pkgs/clan-cli/clan_cli/tests`.
All filenames must be prefixed with `test_` and test functions prefixed with `test_` for pytest to discover them.

### Running python tests

#### Running all python tests

To run all python tests which are executed in the CI pipeline locally, use this `nix build` command

```shellSession
nix build .#checks.x86_64-linux.clan-pytest-{with,without}-core
```

#### Running a specific python test

To run a specific python test outside the nix sandbox

1. Enter the development environment of the python package, by either:
  - Having direnv enabled and entering the directory of the package (eg. `/pkgs/clan-cli`)
  - Or using the command `select-shell {package}` in the top-level dev shell of clan-core, (eg. `switch-shell clan-cli`)
2. Execute the test via pytest using issuing
  `pytest ./path/to/test_file.py:test_function_name -s -n0`

The flags `-sn0` are useful to forwards all stdout/stderr output to the terminal and be able to debug interactively via `breakpoint()`.


### Debugging python tests

To debug a specific python test, find its definition (see above) and make sure to enter the correct dev environment for that python package.

Modify the test and add `breakpoint()` statements to it.

Execute the test using the flags `-sn0` in order to get an interactive shell at the breakpoint:

```shelSession
pytest ./path/to/test_file.py:test_function_name -sn0
```

## Nix Eval Tests

### When to use nix eval tests

Nix eval tests are good for testing any nix logic, including

- nix functions
- nix libraries
- modules for the nixos module system

When not to use

- tests that require building nix derivations (except some very cheap ones)
- tests that require running programs written in other languages
- tests that require building or running nixos machines

### Finding examples of nix eval tests

Existing nix eval tests can be found via this ripgrep command:

```shellSession
rg "nix-unit --eval-store"
```

### Locating definitions of failing nix eval tests

Failing nix eval tests look like this:

```shellSession
    > ✅ test_attrsOf_attrsOf_submodule
    > ✅ test_attrsOf_submodule
    > ❌ test_default
    > /build/nix-8-2/expected.nix --- Nix
    > 1 { foo = { bar = { __prio = 1500; }; } 1 { foo = { bar = { __prio = 1501; }; }
    > . ; }                                   . ; }
    >
    >
    > ✅ test_no_default
    > ✅ test_submodule
    > ✅ test_submoduleWith
    > ✅ test_submodule_with_merging
    >
    > 😢 6/7 successful
    > error: Tests failed
```

To locate the definition, find the flake attribute name of the failing test near the top of the CI Job page, like for example `gitea:clan/clan-core#checks.x86_64-linux.lib-values-eval/1242`.

In this case `lib-values-eval` is the attribute we are looking for.

Find the attribute via ripgrep:

```shellSession
$ rg "lib-values-eval ="
lib/values/flake-module.nix
21:        lib-values-eval = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
grmpf@grmpf-nix ~/p/c/clan-core (test-docs)>
```

In this case the test is defined in the file `lib/values/flake-module.nix` line 21

### Adding nix eval tests

In clan core, the following pattern is usually followed:

- tests are put in a `test.nix` file
- a CI Job is exposed via a `flake-module.nix`
- that `flake-module.nix` is imported via the `flake.nix` at the root of the project

For example see `/lib/values/{test.nix,flake-module.nix}`.

### Running nix eval tests

Since all nix eval tests are exposed via the flake outputs, they can be ran via `nix build`:

```shellSession
nix build .#checks.x86_64-linux.{test-attr-name}
```

For quicker iteration times, instead of `nix build` use the `nix-unit` command available in the dev environment.
Example:

```shellSession
nix-unit --flake .#legacyPackages.x86_64-linux.{test-attr-name}
```

### Debugging nix eval tests

Follow the instructions above to find the definition of the test, then use one of the following techniques:

#### Print debugging

Add `lib.trace` or `lib.traceVal` statements in order to print some variables during evaluation

#### Nix repl

Use `nix repl` to evaluate to inspec the test.

Each test consists opf an `expr` (expression) and an `expected` field. `nix-unit` simply checks if `expr == expected` and prints the diff if that's not the case.

`nix repl` can be used to inspect `expr` manually, or any other variables that you choose to expose.

Example:

```shellSession
$ nix repl
Nix 2.25.5
Type :? for help.
nix-repl> tests = import ./lib/values/test.nix {}

nix-repl> tests
{
  test_attrsOf_attrsOf_submodule = { ... };
  test_attrsOf_submodule = { ... };
  test_default = { ... };
  test_no_default = { ... };
  test_submodule = { ... };
  test_submoduleWith = { ... };
  test_submodule_with_merging = { ... };
}

nix-repl> tests.test_default.expr
{
  foo = { ... };
}
```
