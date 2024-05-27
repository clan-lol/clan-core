# Self Hosting

## General Description

Self-hosting refers to the practice of hosting and maintaining servers, networks, storage, services, and other types of infrastructure by oneself rather than relying on a third-party vendor. This could involve running a server from a home or business location, or leasing a dedicated server at a data center.

There are several reasons for choosing to self-host. These can include:

1. Cost savings: Over time, self-hosting can be more cost-effective, especially for businesses with large scale needs.

1. Control: Self-hosting provides a greater level of control over the infrastructure and services. It allows the owner to customize the system to their specific needs.

1. Privacy and security: Self-hosting can offer improved privacy and security because data remains under the control of the host rather than being stored on third-party servers.

1. Independent: Being independent of third-party services can ensure that one's websites, applications, or services remain up even if the third-party service goes down.

## Stories

### Story 1: Private mumble server hosted at home

Alice wants to self-host a mumble server for her family.

- She visits to the Clan website, and follows the instructions on how to install Clan-OS on her server.
- Alice logs into a terminal on her server via SSH (alternatively uses Clan GUI app)
- Using the Clan CLI or GUI tool, alice creates a new private network for her family (VPN)
- Alice now browses a list of curated Clan modules and finds a module for mumble.
- She adds this module to her network using the Clan tool.
- After that, she uses the clan tool to invite her family members to her network
- Other family members join the private network via the invitation.
- By accepting the invitation, other members automatically install all required software to interact with the network on their machine.

### Story 2: Adding a service to an existing network

Alice wants to add a photos app to her private network

- She uses the clan CLI or GUI tool to manage her existing private Clan family network
- She discovers a module for photoprism, and adds it to her server using the tool
- Other members who are already part of her network, will receive a notification that an update is required to their environment
- After accepting, all new software and services to interact with the new photoprism service will be installed automatically.

## Challenges

...
