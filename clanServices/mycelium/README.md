
[Mycelium](https://github.com/threefoldtech/mycelium) is an end-to-end encrypted IPv6 overlay network that spans the globe.

## Features
- Locality-aware routing: finds the shortest path between nodes.
- All traffic is end-to-end encrypted.
- Can route traffic via friend nodes and is location-aware.
- Automatic rerouting if a physical link goes down.
- IPv6 addresses are derived from private keys.
- A simple, reliable message bus is implemented on top of Mycelium.
- Supports multiple transports (QUIC, TCP, …). Hole punching for QUIC is in progress to enable true P2P connectivity behind NATs.
- Designed for planetary-scale scalability; previous overlay networks reached practical limits, and Mycelium focuses on scaling.
- Can run without a TUN device and be used solely as a reliable message bus.

Example configuration below connects all your machines to the Mycelium network:
```nix
mycelium = {
    roles.peer.tags.all = {};
};
```
