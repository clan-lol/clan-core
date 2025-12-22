# mesh-controller

Minimal network mesh controller in Rust.

Status: alpha

- only tested on macOS so far

## Features

- Declaratively whitelists members via JSON config file
- Assigns deterministic IPv6 addresses
- Issues signed network configurations
- No HTTP API, no database - just static JSON config

## Building

```bash
mkdir build && cd build
cmake .. -DSOURCE_DIR=/path/to/upstream
make
```

This will:
1. Apply a patch to support the Rust controller
2. Build the Rust controller library
3. Build the C++ shim
4. Build the daemon linked with the Rust controller

## Configuration

Create `controller.json` in the home directory:

```json
{
  "networks": [
    {
      "id": "8e4df28b72000001",
      "members": ["8e4df28b72", "af097db6d4"]
    }
  ]
}
```

The network ID must start with your controller's 10-character address.
Member addresses are 10-character addresses to authorize.

## Testing

```bash
cd build
ctest -V
```

Requires root privileges (needs to create network interfaces).
