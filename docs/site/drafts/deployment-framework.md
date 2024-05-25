---
title: "Git Based Machine Deployment with Clan-Core"
description: ""
authors:
  - Qubasa
date: 2024-05-25
---
## Revolutionizing Server Management

In the world of server management, countless tools claim to offer seamless deployment of multiple machines. Yet, many fall short, leaving server admins and self-hosting enthusiasts grappling with complexity. Enter the Clan-Core Framework—a groundbreaking all in one solution designed to transform decentralized self-hosting into an effortless and scalable endeavor.

### The Power of Clan-Core

Imagine having the power to manage your servers with unparalleled ease, scaling your IT infrastructure like never before. Clan-Core empowers you to do just that. At its core, Clan-Core leverages a single Git repository to define everything about your machines. This central repository utilizes Nix or JSON files to specify configurations, including disk formatting, ensuring a streamlined and unified approach.

### Simplified Deployment Process

With Clan-Core, the cumbersome task of bootstrapping a specific ISO is a thing of the past. All you need is SSH access to your Linux server. Clan-Core allows you to overwrite any existing Linux distribution live over SSH, eliminating time-consuming setup processes. This capability means you can deploy updates or new configurations swiftly and efficiently, maximizing uptime and minimizing hassle.

### Secure and Efficient Secret Management

Security is paramount in server management, and Clan-Core takes it seriously. Passwords and other sensitive information are encrypted within the Git repository, automatically decrypted during deployment. This not only ensures the safety of your secrets but also simplifies their management. Clan-Core supports sharing secrets with other admins, fostering collaboration and maintaining reproducibillity and security without sacrificing convenience.

### Services as Apps

Setting up a service can be quite difficult. Many server adjustments need to be made, from setting up a database to adjusting webserver configurations and generating the correct private keys. However, Clan-Core aims to make setting up a service as easy as installing an application. Through Clan-Core's Module system, everything down to secrets can be automatically set up. This transforms the often daunting task of service setup into a smooth, automated process, making it accessible to all.

### Decentralized Mesh VPN

Building on these features is a self-configuring decentralized mesh VPN that interconnects all your machines into a private darknet. This ensures that sensitive services, which might have too much attack surface to be hosted on the public internet, can still be made available privately without the need to worry about potential system compromise. By creating a secure, private network, Clan-Core offers an additional layer of protection for your most critical services.

### Decentralized Domain Name System

Current DNS implementations are distributed but not truly decentralized. For Clan-Core, we implemented our own truly decentralized DNS module. This module uses simple flooding and caching algorithms to discover available domains inside the darknet. This approach ensures that your internal domain name system is robust, reliable, and independent of external control, enhancing the resilience and security of your infrastructure.


### A New Era of Decentralized Self-Hosting

Clan-Core is more than just a tool; it's a paradigm shift in server management. By consolidating machine definitions, secrets and network configuration, into a single, secure repository, it transforms how you manage and scale your infrastructure. Whether you're a seasoned server admin or a self-hosting enthusiast, Clan-Core offers a powerful, user-friendly solution to take your capabilities to the next level.


### Key Features of Clan-Core:

- **Unified Git Repository**: All machine configurations and secrets stored in a single repository.
- **Live Overwrites**: Deploy configurations over existing Linux distributions via SSH.
- **Automated Service Setup**: Easily set up services with Clan-Core's Module system.
- **Decentralized Mesh VPN**: Securely interconnect all machines into a private darknet.
- **Decentralized DNS**: Robust, independent DNS using flooding and caching algorithms.
- **Automated Secret Management**: Encrypted secrets that are automatically decrypted during deployment.
- **Collaboration Support**: Share secrets securely with other admins.


## Clan-Cores Future

Our vision for Clan-Core extends far beyond being just another deployment tool. Clan-Core is a framework we've developed to achieve something much greater. We want to put the "personal" back into "personal computing." Our goal is for everyday users to fully customize their phones or laptops and create truly private spaces for friends and family.

Our first major step is to develop a Graphical User Interface (GUI) that makes configuring all this possible. Initial tests have shown that AI can be leveraged as an alternative to traditional GUIs. This paves the way for a future where people can simply talk to their computers, and they will configure themselves according to the users' wishes. 

By adopting Clan, you're not just embracing a tool—you're joining a movement towards a more efficient, secure, and scalable approach to server management. Join us and revolutionize your IT infrastructure today.




