# Property vs Contract based testing

In this section, we'll explore the importance of testing the backend of your FastAPI application, specifically focusing on the advantages of using contract-based testing with property-based testing frameworks.

## Why Use Property-Based Testing?

Property-based testing is a powerful approach to test your APIs, offering several key benefits:

### 1. Scope

Instead of having to write numerous test cases for various input arguments, property-based testing enables you to test a range of arguments for each parameter using a single test. This approach significantly enhances the robustness of your test suite while reducing redundancy in your testing code. In short, your test code becomes cleaner, more DRY (Don't Repeat Yourself), and more efficient. It also becomes more effective as you can easily test numerous edge cases.

### 2. Reproducibility

Property-based testing tools retain test cases and their results, allowing you to reproduce and replay tests in case of failure. This feature is invaluable for debugging and ensuring the stability of your application over time.

## Frameworks for Property-Based Testing

To implement property-based testing in FastAPI, you can use the following framework:

- [Hypothesis: Property-Based Testing](https://hypothesis.readthedocs.io/en/latest/quickstart.html)
- [Schemathesis](https://schemathesis.readthedocs.io/en/stable/#id2)

## Example

Running schemathesis fuzzer on GET requests

```bash
nix run .#runSchemaTests
```

If you want to test more request types edit the file [flake-module.nix](../checks/impure/flake-module.nix)

After a run it will upload the results to `schemathesis.io` and give you a link to the report.
The credentials to the account are `Username: schemathesis@qube.email` and `Password:6tv4eP96WXsarF`

## Why Schemas Are Not Contracts

A schema is a description of the data structure of your API, whereas a contract defines not only the structure but also the expected behavior and constraints. The following resource explains why schemas are not contracts in more detail:

- [Why Schemas Are Not Contracts](https://pactflow.io/blog/schemas-are-not-contracts/)

In a nutshell, schemas may define the data structure but often fail to capture complex constraints and the expected interactions between different API endpoints. Contracts fill this gap by specifying both the structure and behavior of your API.

## Why Use Contract-Driven Testing?

Contract-driven testing combines the benefits of type annotations and property-based testing, providing a robust approach to ensuring the correctness of your APIs.

- Contracts become an integral part of the function signature and can be checked statically, ensuring that the API adheres to the defined contract.
- Contracts, like property-based tests, allow you to specify conditions and constraints, with the testing framework automatically generating test cases and verifying call results.

### Frameworks for Contract-Driven Testing

To implement contract-driven testing in FastAPI, consider the following framework and extension:

- [Deal: Contract Driven Development](https://deal.readthedocs.io/)
  By adopting contract-driven testing, you can ensure that your FastAPI application not only has a well-defined structure but also behaves correctly, making it more robust and reliable.
- [Whitepaper: Python by contract](https://users.ece.utexas.edu/~gligoric/papers/ZhangETAL22PythonByContractDataset.pdf) This paper goes more into detail how it works

## Examples

You can annotate functions with `@deal.raises(ClanError)` to say that they can _only_ raise a ClanError Exception.

```python
import deal

@deal.raises(ClanError)
def get_task(uuid: UUID) -> BaseTask:
    global POOL
    return POOL[uuid]
```

To say that it can raise multiple exceptions just add after one another separated with a `,`

```python
import deal

@deal.raises(ClanError, IndexError, ZeroDivisionError)
def get_task(uuid: UUID) -> BaseTask:
    global POOL
    return POOL[uuid]
```

### Adding deal annotated functions to pytest

```python
from clan_cli.task_manager import get_task
import deal

@deal.cases(get_task) # <--- Add function get_task to testing corpus
def test_get_task(case: deal.TestCase) -> None:
    case() # <--- Call testing framework with function
```

### Adding example input for deeper testing

You can combine hypothesis annotations with deal annotations to add example inputs to the function so that the verifier can reach deeper parts of the function.

```python
import deal

@deal.example(lambda: get_task(UUID("5c2061e0-4512-4b30-aa8e-7be4a75b8b45"))) # type: ignore
@deal.example(lambda: get_task(UUID("7c2061e6-4512-4b30-aa8e-7be4a75b8b45"))) # type: ignore
@deal.raises(ClanError)
def get_task(uuid: UUID) -> BaseTask:
    global POOL
    return POOL[uuid]
```

You can also add `pre` and `post` conditions. A `pre` condition must be true before the function is executed. A `post` condition must be true after the function was executed. For more information read the [Writing Contracts Section](https://deal.readthedocs.io/basic/values.html).
Or read the [API doc of Deal](https://deal.readthedocs.io/details/api.html)
