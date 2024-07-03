package schema

#machine: machines: [string]: {
    name: string,
    description?: string,
    icon?: string
    tags: [...string]
    system: string
}

#role: string

#service: services: [string]: [string]: {
    // Required meta fields
    meta: {
        name: string,
        icon?: string
        description?: string,
    },
    // We moved the machine sepcific config to "machines".
    // It may be moved back depending on what makes more sense in the future.
    roles: [#role]: {
        machines: [...string],
        tags: [...string],
    }
    machines?: {
        [string]: {
            config?: {
                ...
            }
        }
    },

    // Global Configuration for the service
    config?: {
        // Schema depends on the module.
        // It declares the interface how the service can be configured.
        ...
    }
}