# Inventory API

*Inventory* is an abstract service layer for consistently configuring distributed services across machine boundaries.

The following is a specification of the inventory in [cuelang](https://cuelang.org/) format.

```cue
package compose

#Root: {
	@jsonschema(schema="http://json-schema.org/draft-07/schema#")
	machines?: [string]: {
		deploy?: {
			// Configuration for the deployment of the machine
			targetHost: null | string
		}
		description: null | string
		icon:        null | string
		name:        string
		system:      null | string
		tags: [...string]
	}
	meta?: {
		description: null | string
		icon:        null | string
		name:        string
	}
	services?: {
		borgbackup?: [string]: {
			// borgbackup-config
			config?: {
				// destinations where the machine should be backuped to
				destinations?: {
					[string]: {
						// the name of the backup job
						name: string

						// the borgbackup repository to backup to
						repo: string
					}
				}
			} | *{
				...
			}
			machines?: [string]: {
				// borgbackup-config
				config?: {
					// destinations where the machine should be backuped to
					destinations?: {
						[string]: {
							// the name of the backup job
							name: string

							// the borgbackup repository to backup to
							repo: string
						}
					}
				} | *{
					...
				}
				imports: [...string]
			}
			meta?: {
				description: null | string
				icon:        null | string
				name:        string
			}
			roles?: {
				client?: {
					// borgbackup-config
					config?: {
						// destinations where the machine should be backuped to
						destinations?: {
							[string]: {
								// the name of the backup job
								name: string

								// the borgbackup repository to backup to
								repo: string
							}
						}
					} | *{
						...
					}
					imports: [...string]
					machines: [...string]
					tags: [...string]
				}
				server?: {
					// borgbackup-config
					config?: {
						// destinations where the machine should be backuped to
						destinations?: {
							[string]: {
								// the name of the backup job
								name: string

								// the borgbackup repository to backup to
								repo: string
							}
						}
					} | *{
						...
					}
					imports: [...string]
					machines: [...string]
					tags: [...string]
				}
			}
		}
		packages?: [string]: {
			// packages-config
			config?: {
				// The packages to install on the machine
				packages: [...string]
			} | *{
				...
			}
			machines?: [string]: {
				// packages-config
				config?: {
					// The packages to install on the machine
					packages: [...string]
				} | *{
					...
				}
				imports: [...string]
			}
			meta?: {
				description: null | string
				icon:        null | string
				name:        string
			}
			roles?: default?: {
				// packages-config
				config?: {
					// The packages to install on the machine
					packages: [...string]
				} | *{
					...
				}
				imports: [...string]
				machines: [...string]
				tags: [...string]
			}
		}
		"single-disk"?: [string]: {
			// single-disk-config
			config?: {
				// The primary disk device to install the system on
				device: null | string
			} | *{
				...
			}
			machines?: [string]: {
				// single-disk-config
				config?: {
					// The primary disk device to install the system on
					device: null | string
				} | *{
					...
				}
				imports: [...string]
			}
			meta?: {
				description: null | string
				icon:        null | string
				name:        string
			}
			roles?: default?: {
				// single-disk-config
				config?: {
					// The primary disk device to install the system on
					device: null | string
				} | *{
					...
				}
				imports: [...string]
				machines: [...string]
				tags: [...string]
			}
		}
	}
}
```
