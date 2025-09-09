# Generators

Generators are the core mechanism of the clan vars system for automating the creation and management of generated files, especially secrets, in your NixOS configurations.

## What are Generators?

Generators solve a common problem: instead of manually running commands like `mkpasswd` to create password hashes and copying them into your configuration, generators automate this process declaratively.

A generator defines:

- **Input prompts**: Values to request from users (passwords, names, etc.)
- **Generation script**: Logic to transform inputs into outputs
- **Output files**: Generated files that can be secrets or public data
- **Dependencies**: Other generators this one depends on
- **Runtime inputs**: Tools and packages needed by the script

## Key Benefits

- **Reproducible**: Same inputs produce same outputs across machines
- **Declarative**: Defined in your NixOS configuration alongside usage
- **Secure**: Automatic handling of secrets storage and deployment
- **Collaborative**: Shared generators work across team environments
- **Automated**: No manual copy-paste of generated values

## Common Use Cases

- **Password hashing**: Generate secure password hashes for user accounts
- **SSH keys**: Create and manage SSH host and user keys
- **Certificates**: Generate TLS certificates and certificate authorities
- **API tokens**: Create secure random tokens for services
- **Configuration files**: Generate config files that depend on secrets

## Learning Path

1. **Start here**: [Vars Getting Started Guide](../guides/vars-backend.md) - Hands-on tutorial with practical examples
2. **Understand the architecture**: [Vars Concepts Guide](../guides/vars-concepts.md) - Deep dive into design principles and patterns
3. **Explore complex scenarios**: [Advanced Examples](../guides/vars-advanced-examples.md) - Real-world patterns and best practices
4. **Troubleshoot issues**: [Troubleshooting Guide](../guides/vars-troubleshooting.md) - Common problems and solutions

## API Reference

For complete configuration options and technical details, see:

- [Vars NixOS Module Reference](../reference/clan.core/vars.md) - All configuration options
- [Vars CLI Reference](../reference/cli/vars.md) - Command-line interface