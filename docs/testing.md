# Property vs Contract based testing

In this section, we'll explore the importance of testing the backend of your FastAPI application, specifically focusing on the advantages of using contract-based testing with property-based testing frameworks.

## Why Use Property-Based Testing?

Property-based testing is a powerful approach to test your APIs, offering several key benefits:

### 1. Scope

Instead of having to write numerous test cases for various input arguments, property-based testing enables you to test a range of arguments for each parameter using a single test. This approach significantly enhances the robustness of your test suite while reducing redundancy in your testing code. In short, your test code becomes cleaner, more DRY (Don't Repeat Yourself), and more efficient. It also becomes more effective as you can easily test numerous edge cases.

### 2. Reproducibility

Property-based testing tools retain test cases and their results, allowing you to reproduce and replay tests in case of failure. This feature is invaluable for debugging and ensuring the stability of your application over time.

### Frameworks for Property-Based Testing

To implement property-based testing in FastAPI, you can use the following framework:

- [Using Hypothesis with FastAPI](https://testdriven.io/blog/fastapi-hypothesis/)
- [Schemathesis](https://schemathesis.readthedocs.io/en/stable/#id2)
- [Hypothesis: Property-Based Testing](https://hypothesis.readthedocs.io/en/latest/quickstart.html)

### Why Schemas Are Not Contracts

A schema is a description of the data structure of your API, whereas a contract defines not only the structure but also the expected behavior and constraints. The following resource explains why schemas are not contracts in more detail:

- [Why Schemas Are Not Contracts](https://pactflow.io/blog/schemas-are-not-contracts/)

In a nutshell, schemas may define the data structure but often fail to capture complex constraints and the expected interactions between different API endpoints. Contracts fill this gap by specifying both the structure and behavior of your API.

## Why Use Contract-Driven Testing?

Contract-driven testing combines the benefits of type annotations and property-based testing, providing a robust approach to ensuring the correctness of your APIs.

- Contracts become an integral part of the function signature and can be checked statically, ensuring that the API adheres to the defined contract.

- Contracts, like property-based tests, allow you to specify conditions and constraints, with the testing framework automatically generating test cases and verifying call results.

### Frameworks for Contract-Driven Testing

To implement contract-driven testing in FastAPI, consider the following framework and extension:

- [iContract: Contract-Driven Development](https://icontract.readthedocs.io/en/latest/introduction.html)
- [FastAPI-iContract: Extension for FastAPI](https://github.com/mristin/fastapi-icontract)

By adopting contract-driven testing, you can ensure that your FastAPI application not only has a well-defined structure but also behaves correctly, making it more robust and reliable.