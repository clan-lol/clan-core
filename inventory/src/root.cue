package inventory

import (
	"clan.lol/inventory/services"
	"clan.lol/inventory/machines"
	"clan.lol/inventory/users"
)

@jsonschema(schema="http://json-schema.org/schema#")
#Root: {
	meta: {
		// A name of the clan (primarily shown by the UI)
		name: string
		// A description of the clan
		description: string
		// The icon path
		icon: string
	}

	// A map of services
	services.#service

	// A map of machines
	machines.#machine

	// A map of users
	users.#user
}
