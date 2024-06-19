package machines

#ServiceRole: "server" | "client" | "both"

#machine: machines: [string]: {
    name: string,
    description?: string,
    icon?: string,
    // each machines service
    services?: [string]: {
        // Roles if specificed must contain one or more roles
        // If no roles are specified, the service module defines the default roles.
        roles?: [ ...#ServiceRole ],
        // The service config to use
        // This config is scoped to the service.module, only serializable data (strings,numbers, etc) can be assigned here
        config: {
            ...
        }
    }
}