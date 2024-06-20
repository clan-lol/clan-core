package schema

#groups: groups: {
    // Machine groups
    machines: {
        // Group name mapped to list[machineName]
        // "group1": ["machine1", "machine2"]
        [string]: [...string]
    }
}

#machine: machines: [string]: {
    name: string,
    description?: string,
    icon?: string
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
    roles: [#role]: [...string],
    machines: {
        [string]: {
            config?: {
                ...
            }
        }
    },

    // Configuration for the service
    config: {
        // Schema depends on the module.
        // It declares the interface how the service can be configured.
        ...
    }
}