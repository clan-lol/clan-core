package services

#service: services: [string]: {
    // Required meta fields
    meta: {
        name: string,
        icon?: string
        description?: string,
    },
    // Required module specifies the behavior of the service.
    module: string,

    // We moved the machine sepcific config to "machines".
    // It may be moved back depending on what makes more sense in the future.
    // machineConfig: {
    //     [string]: {
    //         roles: string[],
    //         config: {
    //             defaultUser?: string
    //         }
    //     }
    // },

    // Configuration for the service
    config: {
        // Schema depends on the module.
        // It declares the interface how the service can be configured.
        ...
    }
}
