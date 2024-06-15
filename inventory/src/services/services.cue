package services

#service: services: [string]: {
    autoIncludeMachines: bool,
    meta: {
        name: string,
    },
    // TODO: this should be the list of avilable modules
    module: string,
    machineConfig: {
        [string]: {
            config: {
                defaultUser?: string
            }
        }
    },
    globalConfig: {
        // Should be one of the avilable users
        defaultUser?: string,
    }
}