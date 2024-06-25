package inventory

import (
	"clan.lol/inventory/schema"
)

@jsonschema(schema="http://json-schema.org/schema#")
#Root: {
	meta: {
		// A name of the clan (primarily shown by the UI)
		name: string
		// A description of the clan
		description?: string
		// The icon path
		icon?: string
	}

	// // A map of services
	schema.#service

	// // A map of machines
	schema.#machine
}
